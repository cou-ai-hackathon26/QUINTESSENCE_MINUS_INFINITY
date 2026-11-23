"""
Phase 07: Liquidity Outlook & Decision Lab API Router.
Provides 7-day cash flow simulation, intervention testing (expenses, delays, promises),
and versioned scenario persistence without mutating the actual ledger.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.domain.ledger import StandardAccount
from app.domain.money import Money
from app.domain.scenarios import ConditionalPromise, ScenarioEngine
from app.persistence.models import (
    AccountModel,
    ObligationModel,
    ScenarioModel,
    UserModel,
    now_utc,
)

scenarios_router = APIRouter(prefix="/api/v1/scenarios", tags=["Decision Lab & Scenarios"])

DEFAULT_7_DATES = [
    "2026-11-22",
    "2026-11-23",
    "2026-11-24",
    "2026-11-25",
    "2026-11-26",
    "2026-11-27",
    "2026-11-28",
]


# --- DTOs ---

class SimulateRequestDTO(BaseModel):
    case_id: str = "custom-simulation"
    dates: Optional[List[str]] = None
    opening_cash_paisa: int = Field(..., ge=0)
    assumed_daily_receipt_paisa: int = Field(..., ge=0)
    planned_outflows_paisa: List[int]
    reserve_target_paisa: int = Field(..., ge=0)
    extra_expense_day_1_paisa: int = Field(0, ge=0)
    conditional_promise_paisa: int = Field(0, ge=0)
    conditional_promise_date: Optional[str] = None


class SaveScenarioDTO(SimulateRequestDTO):
    name: str = Field(..., min_length=1)


class SimulateResponseDTO(BaseModel):
    case_id: str
    dates: List[str]
    closing_cash_series: List[int]
    first_reserve_breach: Optional[str]
    first_funding_shortfall: Optional[str]


# --- Endpoints ---

@scenarios_router.post("/simulate", response_model=SimulateResponseDTO)
def simulate_scenario(
    req: SimulateRequestDTO,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Executes pure deterministic 7-day scenario simulation.
    Does NOT mutate actual ledger books or obligations.
    """
    dates = req.dates or DEFAULT_7_DATES
    if len(dates) != 7 or len(req.planned_outflows_paisa) != 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scenario simulation requires exactly 7 dates and 7 planned outflow values.",
        )

    cond_promise = None
    if req.conditional_promise_paisa > 0 and req.conditional_promise_date:
        cond_promise = ConditionalPromise(
            date=req.conditional_promise_date,
            amount=Money(req.conditional_promise_paisa),
        )

    eval_result = ScenarioEngine.simulate_7_day(
        case_id=req.case_id,
        dates=dates,
        opening_cash=Money(req.opening_cash_paisa),
        assumed_daily_receipt=Money(req.assumed_daily_receipt_paisa),
        planned_outflows=[Money(p) for p in req.planned_outflows_paisa],
        reserve_target=Money(req.reserve_target_paisa),
        extra_expense_day_1=Money(req.extra_expense_day_1_paisa),
        conditional_promise=cond_promise,
    )

    return SimulateResponseDTO(
        case_id=eval_result.case_id,
        dates=dates,
        closing_cash_series=eval_result.closing_cash_series,
        first_reserve_breach=eval_result.first_reserve_breach,
        first_funding_shortfall=eval_result.first_funding_shortfall,
    )


