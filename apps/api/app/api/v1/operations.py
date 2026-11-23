"""Everyday Operations API endpoints for Phase 23."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.core.auth import get_current_user
from app.persistence.models import (
    CustomerReservationModel,
    ReturnableContainerModel,
    ShiftHandoverModel,
    UserModel,
)
from app.operations.engine import EverydayOperationsEngine

operations_router = APIRouter(prefix="/api/v1/operations", tags=["Everyday Operations"])


class ReservationItemIn(BaseModel):
    sku: str
    name: Optional[str] = None
    quantity: int = Field(default=1, gt=0)
    unit_price_paisa: int = Field(default=0, ge=0)


class CreateReservationIn(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[ReservationItemIn]
    deposit_paisa: int = Field(default=0, ge=0)
    expiry_hours: int = Field(default=24, ge=1)


class ContainerMovementIn(BaseModel):
    container_type: str  # crate, bottle, drum
    party_name: str
    count: int = Field(gt=0)
    movement_type: str  # issue or return
    deposit_per_unit_paisa: int = Field(default=0, ge=0)


class ShiftHandoverIn(BaseModel):
    shift_name: str
    opened_by: str
    closed_by: str
    declared_cash_paisa: int
    system_cash_paisa: int
    notes: Optional[str] = None


class SupplierChangeCheckIn(BaseModel):
    supplier_name: str
    target_order_id: str
    sku: str
    original_price_paisa: int
    proposed_price_paisa: int
    quantity: int
    proposed_delay_days: int = 0


@operations_router.post("/reservations", status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: CreateReservationIn,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a customer order reservation without creating a sales ledger entry."""
    tenant_id = current_user.tenant_id
    items = [it.model_dump() for it in payload.items]
    res = EverydayOperationsEngine.create_reservation(
        db=db,
        tenant_id=tenant_id,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        items=items,
        deposit_paisa=payload.deposit_paisa,
        expiry_hours=payload.expiry_hours,
    )
    return {
        "id": res.id,
        "tenant_id": res.tenant_id,
        "customer_name": res.customer_name,
        "customer_phone": res.customer_phone,
        "items": json.loads(res.items_json),
        "status": res.status,
        "total_estimated_paisa": res.total_estimated_paisa,
        "deposit_paisa": res.deposit_paisa,
        "expires_at": res.expires_at.isoformat(),
        "created_at": res.created_at.isoformat(),
    }


