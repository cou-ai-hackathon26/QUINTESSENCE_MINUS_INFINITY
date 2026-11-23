"""
Neural Voice Synthesis Streaming API for Bangla MSME voice assistant.
Uses Microsoft Azure Neural TTS (via edge-tts) with disk caching for sub-millisecond repeated responses.
Provides 100% human-natural Bangladeshi Bangla audio (bn-BD-PradeepNeural / bn-BD-NabanitaNeural).
"""
import hashlib
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
import edge_tts

voice_router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

CACHE_DIR = Path("tmp/voice_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
    voice: str = Field(default="bn-BD-PradeepNeural")
    rate: str = Field(default="+0%")
    pitch: str = Field(default="+0Hz")

@voice_router.post("/speak")
async def synthesize_speech(payload: SpeakRequest):
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    spoken_text = naturalize_bangla_text(raw_text)
    
    cache_key = hashlib.md5(f"{payload.voice}_{payload.rate}_{payload.pitch}_{spoken_text}".encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.mp3"
    
    if cache_file.exists():
        return Response(content=cache_file.read_bytes(), media_type="audio/mpeg", headers={"X-Cache": "HIT"})
    
    try:
        communicate = edge_tts.Communicate(spoken_text, payload.voice, rate=payload.rate, pitch=payload.pitch)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        
        audio_bytes = b"".join(audio_chunks)
        if not audio_bytes:
            raise HTTPException(status_code=502, detail="No audio returned from neural voice provider.")
            
        cache_file.write_bytes(audio_bytes)
        return Response(content=audio_bytes, media_type="audio/mpeg", headers={"X-Cache": "MISS"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice synthesis error: {str(e)}")

@voice_router.get("/speak")
async def synthesize_speech_get(
    text: str = Query(..., min_length=1, max_length=1500),
    voice: str = Query("bn-BD-PradeepNeural"),
    rate: str = Query("+0%")
):
    return await synthesize_speech(SpeakRequest(text=text, voice=voice, rate=rate))
