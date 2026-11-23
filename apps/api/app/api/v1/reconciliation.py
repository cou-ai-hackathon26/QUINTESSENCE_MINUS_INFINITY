"""
Supplier Reconciliation Router.
Preserves the 4 golden payable hypotheses (REC 001 - 004),
evaluates evidence claims against confirmed ledger facts,
handles Bangla/Banglish supplier clarification replies,
and generates reviewable draft actions for owner approval.
"""
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.permissions import require_role
from app.domain.money import Money
from app.domain.reconciliation import (
    AllocatedCreditFact,
    DemandFact,
    PaymentFact,
    ReconciliationEngine,
    ReconciliationResult,
    ReturnFact,
)
from app.persistence.models import ActionModel, JournalEntryModel, PostingModel, UserModel

reconciliation_router = APIRouter(prefix="/api/v1/reconciliation", tags=["Reconciliation"])


class FactDTO(BaseModel):
    invoice_id: str
    amount_paisa: int = Field(..., gt=0)
    event_id: Optional[str] = None
    prior_included: Optional[bool] = None


class EvaluateReconciliationRequest(BaseModel):
    case_id: Optional[str] = None
    demand: FactDTO
    eligible_payment: FactDTO
    accepted_return: FactDTO
    payment_included: Optional[bool] = None
    return_included: Optional[bool] = None
    attempt_reuse_event_id: Optional[str] = None
    unavailable_credits: Optional[Dict[str, Dict[str, Any]]] = None


class ClarificationReplyRequest(BaseModel):
    case_id: str
    reply_text: Optional[str] = None
    payment_included: Optional[bool] = None
    return_included: Optional[bool] = None
    demand_amount_paisa: int
    payment_amount_paisa: int
    return_amount_paisa: int
    party_id: Optional[str] = None
    invoice_ref: Optional[str] = None


def parse_clarification_reply(text: str) -> tuple[Optional[bool], Optional[bool]]:
    """
    Parses Bengali or Banglish supplier message to determine
    whether payment and return were included in the supplier demand.
    Checks negative patterns before positive substrings.
    """
    lower = text.lower()
    p_inc: Optional[bool] = None
    r_inc: Optional[bool] = None

    # Payment detection (negative check first)
    if "পেমেন্ট পাই নাই" in text or "টাকা পাই নাই" in text or "payment not received" in lower or "payment excluded" in lower:
        p_inc = False
    elif "পেমেন্ট পাইছি" in text or "পেমেন্ট পেয়েছি" in text or "payment received" in lower or "payment included" in lower or "টাকা পাইছি" in text:
        p_inc = True

    # Return detection (negative check first)
    if "ফেরত বাদ দেই নাই" in text or "বাদ দেয়া হয়নি" in text or "রিটার্ন বিবেচনা করা হয়নি" in text or "return not included" in lower or "ফেরত পাইনি" in text:
        r_inc = False
    elif "ফেরত বাদ" in text or "রিটার্ন বাদ" in text or "return included" in lower or "return deducted" in lower or "মাল বাদ দেওয়া" in text:
        r_inc = True

    return p_inc, r_inc