@operations_router.get("/reservations")
def list_reservations(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists customer reservations for current tenant."""
    tenant_id = current_user.tenant_id
    # First expire any stale reservations
    EverydayOperationsEngine.expire_stale_reservations(db, tenant_id)

    query = db.query(CustomerReservationModel).filter(
        CustomerReservationModel.tenant_id == tenant_id
    )
    if status_filter:
        query = query.filter(CustomerReservationModel.status == status_filter)

    results = query.order_by(CustomerReservationModel.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "customer_name": r.customer_name,
            "customer_phone": r.customer_phone,
            "items": json.loads(r.items_json),
            "status": r.status,
            "total_estimated_paisa": r.total_estimated_paisa,
            "deposit_paisa": r.deposit_paisa,
            "expires_at": r.expires_at.isoformat(),
            "created_at": r.created_at.isoformat(),
        }
        for r in results
    ]


@operations_router.post("/reservations/{reservation_id}/pick")
def pick_reservation(
    reservation_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates reservation to physically picked status."""
    tenant_id = current_user.tenant_id
    try:
        res = EverydayOperationsEngine.pick_reservation(db, tenant_id, reservation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": res.id,
        "status": res.status,
        "message": "Items physically picked and prepared for customer",
    }


@operations_router.post("/containers/movement", status_code=status.HTTP_200_OK)
def record_container_movement(
    payload: ContainerMovementIn,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Records returnable container issue or return, maintaining deposit tracking."""
    tenant_id = current_user.tenant_id
    try:
        container = EverydayOperationsEngine.record_container_movement(
            db=db,
            tenant_id=tenant_id,
            container_type=payload.container_type,
            party_name=payload.party_name,
            count=payload.count,
            movement_type=payload.movement_type,
            deposit_per_unit_paisa=payload.deposit_per_unit_paisa,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": container.id,
        "container_type": container.container_type,
        "party_name": container.party_name,
        "issued_count": container.issued_count,
        "returned_count": container.returned_count,
        "outstanding_count": container.outstanding_count,
        "deposit_per_unit_paisa": container.deposit_per_unit_paisa,
        "total_deposit_held_paisa": container.total_deposit_held_paisa,
    }


@operations_router.get("/containers")
def list_containers(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists tracked returnable containers and held deposits."""
    tenant_id = current_user.tenant_id
    containers = db.query(ReturnableContainerModel).filter(
        ReturnableContainerModel.tenant_id == tenant_id
    ).order_by(ReturnableContainerModel.outstanding_count.desc()).all()

    return [
        {
            "id": c.id,
            "container_type": c.container_type,
            "party_name": c.party_name,
            "issued_count": c.issued_count,
            "returned_count": c.returned_count,
            "outstanding_count": c.outstanding_count,
            "deposit_per_unit_paisa": c.deposit_per_unit_paisa,
            "total_deposit_held_paisa": c.total_deposit_held_paisa,
        }
        for c in containers
    ]


@operations_router.post("/handovers", status_code=status.HTTP_201_CREATED)
def create_handover(
    payload: ShiftHandoverIn,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Records shift handover with factual non-accusatory variance hypotheses."""
    tenant_id = current_user.tenant_id
    handover = EverydayOperationsEngine.create_shift_handover(
        db=db,
        tenant_id=tenant_id,
        shift_name=payload.shift_name,
        opened_by=payload.opened_by,
        closed_by=payload.closed_by,
        declared_cash_paisa=payload.declared_cash_paisa,
        system_cash_paisa=payload.system_cash_paisa,
        notes=payload.notes,
    )
    return {
        "id": handover.id,
        "shift_name": handover.shift_name,
        "opened_by": handover.opened_by,
        "closed_by": handover.closed_by,
        "declared_cash_paisa": handover.declared_cash_paisa,
        "system_cash_paisa": handover.system_cash_paisa,
        "variance_paisa": handover.variance_paisa,
        "notes": handover.notes,
        "possible_reasons": json.loads(handover.possible_reasons_json) if handover.possible_reasons_json else [],
        "created_at": handover.created_at.isoformat(),
    }


@operations_router.get("/handovers")
def list_handovers(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists recorded shift handovers."""
    tenant_id = current_user.tenant_id
    handovers = db.query(ShiftHandoverModel).filter(
        ShiftHandoverModel.tenant_id == tenant_id
    ).order_by(ShiftHandoverModel.created_at.desc()).all()

    return [
        {
            "id": h.id,
            "shift_name": h.shift_name,
            "opened_by": h.opened_by,
            "closed_by": h.closed_by,
            "declared_cash_paisa": h.declared_cash_paisa,
            "system_cash_paisa": h.system_cash_paisa,
            "variance_paisa": h.variance_paisa,
            "notes": h.notes,
            "possible_reasons": json.loads(h.possible_reasons_json) if h.possible_reasons_json else [],
            "created_at": h.created_at.isoformat(),
        }
        for h in handovers
    ]


@operations_router.post("/supplier-change-check")
def check_supplier_change(
    payload: SupplierChangeCheckIn,
    current_user: UserModel = Depends(get_current_user),
):
    """Evaluates scoped supplier delivery/price change proposal without mutating global state."""
    tenant_id = current_user.tenant_id
    return EverydayOperationsEngine.evaluate_supplier_change_proposal(
        tenant_id=tenant_id,
        supplier_name=payload.supplier_name,
        target_order_id=payload.target_order_id,
        sku=payload.sku,
        original_price_paisa=payload.original_price_paisa,
        proposed_price_paisa=payload.proposed_price_paisa,
        quantity=payload.quantity,
        proposed_delay_days=payload.proposed_delay_days,
    )
