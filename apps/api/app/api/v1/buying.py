"""
Phase 19 API Router: Buying Desk.
Endpoints for ingesting supplier offers, comparing landed costs,
evaluating cash constraints, and creating purchase order drafts.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.buying.engine import BuyingDeskEngine
from app.core.auth import get_current_user
from app.core.database import get_db
from app.persistence.models import UserModel

buying_router = APIRouter(prefix="/api/v1/buying", tags=["Buying Desk"])


class IngestOfferDTO(BaseModel):
    supplier_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    base_unit_price_paisa: int = Field(..., gt=0)
    pack_size: int = Field(default=1, gt=0)
    pack_unit: str = Field(default="পিস")
    min_order_quantity: int = Field(default=1, ge=1)
    bonus_condition: Optional[Dict[str, Any]] = None
    cash_discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    credit_period_days: int = Field(default=0, ge=0)
    delivery_fee_paisa: int = Field(default=0, ge=0)
    payment_method_required: str = Field(default="any", pattern="^(cash|credit|any)$")
    source_type: str = Field(default="manual")
    source_doc_id: Optional[str] = None


class CompareOffersDTO(BaseModel):
    target_sku: str = Field(..., min_length=1)
    required_quantity: int = Field(..., gt=0)


class CreateOrderDraftDTO(BaseModel):
    comparison_id: str
    offer_id: str
    quantity: int = Field(..., gt=0)


@buying_router.post("/offers", status_code=status.HTTP_201_CREATED)
def ingest_supplier_offer(
    req: IngestOfferDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ingests a supplier offer and validates bonus condition confidence."""
    engine = BuyingDeskEngine(db, current_user.tenant_id)
    offer = engine.ingest_offer(
        supplier_name=req.supplier_name,
        title=req.title,
        sku=req.sku,
        base_unit_price_paisa=req.base_unit_price_paisa,
        pack_size=req.pack_size,
        pack_unit=req.pack_unit,
        min_order_quantity=req.min_order_quantity,
        bonus_condition=req.bonus_condition,
        cash_discount_percent=req.cash_discount_percent,
        credit_period_days=req.credit_period_days,
        delivery_fee_paisa=req.delivery_fee_paisa,
        payment_method_required=req.payment_method_required,
        source_type=req.source_type,
        source_doc_id=req.source_doc_id,
    )
    return {
        "id": offer.id,
        "supplier_name": offer.supplier_name,
        "title": offer.title,
        "sku": offer.sku,
        "base_unit_price_bdt": offer.base_unit_price_paisa / 100.0,
        "confidence_score": offer.confidence_score,
        "has_critical_blocker": offer.has_critical_blocker,
    }


@buying_router.get("/offers")
def list_supplier_offers(
    sku: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists active supplier offers for the tenant."""
    engine = BuyingDeskEngine(db, current_user.tenant_id)
    offers = engine.list_offers(sku=sku)
    return [
        {
            "id": o.id,
            "supplier_name": o.supplier_name,
            "title": o.title,
            "sku": o.sku,
            "base_unit_price_bdt": o.base_unit_price_paisa / 100.0,
            "pack_size": o.pack_size,
            "min_order_quantity": o.min_order_quantity,
            "bonus_condition": json.loads(o.bonus_condition_json) if o.bonus_condition_json else None,
            "cash_discount_percent": o.cash_discount_percent,
            "credit_period_days": o.credit_period_days,
            "delivery_fee_bdt": o.delivery_fee_paisa / 100.0,
            "payment_method_required": o.payment_method_required,
            "confidence_score": o.confidence_score,
            "has_critical_blocker": o.has_critical_blocker,
        }
        for o in offers
    ]


@buying_router.post("/compare")
def compare_supplier_offers(
    req: CompareOffersDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compares landed unit costs and evaluates cash liquidity constraints."""
    engine = BuyingDeskEngine(db, current_user.tenant_id)
    try:
        result = engine.compare_offers(req.target_sku, req.required_quantity)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@buying_router.post("/orders/draft", status_code=status.HTTP_201_CREATED)
def create_order_draft(
    req: CreateOrderDraftDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a purchase order draft. Requires owner/manager approval before execution."""
    engine = BuyingDeskEngine(db, current_user.tenant_id)
    try:
        action = engine.create_order_draft(
            comparison_id=req.comparison_id,
            offer_id=req.offer_id,
            quantity=req.quantity,
            user_id=current_user.id,
        )
        return {
            "action_id": action.id,
            "action_type": action.action_type,
            "recipient": action.recipient,
            "amount_bdt": action.amount_paisa / 100.0 if action.amount_paisa else 0.0,
            "status": action.status,
            "message": "Purchase order draft created. Explicit owner approval required in Action Center.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
