"""
Phase 20 API Router: Receiving, Returns, and Credit Recovery.
Endpoints for recording receipts, listing discrepancies,
tracking credit claims, and applying credit notes to invoices.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header,status
from pydantic import BaseModel, Field,StrictInt
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.permissions import require_role
from typing import Literal
from app.persistence.models import UserModel
from app.receiving.engine import ReceivingEngine

receiving_router = APIRouter(prefix="/api/v1/receiving", tags=["Receiving & Returns"])


class RecordReceiptDTO(BaseModel):
    supplier_name: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    ordered_quantity: StrictInt = Field(..., gt=0)
    received_quantity: StrictInt = Field(..., ge=0)
    damaged_quantity: StrictInt = Field(default=0, ge=0)
    unit_price_paisa: StrictInt = Field(default=10000, gt=0)
    purchase_draft_id: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    return_window_days: int = Field(default=7, ge=1)


class ApplyCreditDTO(BaseModel):
    invoice_ref: str = Field(..., min_length=1)

class AcceptCreditDTO(BaseModel):
    confirmed_supplier_accepted:Literal[True]
    source_evidence_id:str=Field(min_length=1)

@receiving_router.post('/credits/{credit_note_id}/accept')
def accept_supplier_credit(credit_note_id:str,req:AcceptCreditDTO,current_user:UserModel=Depends(require_role(['owner','manager'])),db:Session=Depends(get_db)):
    try:return ReceivingEngine(db,current_user.tenant_id).accept_credit(credit_note_id,req.source_evidence_id,current_user.id)
    except ValueError as error:raise HTTPException(422,str(error))


@receiving_router.post("/receipts", status_code=status.HTTP_201_CREATED)
def record_goods_receipt(
    req: RecordReceiptDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias='Idempotency-Key'),
):
    """Records delivery receipt, updates usable stock, and detects discrepancies."""
    if req.damaged_quantity > req.received_quantity:
        raise HTTPException(status_code=422, detail="Damaged quantity cannot exceed received quantity.")
    engine = ReceivingEngine(db, current_user.tenant_id)
    try:result = engine.record_receipt(
        supplier_name=req.supplier_name,
        sku=req.sku,
        ordered_quantity=req.ordered_quantity,
        received_quantity=req.received_quantity,
        damaged_quantity=req.damaged_quantity,
        unit_price_paisa=req.unit_price_paisa,
        purchase_draft_id=req.purchase_draft_id,
        batch_number=req.batch_number,
        expiry_date=req.expiry_date,
        return_window_days=req.return_window_days,
        request_key=request_key,
    )
    except ValueError as error:raise HTTPException(422,str(error))
    return result


@receiving_router.get("/receipts")
def list_goods_receipts(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists goods receipts for the tenant."""
    engine = ReceivingEngine(db, current_user.tenant_id)
    receipts = engine.list_receipts()
    return [
        {
            "id": r.id,
            "supplier_name": r.supplier_name,
            "sku": r.sku,
            "ordered_quantity": r.ordered_quantity,
            "received_quantity": r.received_quantity,
            "damaged_quantity": r.damaged_quantity,
            "shortage_quantity": r.shortage_quantity,
            "batch_number": r.batch_number,
            "expiry_date": r.expiry_date,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in receipts
    ]


@receiving_router.get("/credits")
def list_credit_notes(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists credit notes and return claims."""
    engine = ReceivingEngine(db, current_user.tenant_id)
    notes = engine.list_credit_notes()
    return [
        {
            "id": cn.id,
            "receipt_id": cn.receipt_id,
            "supplier_name": cn.supplier_name,
            "claim_reason": cn.claim_reason,
            "amount_bdt": cn.amount_paisa / 100.0,
            "status": cn.status,
            "applied_invoice_ref": cn.applied_invoice_ref,
            "return_window_deadline": cn.return_window_deadline.isoformat() if cn.return_window_deadline else None,
            "created_at": cn.created_at.isoformat() if cn.created_at else None,
        }
        for cn in notes
    ]


@receiving_router.post("/credits/{credit_note_id}/apply")
def apply_credit_note(
    credit_note_id: str,
    req: ApplyCreditDTO,
    current_user: UserModel = Depends(require_role(['owner','manager','accountant'])),
    db: Session = Depends(get_db),
):
    """Applies credit note to invoice. Strictly rejects duplicate application."""
    engine = ReceivingEngine(db, current_user.tenant_id)
    try:
        result = engine.apply_credit_to_invoice(credit_note_id, req.invoice_ref)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
