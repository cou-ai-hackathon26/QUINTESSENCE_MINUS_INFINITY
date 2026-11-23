"""
Phase 22: Notifications, Voice Alerts & Actionable Inbox Engine.
Provides deduplicated actionable alert emission, status lifecycle (unread, read, snoozed, resolved),
and daily factual executive briefing with audio-ready scripts.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.domain.ledger import StandardAccount
from app.persistence.models import (
    AccountModel,
    CreditNoteModel,
    GoodsReceiptModel,
    NotificationModel,
    now_utc,
)


class NotificationEngine:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def emit_notification(
        self,
        title: str,
        message: str,
        category: str,
        priority: str = "medium",
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[str] = None,
        dedup_key: Optional[str] = None,
    ) -> NotificationModel:
        """
        Emits an actionable notification.
        If an unresolved notification with the same dedup_key exists,
        updates the message and priority instead of creating duplicate urgency.
        """
        key = dedup_key or f"{category}:{target_entity_type or 'gen'}:{target_entity_id or 'none'}"

        existing = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.tenant_id == self.tenant_id,
                NotificationModel.dedup_key == key,
                NotificationModel.status.in_(["unread", "read", "snoozed"]),
            )
            .first()
        )

        if existing:
            existing.title = title
            existing.message = message
            existing.priority = priority
            existing.status = "unread"
            existing.updated_at = now_utc()
            self.db.commit()
            return existing

        notif = NotificationModel(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            title=title,
            message=message,
            category=category,
            priority=priority,
            status="unread",
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dedup_key=key,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        self.db.add(notif)
        self.db.commit()
        return notif

    def list_notifications(self, status: Optional[str] = None) -> List[NotificationModel]:
        now = datetime.now(timezone.utc)
        q = self.db.query(NotificationModel).filter(NotificationModel.tenant_id == self.tenant_id)

        if status:
            q = q.filter(NotificationModel.status == status)
        else:
            # Exclude snoozed whose snooze deadline is still in the future
            q = q.filter(
                (NotificationModel.status != "resolved")
                & (
                    (NotificationModel.status != "snoozed")
                    | (NotificationModel.snoozed_until <= now)
                    | (NotificationModel.snoozed_until.is_(None))
                )
            )

        return q.order_by(NotificationModel.created_at.desc()).all()

    def mark_as_read(self, notification_id: str) -> NotificationModel:
        notif = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id,
                NotificationModel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if not notif:
            raise ValueError("Notification not found")
        notif.status = "read"
        notif.updated_at = now_utc()
        self.db.commit()
        return notif

    def snooze(self, notification_id: str, hours: int = 4) -> NotificationModel:
        notif = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id,
                NotificationModel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if not notif:
            raise ValueError("Notification not found")
        notif.status = "snoozed"
        notif.snoozed_until = datetime.now(timezone.utc) + timedelta(hours=hours)
        notif.updated_at = now_utc()
        self.db.commit()
        return notif

    def resolve(self, notification_id: str) -> NotificationModel:
        notif = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id,
                NotificationModel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if not notif:
            raise ValueError("Notification not found")
        notif.status = "resolved"
        notif.updated_at = now_utc()
        self.db.commit()
        return notif

    def generate_daily_executive_brief(self) -> Dict[str, Any]:
        """
        Generates daily executive briefing:
        - Factual liquid cash balance
        - High-priority open alerts count
        - Unapplied credit note count
        - Script formatted for voice narration
        """
        cash_acc = (
            self.db.query(AccountModel)
            .filter(
                AccountModel.tenant_id == self.tenant_id,
                AccountModel.code == StandardAccount.CASH.value,
            )
            .first()
        )
        wallet_accounts = self.db.query(AccountModel).filter(AccountModel.tenant_id == self.tenant_id, AccountModel.code.like('asset:wallet:%')).all()
        cash_bdt = ((cash_acc.current_balance_paisa if cash_acc else 0) + sum(a.current_balance_paisa for a in wallet_accounts)) / 100.0

        open_notifs = self.list_notifications()
        high_priority = [n for n in open_notifs if n.priority == "high" and n.status not in ("resolved", "snoozed")]

        unapplied_credits = (
            self.db.query(CreditNoteModel)
            .filter(
                CreditNoteModel.tenant_id == self.tenant_id,
                CreditNoteModel.status != "applied_to_bill",
            )
            .all()
        )
        total_credit_bdt = sum(cn.amount_paisa for cn in unapplied_credits) / 100.0

        voice_script_bn = (
            f"শুভ সকাল। আপনার দোকানে বর্তমানে মোট লিকুইড ক্যাশ রয়েছে ৳{cash_bdt:,.2f}। "
            f"আজকের জন্য {len(high_priority)}টি জরুরী সতর্কতা রয়েছে। "
            f"সরবরাহকারীদের থেকে মোট ৳{total_credit_bdt:,.2f} মূল্যের দাবিযোগ্য ক্রেডিট বাকি রয়েছে।"
        )

        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "liquid_cash_bdt": cash_bdt,
            "open_notifications_count": len(open_notifs),
            "high_priority_count": len(high_priority),
            "unapplied_credit_amount_bdt": total_credit_bdt,
            "voice_script_bn": voice_script_bn,
            "voice_script_en": f"Good morning. Total liquid cash is ৳{cash_bdt:,.2f} with {len(high_priority)} urgent alerts.",
        }
