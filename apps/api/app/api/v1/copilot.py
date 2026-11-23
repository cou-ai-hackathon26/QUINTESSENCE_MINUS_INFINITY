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

    audio_bytes = await file.read()
    result = engine.process_voice_input(
        session_id=session_id,
        audio_bytes=audio_bytes,
        filename=file.filename or "voice_input.mp3",
        mime_type=file.content_type or "audio/mp3",
        user_id=current_user.id,
    )
    return result
