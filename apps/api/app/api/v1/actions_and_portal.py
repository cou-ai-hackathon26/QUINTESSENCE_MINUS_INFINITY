"""
Phase 08 API Router: Action Center, Scoped Customer Portal, and SSLCOMMERZ Payments.
"""
from datetime import datetime, timedelta, timezone
import json
import secrets
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.sslcommerz import SSLCommerzAdapter
from app.core.auth import get_current_user
from app.core.database import get_db
from app.domain.ledger import StandardAccount
from app.domain.merchant import MerchantService
from app.domain.money import Money
from app.persistence.models import (
    AccountModel,
    ActionModel,
    CustomerPortalTokenModel,
    JournalEntryModel,
    PartyModel,
    PostingModel,
    TenantModel,
    UserModel,
    generate_uuid,
    now_utc,
)

actions_router = APIRouter(prefix="/api/v1", tags=["Actions, Portal & Payments"])


def is_expired(dt: Optional[datetime]) -> bool:
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    target = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return now > target


# --- DTOs ---

class ActionCreateDTO(BaseModel):
    action_type: str = Field(..., pattern="^(supplier_payment|customer_reminder|stock_reorder)$")
    recipient: str = Field(..., min_length=1)
    amount_paisa: Optional[int] = Field(None, ge=0)
    idempotency_key: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    expires_in_hours: int = 24


class PortalGenerateDTO(BaseModel):
    party_id: str
    invoice_number: str
    amount_paisa: int = Field(..., gt=0)
    description: Optional[str] = None
    expires_in_days: int = 7


class DisputeDTO(BaseModel):
    dispute_note: str = Field(..., min_length=3)


# --- 1. Action Center Endpoints ---

