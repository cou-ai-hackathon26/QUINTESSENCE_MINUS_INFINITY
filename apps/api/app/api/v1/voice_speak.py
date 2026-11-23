"""
Neural Voice Synthesis Streaming API for Bangla MSME voice assistant.
Uses the third-party edge-tts client for Microsoft Edge online speech.
Availability and voice quality depend on that external service.
"""
import hashlib
import re
import asyncio
import os
import time
import tempfile
from threading import BoundedSemaphore
from typing import Literal
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel, Field
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.limits import admit
from app.persistence.models import UserModel
try:
    import edge_tts
except ImportError:
    edge_tts = None

voice_router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

CACHE_DIR = Path(settings.VOICE_CACHE_PATH)
_slots = BoundedSemaphore(2)
PRIVATE_HEADERS = {'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'}

def naturalize_speech_text(text: str) -> str:
    """Naturalizes text for human-like conversational Bengali & English speech."""
    # Strip markdown bold, italics, backticks
    text = re.sub(r'[*_`#~]', '', text)
    # If text contains Latin English characters, convert ৳ to ' Taka '
    if bool(re.search(r'[a-zA-Z]', text)):
        text = re.sub(r'৳\s*([0-9,]+(?:\.[0-9]+)?)', r'\1 Taka', text)
    else:
        # Convert ৳ symbol to spoken word ' টাকা '
        text = re.sub(r'৳\s*([0-9০-৯,]+(?:\.[0-9০-৯]+)?)', r'\1 টাকা', text)
    # Convert vertical bar to bengali full stop
    text = text.replace('|', '।')
    # Clean up double spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

naturalize_bangla_text = naturalize_speech_text

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1500)
    voice: Literal['bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural', 'en-US-GuyNeural', 'en-US-JennyNeural'] = 'bn-BD-PradeepNeural'
    rate: Literal['-10%', '+0%', '+10%'] = '+0%'
    pitch: Literal['+0Hz'] = '+0Hz'

@voice_router.post("/speak")
async def synthesize_speech(payload: SpeakRequest, current_user: UserModel = Depends(get_current_user)):
    admit('voice:' + current_user.tenant_id, 20)
    if edge_tts is None:
        raise HTTPException(503, 'Online speech is unavailable. The written transcript remains available.')
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    spoken_text = naturalize_bangla_text(raw_text)
    
    folder = CACHE_DIR / hashlib.sha256(current_user.tenant_id.encode()).hexdigest()
    folder.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha256(f"{payload.voice}_{payload.rate}_{payload.pitch}_{spoken_text}".encode("utf-8")).hexdigest()
    cache_file = folder / f"{cache_key}.mp3"
    now = time.time()
    files = []
    for entry in CACHE_DIR.glob('*/*.mp3'):
        try:
            stamp = entry.stat().st_mtime
            if now - stamp > settings.VOICE_CACHE_TTL_SECONDS:
                entry.unlink(missing_ok=True)
            else:
                files.append((stamp, entry))
        except FileNotFoundError:
            pass
    for _, entry in sorted(files)[:max(0, len(files) - settings.VOICE_CACHE_MAX_FILES + 1)]:
        entry.unlink(missing_ok=True)
    
    if cache_file.exists():
        try:
            return Response(content=cache_file.read_bytes(), media_type="audio/mpeg", headers={**PRIVATE_HEADERS, 'X-Cache': 'HIT'})
        except FileNotFoundError:
            pass  # Another admitted request may have expired/evicted this cache entry.
    
    if not _slots.acquire(blocking=False):
        raise HTTPException(429, 'Speech is busy. Retry shortly.')
    try:
        communicate = edge_tts.Communicate(spoken_text, payload.voice, rate=payload.rate, pitch=payload.pitch)
        audio_chunks = []
        size = 0
        async with asyncio.timeout(settings.VOICE_TIMEOUT_SECONDS):
            async for chunk in communicate.stream():
                if chunk['type'] == 'audio':
                    size += len(chunk['data'])
                    if size > 2 * 1024 * 1024:
                        raise HTTPException(502, 'Speech response exceeded its size limit.')
                    audio_chunks.append(chunk['data'])
        
        audio_bytes = b"".join(audio_chunks)
        if not audio_bytes:
            raise HTTPException(status_code=502, detail="No audio returned from neural voice provider.")
            
        with tempfile.NamedTemporaryFile(dir=folder, delete=False, suffix='.tmp') as temporary:
            temporary.write(audio_bytes)
            name = temporary.name
        try:
            os.replace(name, cache_file)
        finally:
            Path(name).unlink(missing_ok=True)
        return Response(content=audio_bytes, media_type="audio/mpeg", headers={**PRIVATE_HEADERS, 'X-Cache': 'MISS'})
    except HTTPException:
        raise
    except TimeoutError:
        raise HTTPException(504, 'Speech timed out. The written transcript remains available.')
    except Exception:
        raise HTTPException(502, 'Online speech could not finish. The written transcript remains available.')
    finally:
        _slots.release()

@voice_router.get("/speak")
async def synthesize_speech_get(current_user: UserModel = Depends(get_current_user)):
    raise HTTPException(405, 'Use authenticated POST so private speech text is not placed in a URL.')