@scenarios_router.post("/save", response_model=SimulateResponseDTO)
def save_scenario(
    req: SaveScenarioDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simulates and stores a versioned scenario record for the tenant.
    """
    dates = req.dates or DEFAULT_7_DATES
    if len(dates) != 7 or len(req.planned_outflows_paisa) != 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scenario requires exactly 7 dates and 7 planned outflow values.",
        )

    cond_promise = None
    if req.conditional_promise_paisa > 0 and req.conditional_promise_date:
        cond_promise = ConditionalPromise(
            date=req.conditional_promise_date,
            amount=Money(req.conditional_promise_paisa),
        )

    eval_result = ScenarioEngine.simulate_7_day(
        case_id=req.case_id,
        dates=dates,
        opening_cash=Money(req.opening_cash_paisa),
        assumed_daily_receipt=Money(req.assumed_daily_receipt_paisa),
        planned_outflows=[Money(p) for p in req.planned_outflows_paisa],
        reserve_target=Money(req.reserve_target_paisa),
        extra_expense_day_1=Money(req.extra_expense_day_1_paisa),
        conditional_promise=cond_promise,
    )

    record = ScenarioModel(
        tenant_id=current_user.tenant_id,
        name=req.name,
        opening_cash_paisa=req.opening_cash_paisa,
        assumed_daily_receipt_paisa=req.assumed_daily_receipt_paisa,
        planned_outflows_json=json.dumps(req.planned_outflows_paisa),
        reserve_target_paisa=req.reserve_target_paisa,
        extra_expense_paisa=req.extra_expense_day_1_paisa,
        conditional_promise_paisa=req.conditional_promise_paisa,
        conditional_promise_date=req.conditional_promise_date,
        first_reserve_breach_date=eval_result.first_reserve_breach,
        first_funding_shortfall_date=eval_result.first_funding_shortfall,
        closing_series_json=json.dumps(eval_result.closing_cash_series),
    )
    db.add(record)
    db.commit()

    return SimulateResponseDTO(
        case_id=record.id,
        dates=dates,
        closing_cash_series=eval_result.closing_cash_series,
        first_reserve_breach=eval_result.first_reserve_breach,
        first_funding_shortfall=eval_result.first_funding_shortfall,
    )


@scenarios_router.get("")
def list_scenarios(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists saved scenarios for the current tenant."""
    scenarios = (
        db.query(ScenarioModel)
        .filter(ScenarioModel.tenant_id == current_user.tenant_id)
        .order_by(ScenarioModel.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "version": s.version,
            "opening_cash_paisa": s.opening_cash_paisa,
            "assumed_daily_receipt_paisa": s.assumed_daily_receipt_paisa,
            "reserve_target_paisa": s.reserve_target_paisa,
            "extra_expense_paisa": s.extra_expense_paisa,
            "planned_outflows_paisa": json.loads(s.planned_outflows_json),
            "conditional_promise_paisa": s.conditional_promise_paisa,
            "conditional_promise_date": s.conditional_promise_date,
            "closing_cash_series": json.loads(s.closing_series_json),
            "first_reserve_breach_date": s.first_reserve_breach_date,
            "first_funding_shortfall_date": s.first_funding_shortfall_date,
            "created_at": s.created_at.isoformat(),
        }
        for s in scenarios
    ]


@scenarios_router.get("/baseline")
def get_tenant_baseline(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Derives baseline outlook from the tenant's current live cash drawer balance.
    Outflows use golden default (2000, 0, 6000, 0, 4000, 0, 3000 BDT) unless overridden.
    """
    cash_acc = (
        db.query(AccountModel)
        .filter(
            AccountModel.tenant_id == current_user.tenant_id,
            AccountModel.code == StandardAccount.CASH.value,
        )
        .first()
    )
    opening_cash = cash_acc.current_balance_paisa if cash_acc else 0

    # Golden contract baseline parameters
    today = datetime.now(timezone(timedelta(hours=6))).date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]
    golden_outflows_paisa = [0] * 7
    sources = []
    obligations = db.query(ObligationModel).filter(ObligationModel.tenant_id == current_user.tenant_id, ObligationModel.status == 'supported').all()
    for obligation in obligations:
        due = obligation.due_at.date().isoformat()
        if due in dates:
            golden_outflows_paisa[dates.index(due)] += obligation.amount_paisa
            sources.append({'id':obligation.id,'invoice_ref':obligation.invoice_ref,'due_date':due,'amount_paisa':obligation.amount_paisa})
    daily_receipt_paisa = 0  # No future revenue is inferred from missing history.
    reserve_target_paisa = 0  # Owner must choose a reserve target.

    eval_result = ScenarioEngine.simulate_7_day(
        case_id="baseline",
        dates=dates,
        opening_cash=Money(opening_cash),
        assumed_daily_receipt=Money(daily_receipt_paisa),
        planned_outflows=[Money(p) for p in golden_outflows_paisa],
        reserve_target=Money(reserve_target_paisa),
    )

    return {
        "dates": dates,
        "obligation_sources": sources,
        "assumption_status": "owner_input_required; supported obligations only; no invented future revenue",
        "as_of": datetime.now(timezone.utc).isoformat(),
        "opening_cash_paisa": opening_cash,
        "assumed_daily_receipt_paisa": daily_receipt_paisa,
        "planned_outflows_paisa": golden_outflows_paisa,
        "reserve_target_paisa": reserve_target_paisa,
        "closing_cash_series": eval_result.closing_cash_series,
        "first_reserve_breach": eval_result.first_reserve_breach,
        "first_funding_shortfall": eval_result.first_funding_shortfall,
    }
