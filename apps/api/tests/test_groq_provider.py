"""Explicit offline HTTP test doubles. Genuine calls are checked separately."""
import json
import httpx
import pytest
from app.core.config import settings
from app.groq_provider import GroqProvider,InferenceUnavailable,strict_schema
from app.ai_schemas import CommercialExtraction
from test_workbench_auth import client


def extraction(**overrides):
    return CommercialExtraction(party_name=None,invoice_ref=None,amount_paisa=None,claim_date=None,payment_method=None,extracted_text='Source with no amount',source_quote='no amount',uncertainties=['Amount missing'],line_items=[],operations=[],**overrides)


def response(value):
    return httpx.Response(200,json={'id':'explicit-mock-request','choices':[{'message':{'content':value}}],'usage':{'prompt_tokens':21,'completion_tokens':12}})


def test_no_key_is_unavailable_and_never_returns_canned_source():
    with pytest.raises(InferenceUnavailable,match='not_configured'):
        GroqProvider().generate('system','source',CommercialExtraction)


def test_vision_transport_strict_schema_no_secret_in_url_and_null_stays_unknown(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    def handler(request):
        assert request.headers['authorization']=='Bearer synthetic-test-key'
        assert 'synthetic-test-key' not in str(request.url)
        body=json.loads(request.content)
        assert body['model']==settings.GROQ_VISION_MODEL
        assert body['messages'][1]['content'][1]['image_url']['url']=='data:image/png;base64,YWJj'
        assert body['response_format']['json_schema']['strict'] is True
        return response(extraction().model_dump_json())
    provider=GroqProvider(transport=httpx.MockTransport(handler))
    parsed=provider.generate('system','unknown',CommercialExtraction,images=[{'mime':'image/png','bytes':b'abc'}])
    assert parsed.amount_paisa is None and parsed.party_name is None
    receipt=provider.receipts[0]
    assert receipt.status=='succeeded' and receipt.input_tokens==21
    assert receipt.provider_request_id=='explicit-mock-request'
    assert 'synthetic-test-key' not in repr(receipt.__dict__)


@pytest.mark.parametrize('status',[401,429,500])
def test_failure_is_sanitized_receipted_and_never_extracted(monkeypatch,status):
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    provider=GroqProvider(transport=httpx.MockTransport(lambda request:httpx.Response(status,json={'error':'private provider response synthetic-test-key'})))
    with pytest.raises(InferenceUnavailable) as error:
        provider.generate('system','source',CommercialExtraction)
    assert 'synthetic-test-key' not in str(error.value)
    assert provider.receipts[0].status=='failed'
    assert provider.receipts[0].error_code=='http_'+str(status)


def test_malformed_model_output_is_not_success(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    provider=GroqProvider(transport=httpx.MockTransport(lambda request:response('{"fabricated":true}')))
    with pytest.raises(InferenceUnavailable,match='schema_validation_failed'):
        provider.generate('system','source',CommercialExtraction)
    assert provider.receipts[0].status=='invalid_output'


def test_whisper_uses_actual_multipart_bytes_and_rejects_silence(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    def handler(request):
        assert str(request.url).endswith('/audio/transcriptions')
        assert 'multipart/form-data' in request.headers['content-type']
        assert b'explicit-audio-test-bytes' in request.content
        assert b'whisper-large-v3' in request.content
        return httpx.Response(200,json={'text':'','x_groq':{'id':'mock-audio-request'}})
    provider=GroqProvider(transport=httpx.MockTransport(handler))
    with pytest.raises(InferenceUnavailable,match='no_speech_detected'):
        provider.transcribe(b'explicit-audio-test-bytes','audio/wav')
    assert provider.receipts[0].status=='invalid_output'


def test_strict_output_schema_requires_nullable_properties():
    schema=strict_schema(CommercialExtraction)
    assert set(schema['required'])==set(schema['properties'])
    assert schema['additionalProperties'] is False
    assert 'null' in json.dumps(schema['properties']['amount_paisa'])


def test_money_and_required_review_facts_do_not_depend_on_model_self_rating():
    from pydantic import ValidationError
    from app.ai_schemas import ProposedOperation
    op=ProposedOperation(type='debt_collection',amount_paisa=50000,source_quote='Paid 500',missing_fields=[])
    assert set(op.missing_fields)=={'party','payment account'}
    for amount in ('50000',500.5,True):
        with pytest.raises(ValidationError):
            ProposedOperation(type='cash_sale',amount_paisa=amount,source_quote='Source')


def test_voice_endpoint_rejects_non_audio_before_provider_calls(client,monkeypatch):
    c,_=client
    c.post('/api/v1/auth/judge-session',json={});c.headers['Origin']='http://testserver'
    session=c.post('/api/v1/copilot/sessions',json={}).json()
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    result=c.post('/api/v1/copilot/sessions/'+session['id']+'/voice',files={'file':('source.txt',b'not audio','text/plain')})
    assert result.status_code==415


def test_failed_provider_preserves_private_source_and_does_not_fabricate_claim(client,monkeypatch):
    from app.persistence.models import ProviderReceiptModel,DocumentChunkModel
    c,factory=client
    identity=c.post('/api/v1/auth/judge-session',json={}).json()
    c.headers['Origin']='http://testserver'
    monkeypatch.setattr(settings,'GROQ_API_KEY','synthetic-test-key')
    original=httpx.Client.post
    def post(self,url,*args,**kwargs):
        if str(url).startswith('https://api.groq.com/'):
            return httpx.Response(429,json={'error':'private provider error'})
        return original(self,url,*args,**kwargs)
    monkeypatch.setattr(httpx.Client,'post',post)
    result=c.post('/api/v1/evidence/upload',files={'file':('unseen.txt',b'Exact original source INV-X123','text/plain')})
    assert result.status_code==200
    document=c.get('/api/v1/evidence/'+result.json()['evidence_id']).json()
    assert document['status']=='needs_review' and document['claims'][0]['amount_paisa'] is None
    assert document['extraction_error']=='http_429'
    assert c.get('/api/v1/evidence/'+document['id']+'/content').content==b'Exact original source INV-X123'
    assert document['provider_receipts'][0]['status']=='failed'
    with factory() as db:
        assert db.query(ProviderReceiptModel).filter_by(tenant_id=identity['tenant_id'],entity_id=document['id']).count()==1
        chunk=db.query(DocumentChunkModel).filter_by(tenant_id=identity['tenant_id'],document_id=document['id']).one()
        assert chunk.content=='Exact original source INV-X123'
