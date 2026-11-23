"""
Phase 18 API Router: Copilot and Compound Voice Transaction Review.
Provides scoped conversations, intent routing, transparent citations,
evidence-support scoring, reviewed action drafts, and voice audio review.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.copilot.engine import CopilotEngine
from app.ingestion.adapters import AIModelAdapter, ProviderUnavailableError, parse_paisa_amount
from app.groq_provider import configured,InferenceUnavailable
from app.copilot.grounded import answer_query
from app.core.config import settings
from starlette.concurrency import run_in_threadpool
from app.api.v1.evidence import upload_evidence
from app.persistence.models import ExtractedClaimModel,now_utc
from app.persistence.models import (
    CopilotMessageModel,
    CopilotSessionModel,
    UserModel,
)

copilot_router = APIRouter(prefix="/api/v1/copilot", tags=["Copilot"])


# --- DTOs ---

class CreateSessionDTO(BaseModel):
    title: Optional[str] = "নতুন ব্যবসায়িক পর্যালোচনা"
    context_entity_type: Optional[str] = None
    context_entity_id: Optional[str] = None


class SendMessageDTO(BaseModel):
    query: str = Field(..., min_length=1)


class MessageResponseDTO(BaseModel):
    id: str
    role: str
    content: str
    intent: Optional[str] = None
    confidence_score: Optional[int] = None
    confidence_band: Optional[str] = None
    readiness: Optional[str] = None
    citations: List[Dict[str, Any]] = []
    action_draft_id: Optional[str] = None
    audio_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class SessionDetailDTO(BaseModel):
    id: str
    title: str
    context_entity_type: Optional[str] = None
    context_entity_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    messages: List[MessageResponseDTO] = []


# --- Endpoints ---

@copilot_router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(
    req: CreateSessionDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a new isolated conversation session for the shop."""
    engine = CopilotEngine(db, current_user.tenant_id)
    session = engine.create_session(
        title=req.title,
        context_entity_type=req.context_entity_type,
        context_entity_id=req.context_entity_id,
    )
    return {
        "id": session.id,
        "title": session.title,
        "context_entity_type": session.context_entity_type,
        "context_entity_id": session.context_entity_id,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


@copilot_router.get("/sessions")
def list_sessions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists recent conversation sessions for the shop."""
    engine = CopilotEngine(db, current_user.tenant_id)
    sessions = engine.list_sessions()
    return [
        {
            "id": s.id,
            "title": s.title,
            "context_entity_type": s.context_entity_type,
            "context_entity_id": s.context_entity_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ]


@copilot_router.get("/sessions/{session_id}", response_model=SessionDetailDTO)
def get_session_detail(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves session details and its full message history."""
    engine = CopilotEngine(db, current_user.tenant_id)
    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    messages = engine.get_messages(session_id)
    return SessionDetailDTO(
        id=session.id,
        title=session.title,
        context_entity_type=session.context_entity_type,
        context_entity_id=session.context_entity_id,
        created_at=session.created_at.isoformat() if session.created_at else None,
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
        messages=[
            MessageResponseDTO(
                id=m.id,
                role=m.role,
                content=m.content,
                intent=m.intent,
                confidence_score=m.confidence_score,
                confidence_band=m.confidence_band,
                readiness=m.readiness,
                citations=json.loads(m.citations_json) if m.citations_json else [],
                action_draft_id=m.action_draft_id,
                audio_metadata=json.loads(m.audio_metadata_json) if m.audio_metadata_json else None,
                created_at=m.created_at.isoformat() if m.created_at else None,
            )
            for m in messages
        ],
    )


@copilot_router.post("/sessions/{session_id}/messages")
def send_copilot_message(
    session_id: str,
    req: SendMessageDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Routes query, executes scoped intent, and returns sourced response with confidence score."""
    engine = CopilotEngine(db, current_user.tenant_id)
    if configured() and settings.AI_PROVIDER=='groq':
        session=engine.get_session(session_id)
        if not session:raise HTTPException(404,'Session not found.')
        try:return answer_query(engine,session,req.query,current_user.id)
        except InferenceUnavailable as error:
            db.commit();raise HTTPException(error.status,str(error))
    if engine.classify_intent(req.query) == "action_draft" and not parse_paisa_amount(req.query):
        raise HTTPException(status_code=422, detail="Provide an explicit positive payment amount before preparing a draft.")
    try:
        result = engine.process_query(
            session_id=session_id,
            query=req.query,
            user_id=current_user.id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@copilot_router.post("/sessions/{session_id}/voice")
async def send_copilot_voice(
    session_id: str,
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Processes real voice audio, transcribes, parses compound events, and prepares reviewable action drafts."""
    engine = CopilotEngine(db, current_user.tenant_id)
    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if not (file.content_type or '').startswith('audio/'):
        raise HTTPException(415,'An audio file is required.')
    if configured() and settings.AI_PROVIDER=='groq':
        result=await run_in_threadpool(upload_evidence,file,current_user,db)
        source_id=result['evidence_id']
        claim=db.query(ExtractedClaimModel).filter_by(tenant_id=current_user.tenant_id,evidence_id=source_id).first()
        payload=json.loads(claim.raw_model_response or '{}') if claim else {}
        extraction=payload.get('extraction')
        if not extraction:raise HTTPException(503,'Audio stored, but transcription or extraction did not finish ('+str(payload.get('extraction_error') or 'unknown')+'). Review source '+source_id+'.')
        transcript=extraction.get('extracted_text','')
        proposed=extraction.get('operations',[])
        ambiguous=bool(extraction.get('uncertainties')) or any(op.get('amount_paisa') is None or op.get('type')=='unknown' or op.get('missing_fields') for op in proposed)
        compound=[{**op,'party':op.get('party_name'),'amount_bdt':op['amount_paisa']/100 if op.get('amount_paisa') is not None else None} for op in proposed]
        metadata={'transcription':transcript,'is_ambiguous':ambiguous,'compound_operations':compound,'proposed_operations':proposed,'missing_facts':extraction.get('uncertainties',[]),'provider_receipts':result['provider_receipts'],'evidence_id':source_id}
        message=CopilotMessageModel(tenant_id=current_user.tenant_id,session_id=session.id,role='assistant',content=transcript,intent='voice_transaction_review',readiness='needs_clarification' if ambiguous else 'ready_for_review',citations_json=json.dumps([{'source_type':'audio_transcript','document_id':source_id,'filename':file.filename}]),audio_metadata_json=json.dumps(metadata,ensure_ascii=False))
        db.add(message);session.updated_at=now_utc();db.commit()
        return {'message_id':message.id,'session_id':session.id,'transcription':transcript,'is_ambiguous':ambiguous,'compound_operations':compound,'provider_receipts':result['provider_receipts'],'content':message.content,'evidence_id':source_id}

    if not AIModelAdapter().is_configured():
        raise HTTPException(status_code=503, detail="Voice transcription provider is not configured. Your recording has not been transcribed.")
    if not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=415, detail="An audio file is required.")
    audio_bytes = await file.read(20 * 1024 * 1024 + 1)
    if not audio_bytes or len(audio_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio must be non-empty and under 20 MB.")
    try:
        result = engine.process_voice_input(
            session_id=session_id,
            audio_bytes=audio_bytes,
            filename=file.filename or "voice_input.webm",
            mime_type=file.content_type,
            user_id=current_user.id,
        )
    except ProviderUnavailableError:
        raise HTTPException(status_code=503, detail="Voice provider is unavailable. Keep your recording and retry.")
    return result
