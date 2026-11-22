"""
7-Day Cash Outlook & Spending-Impact Scenario Engine.
Simulates daily cash flow over a 7-day horizon.
Identifies first reserve breach and first funding shortfall without mutating ledger.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.domain.money import Money


@dataclass(frozen=True)
class ConditionalPromise:
    date: str
    amount: Money
    status: str = "promised_not_actual"


@dataclass
class ScenarioEvaluation:
    case_id: str
    closing_cash_series: List[int]  # daily closing cash in paisa
    first_reserve_breach: Optional[str]  # date string or None
    first_funding_shortfall: Optional[str]  # date string or None


class ScenarioEngine:
    """Pure deterministic 7-day scenario simulation."""

    @staticmethod
    def simulate_7_day(
        case_id: str,
        dates: List[str],
        opening_cash: Money,
        assumed_daily_receipt: Money,
        planned_outflows: List[Money],
        reserve_target: Money,
        extra_expense_day_1: Money = Money(0),
        conditional_promise: Optional[ConditionalPromise] = None,
    ) -> ScenarioEvaluation:
        if len(dates) != 7 or len(planned_outflows) != 7:
            raise ValueError("Scenario simulation requires exactly 7 days and 7 planned outflow values.")

        current_cash = opening_cash
        closing_cash_series: List[int] = []
        first_reserve_breach: Optional[str] = None
        first_funding_shortfall: Optional[str] = None

        for day_idx, date in enumerate(dates):
            # Day inflows: assumed daily cash receipt
            inflow = assumed_daily_receipt

            # Check if conditional promise lands on this date
            if conditional_promise and conditional_promise.date == date:
                inflow = inflow + conditional_promise.amount

            # Outflows: planned outflow for this day
            outflow = planned_outflows[day_idx]

            # Day 1 extra expense intervention
            if day_idx == 0:
                outflow = outflow + extra_expense_day_1

            # Net day calculation
            current_cash = current_cash + inflow - outflow
            closing_cash_series.append(current_cash.paisa)

            # Check reserve breach: closing cash strictly less than reserve target
            if current_cash < reserve_target and first_reserve_breach is None:
                first_reserve_breach = date

            # Check funding shortfall: closing cash strictly less than 0
            if current_cash.is_negative() and first_funding_shortfall is None:
                first_funding_shortfall = date

        return ScenarioEvaluation(
            case_id=case_id,
            closing_cash_series=closing_cash_series,
            first_reserve_breach=first_reserve_breach,
            first_funding_shortfall=first_funding_shortfall,
        )