@reconciliation_router.post("/evaluate")
def evaluate_reconciliation(
    req: EvaluateReconciliationRequest,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Evaluates the 4 canonical payable hypotheses from demand, payment, and return facts.
    """
    case_id = req.case_id or f"REC-{uuid.uuid4().hex[:8]}"

    demand_fact = DemandFact(invoice_id=req.demand.invoice_id, amount=Money(req.demand.amount_paisa))
    payment_fact = PaymentFact(
        event_id=req.eligible_payment.event_id or "EVT-PAY",
        invoice_id=req.eligible_payment.invoice_id,
        amount=Money(req.eligible_payment.amount_paisa),
        prior_included=req.payment_included,
    )
    return_fact = ReturnFact(
        event_id=req.accepted_return.event_id or "EVT-RET",
        invoice_id=req.accepted_return.invoice_id,
        amount=Money(req.accepted_return.amount_paisa),
        prior_included=req.return_included,
    )

    unavailable_credits: Dict[str, AllocatedCreditFact] = {}
    if req.unavailable_credits:
        for ev_id, c_data in req.unavailable_credits.items():
            unavailable_credits[ev_id] = AllocatedCreditFact(
                event_id=ev_id,
                amount=Money(c_data["amount_paisa"]),
                allocated_invoice_id=c_data["allocated_invoice_id"],
                allocated_amount=Money(c_data["allocated_amount_paisa"]),
            )

    result: ReconciliationResult = ReconciliationEngine.evaluate(
        case_id=case_id,
        demand=demand_fact,
        eligible_payment=payment_fact,
        accepted_return=return_fact,
        unavailable_credits=unavailable_credits if unavailable_credits else None,
        payment_included=req.payment_included,
        return_included=req.return_included,
        attempt_reuse_event_id=req.attempt_reuse_event_id,
    )

    d = req.demand.amount_paisa
    p = req.eligible_payment.amount_paisa
    r = req.accepted_return.amount_paisa

    hypotheses = [
        {
            "code": "REC-001",
            "name": "উভয় দাবি অমীমাংসিত / বাদ (Both Excluded)",
            "payment_included": False,
            "return_included": False,
            "resulting_due_paisa": d - p - r,
            "status": "selected" if (req.payment_included is False and req.return_included is False) else "candidate",
            "description": f"পেমেন্ট ও ফেরত উভয়ই বাদ দিলে নিট প্রদেয় {(d - p - r) // 100} টাকা।",
        },
        {
            "code": "REC-002",
            "name": "পেমেন্ট ও ফেরত উভয়ই অন্তর্ভুক্ত (Both Included)",
            "payment_included": True,
            "return_included": True,
            "resulting_due_paisa": d,
            "status": "selected" if (req.payment_included is True and req.return_included is True) else "candidate",
            "description": f"মহাজন দাবি করার আগেই উভয়টি সমন্বয় করেছেন। নিট প্রদেয় {d // 100} টাকা।",
        },
        {
            "code": "REC-003",
            "name": "কেবল পেমেন্ট সমন্বয় (Payment Included, Return Excluded)",
            "payment_included": True,
            "return_included": False,
            "resulting_due_paisa": d - r,
            "status": "selected" if (req.payment_included is True and req.return_included is False) else "candidate",
            "description": f"পেমেন্ট অন্তর্ভুক্ত কিন্তু ফেরত মাল বাদ দিতে হবে। নিট প্রদেয় {(d - r) // 100} টাকা।",
        },
        {
            "code": "REC-004",
            "name": "কেবল ফেরত সমন্বয় (Payment Excluded, Return Included)",
            "payment_included": False,
            "return_included": True,
            "resulting_due_paisa": d - p,
            "status": "selected" if (req.payment_included is False and req.return_included is True) else "candidate",
            "description": f"ফেরত মাল অন্তর্ভুক্ত কিন্তু পেমেন্ট বাদ দিতে হবে। নিট প্রদেয় {(d - p) // 100} টাকা।",
        },
    ]

    return {
        "case_id": result.case_id,
        "expected_state": result.expected_state,
        "missing_fact": result.missing_fact,
        "expected_payables_paisa": result.expected_payables,
        "applied_credits_paisa": result.applied_credits_paisa,
        "hypotheses": hypotheses,
    }


@reconciliation_router.post("/clarify")
def clarify_and_draft_action(
    req: ClarificationReplyRequest,
    current_user: UserModel = Depends(require_role(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    """
    Applies a supplier's clarification reply (either structured flags or parsed text),
    resolves the reconciliation hypothesis, and prepares a draft action for owner review.
    """
    p_inc = req.payment_included
    r_inc = req.return_included

    if req.reply_text and (p_inc is None or r_inc is None):
        parsed_p, parsed_r = parse_clarification_reply(req.reply_text)
        if p_inc is None:
            p_inc = parsed_p
        if r_inc is None:
            r_inc = parsed_r

    demand_fact = DemandFact(invoice_id=req.invoice_ref or "INV", amount=Money(req.demand_amount_paisa))
    payment_fact = PaymentFact(
        event_id="EVT-PAY",
        invoice_id=req.invoice_ref or "INV",
        amount=Money(req.payment_amount_paisa),
        prior_included=p_inc,
    )
    return_fact = ReturnFact(
        event_id="EVT-RET",
        invoice_id=req.invoice_ref or "INV",
        amount=Money(req.return_amount_paisa),
        prior_included=r_inc,
    )

    result = ReconciliationEngine.evaluate(
        case_id=req.case_id,
        demand=demand_fact,
        eligible_payment=payment_fact,
        accepted_return=return_fact,
        payment_included=p_inc,
        return_included=r_inc,
    )

    # Determine resolved payable
    resolved_payable_paisa = result.expected_payables[0] if len(result.expected_payables) == 1 else None

    action_id = None
    if resolved_payable_paisa is not None and result.expected_state == "supported":
        # Create a reviewable draft action for owner approval
        import json
        action = ActionModel(
            tenant_id=current_user.tenant_id,
            action_type="supplier_reconciliation_settlement",
            recipient=req.party_id or req.invoice_ref or "supplier",
            amount_paisa=resolved_payable_paisa,
            payload_json=json.dumps({
                "case_id": req.case_id,
                "invoice_ref": req.invoice_ref,
                "party_id": req.party_id,
                "original_demand_paisa": req.demand_amount_paisa,
                "agreed_payable_paisa": resolved_payable_paisa,
                "payment_included": p_inc,
                "return_included": r_inc,
                "reply_text": req.reply_text,
            }),
            status="pending_approval",
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        action_id = action.id

    return {
        "case_id": req.case_id,
        "payment_included": p_inc,
        "return_included": r_inc,
        "resolved_state": result.expected_state,
        "missing_fact": result.missing_fact,
        "resolved_payable_paisa": resolved_payable_paisa,
        "draft_action_id": action_id,
        "requires_owner_approval": bool(action_id),
    }