@actions_router.get("/actions")
def list_actions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actions = (
        db.query(ActionModel)
        .filter(ActionModel.tenant_id == current_user.tenant_id)
        .order_by(ActionModel.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "action_type": a.action_type,
            "recipient": a.recipient,
            "amount_paisa": a.amount_paisa,
            "status": a.status,
            "idempotency_key": a.idempotency_key,
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "executed_at": a.executed_at.isoformat() if a.executed_at else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in actions
    ]


@actions_router.post("/actions")
def create_action_draft(
    req: ActionCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Idempotency check
    if req.idempotency_key:
        existing = (
            db.query(ActionModel)
            .filter(
                ActionModel.tenant_id == current_user.tenant_id,
                ActionModel.idempotency_key == req.idempotency_key,
            )
            .first()
        )
        if existing:
            return {"status": "existing", "action_id": existing.id, "current_status": existing.status}

    expires_at = now_utc() + timedelta(hours=req.expires_in_hours)
    action = ActionModel(
        tenant_id=current_user.tenant_id,
        action_type=req.action_type,
        recipient=req.recipient,
        amount_paisa=req.amount_paisa,
        status="pending_approval" if req.amount_paisa and req.amount_paisa > 0 else "draft",
        idempotency_key=req.idempotency_key or f"ACT-{generate_uuid()[:8].upper()}",
        payload_json=json.dumps(req.payload) if req.payload else None,
        created_by_user_id=current_user.id,
        expires_at=expires_at,
    )
    db.add(action)
    db.commit()
    return {"status": "created", "action_id": action.id, "action_status": action.status}


@actions_router.post("/actions/{action_id}/approve")
def approve_action(
    action_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    action = (
        db.query(ActionModel)
        .filter(ActionModel.id == action_id, ActionModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

    if action.status not in ["draft", "pending_approval"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot approve action in '{action.status}' state.")

    # Role enforcement: Cashier cannot approve financial disbursements
    if action.amount_paisa and action.amount_paisa > 0 and current_user.role == "cashier":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cashier is not authorized to approve payments.")

    action.status = "approved"
    action.approved_by_user_id = current_user.id
    db.commit()
    return {"status": "approved", "action_id": action.id}


@actions_router.post("/actions/{action_id}/execute")
def execute_action(
    action_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    action = (
        db.query(ActionModel)
        .filter(ActionModel.id == action_id, ActionModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

    if action.status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Action must be approved before execution. Current state: {action.status}")

    # Check expiry
    if is_expired(action.expires_at):
        action.status = "failed"
        action.outcome_json = json.dumps({"error": "Action expired before execution"})
        db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Action has expired.")

    # Execute action
    action.status = "completed"
    action.executed_at = now_utc()
    action.outcome_json = json.dumps({"result": "executed_successfully", "timestamp": now_utc().isoformat()})
    db.commit()
    return {"status": "completed", "action_id": action.id, "executed_at": action.executed_at.isoformat()}


@actions_router.post("/actions/{action_id}/cancel")
def cancel_action(
    action_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    action = (
        db.query(ActionModel)
        .filter(ActionModel.id == action_id, ActionModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

    if action.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel action in '{action.status}' state.")

    action.status = "cancelled"
    db.commit()
    return {"status": "cancelled", "action_id": action.id}


# --- 2. Customer Scoped Portal Endpoints ---

@actions_router.post("/portal/generate-link")
def generate_portal_link(
    req: PortalGenerateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    party = db.query(PartyModel).filter(PartyModel.id == req.party_id, PartyModel.tenant_id == current_user.tenant_id).first()
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer party not found.")

    token = secrets.token_urlsafe(32)
    expires_at = now_utc() + timedelta(days=req.expires_in_days)

    portal_token = CustomerPortalTokenModel(
        token=token,
        tenant_id=current_user.tenant_id,
        party_id=req.party_id,
        invoice_number=req.invoice_number,
        amount_paisa=req.amount_paisa,
        description=req.description,
        expires_at=expires_at,
    )
    db.add(portal_token)
    db.commit()

    return {
        "status": "success",
        "token": token,
        "portal_url": f"/pay/{token}",
        "expires_at": expires_at.isoformat(),
    }


@actions_router.get("/portal/{token}")
def get_portal_view(
    token: str,
    db: Session = Depends(get_db),
):
    """Scoped public invoice view without merchant credentials."""
    pt = db.query(CustomerPortalTokenModel).filter(CustomerPortalTokenModel.token == token).first()
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or unknown invoice link.")

    if pt.is_revoked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invoice link has been revoked by the merchant.")

    if is_expired(pt.expires_at):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This invoice link has expired.")

    tenant = db.query(TenantModel).filter(TenantModel.id == pt.tenant_id).first()
    party = db.query(PartyModel).filter(PartyModel.id == pt.party_id).first()

    return {
        "shop_name": tenant.name if tenant else "দোকান",
        "currency": "BDT",
        "customer_name": party.name if party else "সম্মানিত ক্রেতা",
        "invoice_number": pt.invoice_number,
        "amount_paisa": pt.amount_paisa,
        "description": pt.description,
        "is_paid": pt.is_paid,
        "dispute_note": pt.dispute_note,
        "expires_at": pt.expires_at.isoformat(),
    }


@actions_router.post("/portal/{token}/dispute")
def submit_portal_dispute(
    token: str,
    req: DisputeDTO,
    db: Session = Depends(get_db),
):
    pt = db.query(CustomerPortalTokenModel).filter(CustomerPortalTokenModel.token == token).first()
    if not pt or pt.is_revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invoice link.")

    pt.dispute_note = req.dispute_note
    db.commit()
    return {"status": "success", "message": "Dispute note submitted to merchant."}


# --- 3. SSLCOMMERZ Connector Endpoints ---

@actions_router.post("/portal/{token}/pay")
def initiate_customer_payment(
    token: str,
    db: Session = Depends(get_db),
):
    pt = db.query(CustomerPortalTokenModel).filter(CustomerPortalTokenModel.token == token).first()
    if not pt or pt.is_revoked or pt.is_paid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice is already paid or invalid.")

    party = db.query(PartyModel).filter(PartyModel.id == pt.party_id).first()
    cus_name = party.name if party else "Customer"
    cus_phone = party.phone if party and party.phone else "01700000000"

    adapter = SSLCommerzAdapter()
    tran_id = f"TX-{pt.id[:8].upper()}-{secrets.token_hex(4).upper()}"

    res = adapter.init_payment_session(
        tran_id=tran_id,
        total_amount_paisa=pt.amount_paisa,
        cus_name=cus_name,
        cus_phone=cus_phone,
        success_url="/api/v1/payments/sslcommerz/success",
        fail_url="/api/v1/payments/sslcommerz/fail",
        cancel_url="/api/v1/payments/sslcommerz/cancel",
        ipn_url="/api/v1/payments/sslcommerz/ipn",
    )

    return {
        "status": "initiated",
        "gateway_url": res.gateway_url,
        "tran_id": tran_id,
        "amount_bdt": res.amount_bdt,
    }


@actions_router.post("/payments/sslcommerz/ipn")
async def sslcommerz_ipn(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handles SSLCOMMERZ IPN Webhook and Callback.
    Validates amount, currency, merchant store, and duplicate transaction.
    Atomically records ledger posting and reduces customer due.
    """
    try:
        body = await request.json()
    except Exception:
        body = dict(await request.form())

    tran_id = body.get("tran_id")
    token_str = body.get("token")

    pt = None
    if token_str:
        pt = db.query(CustomerPortalTokenModel).filter(CustomerPortalTokenModel.token == token_str).first()

    if not pt and tran_id:
        # Search by tran_id in actions or existing events
        existing_entry = db.query(JournalEntryModel).filter(JournalEntryModel.event_id == tran_id).first()
        if existing_entry:
            return {"status": "duplicate", "message": "Transaction already verified and posted."}

    expected_paisa = pt.amount_paisa if pt else int(float(body.get("amount", 0)) * 100)

    adapter = SSLCommerzAdapter()
    val_result = adapter.validate_callback(
        callback_data=body,
        expected_amount_paisa=expected_paisa,
        expected_currency="BDT",
    )

    if not val_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSLCOMMERZ Validation Failed: {val_result.error_message}",
        )

    # Idempotency check on journal entry
    existing_entry = db.query(JournalEntryModel).filter(JournalEntryModel.event_id == tran_id).first()
    if existing_entry:
        return {"status": "already_processed", "entry_id": existing_entry.id}

    tenant_id = pt.tenant_id if pt else (db.query(TenantModel).first().id if db.query(TenantModel).first() else "tenant-01")

    # Record balanced journal entry:
    # Debit Pending Gateway Settlement (or Bank), Credit Customer Receivables
    cash_acc = MerchantService.get_or_create_account(db, tenant_id, StandardAccount.PENDING_GATEWAY.value, "Pending Gateway Settlement", "asset")
    rec_acc = MerchantService.get_or_create_account(db, tenant_id, StandardAccount.RECEIVABLES.value, "Customer Dues", "asset")

    entry = JournalEntryModel(
        tenant_id=tenant_id,
        entry_number=f"PAY-{generate_uuid()[:8].upper()}",
        description=f"SSLCOMMERZ Verified Payment: {val_result.val_id}",
        event_id=tran_id,
    )
    db.add(entry)
    db.flush()

    p_gateway = PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="debit", amount_paisa=val_result.amount_paisa)
    p_rec = PostingModel(journal_entry_id=entry.id, account_id=rec_acc.id, direction="credit", amount_paisa=val_result.amount_paisa)
    db.add(p_gateway)
    db.add(p_rec)

    cash_acc.current_balance_paisa += val_result.amount_paisa
    rec_acc.current_balance_paisa -= val_result.amount_paisa

    if pt:
        pt.is_paid = True
        party = db.query(PartyModel).filter(PartyModel.id == pt.party_id, PartyModel.tenant_id == tenant_id).first()
        if party:
            party.current_due_paisa -= val_result.amount_paisa

    db.commit()
    return {"status": "verified_and_posted", "entry_id": entry.id, "tran_id": tran_id}
