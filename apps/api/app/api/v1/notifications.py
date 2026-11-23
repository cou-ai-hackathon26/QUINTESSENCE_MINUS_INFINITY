"""
Phase 22 API Router: Notifications, Voice Alerts & Actionable Inbox.
Endpoints for emitting alerts, managing read/snooze/resolve states,
and retrieving the daily executive voice briefing.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.notifications.engine import NotificationEngine
from app.persistence.models import UserModel

notifications_router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications & Inbox"])


class EmitNotificationDTO(BaseModel):
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(unresolved_receipt|unapplied_credit|return_deadline|cash_constraint|approval_required)$")
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    dedup_key: Optional[str] = None


class SnoozeDTO(BaseModel):
    hours: int = Field(default=4, ge=1, le=72)


@notifications_router.post("/emit", status_code=status.HTTP_201_CREATED)
def emit_notification(
    req: EmitNotificationDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Emits an alert with idempotency via dedup_key."""
    engine = NotificationEngine(db, current_user.tenant_id)
    notif = engine.emit_notification(
        title=req.title,
        message=req.message,
        category=req.category,
        priority=req.priority,
        target_entity_type=req.target_entity_type,
        target_entity_id=req.target_entity_id,
        dedup_key=req.dedup_key,
    )
    return {
        "id": notif.id,
        "title": notif.title,
        "priority": notif.priority,
        "status": notif.status,
        "dedup_key": notif.dedup_key,
    }


@notifications_router.get("")
def list_notifications(
    status: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists inbox alerts for the tenant."""
    engine = NotificationEngine(db, current_user.tenant_id)
    items = engine.list_notifications(status=status)
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "priority": n.priority,
            "status": n.status,
            "target_entity_type": n.target_entity_type,
            "target_entity_id": n.target_entity_id,
            "created_at": n.created_at.isoformat(),
        }
        for n in items
    ]


@notifications_router.post("/{notification_id}/read")
def mark_read(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = NotificationEngine(db, current_user.tenant_id)
    try:
        n = engine.mark_as_read(notification_id)
        return {"id": n.id, "status": n.status}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@notifications_router.post("/{notification_id}/snooze")
def snooze_notification(
    notification_id: str,
    req: SnoozeDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = NotificationEngine(db, current_user.tenant_id)
    try:
        n = engine.snooze(notification_id, hours=req.hours)
        return {"id": n.id, "status": n.status, "snoozed_until": n.snoozed_until.isoformat() if n.snoozed_until else None}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@notifications_router.post("/{notification_id}/resolve")
def resolve_notification(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = NotificationEngine(db, current_user.tenant_id)
    try:
        n = engine.resolve(notification_id)
        return {"id": n.id, "status": n.status}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@notifications_router.get("/brief")
def get_daily_brief(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves factual daily executive summary with voice narration script."""
    engine = NotificationEngine(db, current_user.tenant_id)
    return engine.generate_daily_executive_brief()
