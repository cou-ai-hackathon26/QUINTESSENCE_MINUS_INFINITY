"""
Supplier Statement & Demand Reconciliation Domain Engine.
Preserves the canonical 4 hypotheses for supplier demands,
distinguishes fact applicability from prior deduction,
excludes credits already allocated to other invoices,
and flags missing facts without hallucinating closure.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from app.domain.money import Money


@dataclass(frozen=True)
class DemandFact:
    invoice_id: str
    amount: Money


@dataclass(frozen=True)
class PaymentFact:
    event_id: str
    invoice_id: str
    amount: Money
    prior_included: Optional[bool] = None


@dataclass(frozen=True)
class ReturnFact:
    event_id: str
    invoice_id: str
    amount: Money
    prior_included: Optional[bool] = None


@dataclass(frozen=True)
class AllocatedCreditFact:
    event_id: str
    amount: Money
    allocated_invoice_id: str
    allocated_amount: Money


@dataclass
class ReconciliationResult:
    case_id: str
    expected_payables: List[int]  # in paisa
    expected_state: str  # "supported" | "unresolved"
    missing_fact: Optional[str] = None
    applied_credits_paisa: int = 0


class ReconciliationEngine:
    """Pure deterministic supplier statement reconciliation."""

    @staticmethod
    def evaluate(
        case_id: str,
        demand: DemandFact,
        eligible_payment: PaymentFact,
        accepted_return: ReturnFact,
        unavailable_credits: Optional[Dict[str, AllocatedCreditFact]] = None,
        payment_included: Optional[bool] = None,
        return_included: Optional[bool] = None,
        attempt_reuse_event_id: Optional[str] = None,
    ) -> ReconciliationResult:
        # Check credit reuse exclusion:
        applied_credit_paisa = 0
        if attempt_reuse_event_id:
            if unavailable_credits and attempt_reuse_event_id in unavailable_credits:
                # Credit is already locked/allocated to another invoice (e.g. invoice 38)
                applied_credit_paisa = 0

        d = demand.amount.paisa
        p = eligible_payment.amount.paisa
        r = accepted_return.amount.paisa

        # The 4 canonical hypotheses:
        # H1: payment_included=True,  return_included=True  => payable = d
        # H2: payment_included=True,  return_included=False => payable = d - r
        # H3: payment_included=False, return_included=True  => payable = d - p
        # H4: payment_included=False, return_included=False => payable = d - p - r

        h1 = d
        h2 = d - r
        h3 = d - p
        h4 = d - p - r

        if payment_included is None and return_included is None:
            # All 4 possibilities exist
            payables = sorted([h4, h3, h2, h1])
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=payables,
                expected_state="unresolved",
                missing_fact="whether previous payments and returns are included in demand",
            )

        if payment_included is True and return_included is True:
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=[h1],
                expected_state="supported",
            )

        if payment_included is True and return_included is False:
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=[h2],
                expected_state="supported",
            )

        if payment_included is False and return_included is True:
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=[h3],
                expected_state="supported",
            )

        if payment_included is False and return_included is False:
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=[h4],
                expected_state="supported",
                applied_credits_paisa=applied_credit_paisa,
            )

        if payment_included is None and return_included is False:
            # Payment inclusion is unresolved; return is definitely excluded
            # Possibilities are H4 (payment excluded) or H2 (payment included)
            payables = sorted([h4, h2])
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=payables,
                expected_state="unresolved",
                missing_fact=f"whether {eligible_payment.event_id} is included in the current demand",
            )

        if payment_included is False and return_included is None:
            # Return inclusion is unresolved; payment is definitely excluded
            payables = sorted([h4, h3])
            return ReconciliationResult(
                case_id=case_id,
                expected_payables=payables,
                expected_state="unresolved",
                missing_fact="whether accepted return is included in the current demand",
            )

        # Default fallback
        return ReconciliationResult(
            case_id=case_id,
            expected_payables=[h4, h3, h2, h1],
            expected_state="unresolved",
        )
