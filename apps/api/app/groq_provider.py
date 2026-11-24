"""Actual Groq HTTP boundary. No production fixture or local transcript fallback."""
import base64
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from threading import BoundedSemaphore, Lock
from copy import deepcopy
from typing import TypeVar
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings
from app.persistence.models import ProviderReceiptModel

T=TypeVar('T',bound=BaseModel)
_inference_slots = BoundedSemaphore(2)
_key_lock = Lock()
_key_cursor = 0

class InferenceUnavailable(Exception):
    def __init__(self,code='provider_unavailable',status=503):
        self.code=code;self.status=status
        super().__init__('Groq inference could not finish ('+code+'). Your source is retained; retry after checking the provider status.')

def configured():
    return bool(settings.groq_api_keys or settings.GROQ_API_KEY.strip())

def get_current_key(offset: int = 0) -> str:
    global _key_cursor
    keys = settings.groq_api_keys
    if not keys:
        return settings.GROQ_API_KEY.strip()
    with _key_lock:
        return keys[(_key_cursor + offset) % len(keys)]

def rotate_key():
    global _key_cursor
    keys = settings.groq_api_keys
    if keys:
        with _key_lock:
            _key_cursor = (_key_cursor + 1) % len(keys)

def strict_schema(model):
    schema=deepcopy(model.model_json_schema())
    def visit(value):
        if isinstance(value,dict):
            value.pop('default',None)
            if value.get('type')=='object':
                value['additionalProperties']=False
                value['required']=list(value.get('properties',{}))
            for child in value.values():visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    visit(schema);return schema

def receipt_dict(receipt):
    return {key:getattr(receipt,key) for key in ['id','provider','model','capability','status','provider_request_id','input_tokens','output_tokens','latency_ms','error_code']}

class GroqProvider:
    def __init__(self,db=None,tenant_id=None,entity_type=None,entity_id=None,transport=None):
        self.db=db;self.tenant_id=tenant_id;self.entity_type=entity_type;self.entity_id=entity_id;self.transport=transport;self.receipts=[]

    def _call(self,endpoint,model,capability,payload=None,files=None,data=None):
        if not configured():raise InferenceUnavailable('not_configured')
        if self.db and self.tenant_id:
            from app.core.limits import admit
            admit('inference:' + self.tenant_id, 40)
            start = datetime.now(timezone.utc) - timedelta(days=1)
            recent = self.db.query(ProviderReceiptModel).filter(ProviderReceiptModel.created_at >= start)
            if recent.count() >= settings.AI_GLOBAL_DAILY_CALLS or recent.filter(ProviderReceiptModel.tenant_id == self.tenant_id).count() >= settings.AI_TENANT_DAILY_CALLS:
                raise InferenceUnavailable('daily_call_limit', 429)
        if not _inference_slots.acquire(blocking=False):
            raise InferenceUnavailable('inference_busy', 429)
        started=time.monotonic();status='failed';body={};error=None
        fingerprint_input={'payload':payload or data,'files':{name:hashlib.sha256(value[1]).hexdigest() for name,value in (files or {}).items()}}
        fingerprint=hashlib.sha256(json.dumps(fingerprint_input,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        keys_pool = settings.groq_api_keys or [settings.GROQ_API_KEY.strip()]
        max_attempts = max(3, len(keys_pool) * 2)
        try:
            for attempt in range(max_attempts):
                current_key = get_current_key(attempt)
                with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS, transport=self.transport) as client:
                    response = client.post(
                        'https://api.groq.com/openai/v1/' + endpoint,
                        headers={'Authorization': 'Bearer ' + current_key},
                        json=payload,
                        files=files,
                        data=data,
                    )
                    if response.status_code == 429 and attempt < max_attempts - 1:
                        rotate_key()
                        header_val = response.headers.get('retry-after') or response.headers.get('x-ratelimit-reset-tokens') or '3'
                        try:
                            retry_after = float(str(header_val).rstrip('s'))
                        except ValueError:
                            retry_after = 3.0
                        if len(keys_pool) > 1:
                            time.sleep(0.5)
                        else:
                            time.sleep(min(max(retry_after, 3.0), 20.0))
                        continue
                    if not response.is_success:
                        error = 'http_' + str(response.status_code)
                        raise InferenceUnavailable(error, 429 if response.status_code == 429 else 503)
                    body = response.json()
                    status = 'succeeded'
                    return body
        except InferenceUnavailable:raise
        except (httpx.HTTPError,ValueError):
            error='connection_or_response_error';raise InferenceUnavailable(error)
        finally:
            _inference_slots.release()
            receipt=ProviderReceiptModel(tenant_id=self.tenant_id,entity_type=self.entity_type,entity_id=self.entity_id,capability=capability,provider='groq',model=model,status=status,request_fingerprint=fingerprint,provider_request_id=body.get('id') or body.get('x_groq',{}).get('id'),input_tokens=body.get('usage',{}).get('prompt_tokens'),output_tokens=body.get('usage',{}).get('completion_tokens'),latency_ms=int((time.monotonic()-started)*1000),error_code=error)
            if self.db and self.tenant_id:self.db.add(receipt);self.db.flush()
            self.receipts.append(receipt)

    def generate(self,system,prompt,output:type[T],images=None,capability='text_reasoning')->T:
        model=settings.GROQ_VISION_MODEL if images else settings.GROQ_TEXT_MODEL
        content=[{'type':'text','text':prompt}]
        for image in images or []:
            content.append({'type':'image_url','image_url':{'url':'data:'+image['mime']+';base64,'+base64.b64encode(image['bytes']).decode()}})
        payload={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':content if images else prompt}],'response_format':{'type':'json_schema','json_schema':{'name':output.__name__,'strict':True,'schema':strict_schema(output)}},'max_completion_tokens':settings.AI_MAX_OUTPUT_TOKENS,'temperature':0.1,'reasoning_effort':'low'}
        body=self._call('chat/completions',model,capability,payload=payload)
        try:
            raw=body['choices'][0]['message']['content'];return output.model_validate_json(raw)
        except (KeyError,IndexError,TypeError,ValidationError,ValueError):
            if self.receipts:self.receipts[-1].status='invalid_output';self.receipts[-1].error_code='schema_validation_failed'
            raise InferenceUnavailable('schema_validation_failed')

    def transcribe(self,audio,mime,filename='recording.webm'):
        body=self._call('audio/transcriptions',settings.GROQ_WHISPER_MODEL,'audio_transcription',files={'file':(filename,audio,mime)},data={'model':settings.GROQ_WHISPER_MODEL,'response_format':'verbose_json','temperature':'0'})
        text=body.get('text','').strip()
        if not text:
            self.receipts[-1].status='invalid_output';self.receipts[-1].error_code='no_speech_detected'
            raise InferenceUnavailable('no_speech_detected',422)
        return text
