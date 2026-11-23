"""
Phase 21 API Router: Demand Memory & Supported Future Impact.
Endpoints for logging unmet customer visits, viewing demand records,
and analyzing availability-aware stockout impact scenarios.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.demand.engine import DemandEngine
from app.persistence.models import UserModel

demand_router = APIRouter(prefix="/api/v1/demand", tags=["Demand Memory"])


class RecordUnmetDemandDTO(BaseModel):
    requested_product: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1)
    reason: str = Field(default="stockout", pattern="^(stockout|not_carried|price_too_high)$")
    customer_name: Optional[str] = None
    sku: Optional[str] = None
    notes: Optional[str] = None


@demand_router.post("/unmet", status_code=status.HTTP_201_CREATED)
def record_unmet_demand(
    req: RecordUnmetDemandDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Records unmet customer demand without mutating ledger revenue."""
    engine = DemandEngine(db, current_user.tenant_id)
    demand = engine.record_unmet_demand(
        requested_product=req.requested_product,
        quantity=req.quantity,
        reason=req.reason,
        customer_name=req.customer_name,
        sku=req.sku,
        notes=req.notes,
    )
    return {
        "id": demand.id,
        "requested_product": demand.requested_product,
        "sku": demand.sku,
        "quantity": demand.quantity,
        "reason": demand.reason,
        "recorded_at": demand.recorded_at.isoformat(),
        "ledger_revenue_impact": 0,
    }


@demand_router.get("/unmet")
def list_unmet_demands(
    sku: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists unmet demand records for the tenant."""
    engine = DemandEngine(db, current_user.tenant_id)
    records = engine.list_unmet_demands(sku=sku)
    return [
        {
            "id": r.id,
            "customer_name": r.customer_name,
            "requested_product": r.requested_product,
            "sku": r.sku,
            "quantity": r.quantity,
            "reason": r.reason,
            "notes": r.notes,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in records
    ]


@demand_router.get("/analysis/{sku}")
def analyze_demand_impact(
    sku: str,
    lead_time_days: int = 3,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Provides honest availability-aware reorder scenarios without fabricated probabilities."""
    engine = DemandEngine(db, current_user.tenant_id)
    return engine.analyze_demand_impact(sku, lead_time_days=lead_time_days)
