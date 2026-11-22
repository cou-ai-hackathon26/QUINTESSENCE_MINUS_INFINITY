"""
Liquidity Outlook & Channel Shortfall Domain Engine.
Distinguishes spendable cash right now from digital channels and future promises.
Enforces that a promise is not spendable cash until realized,
and that digital balances do not automatically satisfy cash-only obligations.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.domain.money import Money


@dataclass
class AccountBalances:
    cash: Money
    nagad: Money
    bkash: Money

    @property
    def total_digital(self) -> Money:
        return self.nagad + self.bkash

    @property
    def total_all(self) -> Money:
        return self.cash + self.nagad + self.bkash


@dataclass(frozen=True)
class Obligation:
    amount: Money
    accepted_methods: List[str]
    due_at: str


@dataclass(frozen=True)
class Promise:
    amount: Money
    method: str
    at: str
    status: str = "promised_not_actual"


@dataclass
class LiquidityEvaluation:
    case_id: str
    available_spendable_cash: Money
    funding_shortfall: Money
    reserve_shortfall: Money
    cash_before_payment: Optional[Money] = None
    cash_after_payment: Optional[Money] = None
    accounts_after_cashout: Optional[Dict[str, int]] = None
    total_after_cashout: Optional[int] = None


class LiquidityEngine:
    """Pure deterministic liquidity evaluation."""

    @staticmethod
    def evaluate_immediate_obligation(
        case_id: str,
        accounts: AccountBalances,
        obligation: Obligation,
        actual_cash_receipt: Money,
        promise: Optional[Promise] = None,
        cash_reserve: Money = Money(0),
    ) -> LiquidityEvaluation:
        # Spendable cash available right now:
        # A promise is NOT spendable cash right now
        available_cash = accounts.cash + actual_cash_receipt

        # Check obligation method constraint:
        if "cash" in obligation.accepted_methods:
            # Need physical cash
            if available_cash >= obligation.amount:
                cash_before = available_cash
                cash_after = available_cash - obligation.amount
                funding_shortfall = Money(0)
                # Check reserve shortfall
                reserve_shortfall = max(Money(0), cash_reserve - cash_after)
            else:
                cash_before = available_cash
                cash_after = Money(0)
                funding_shortfall = obligation.amount - available_cash
                reserve_shortfall = cash_reserve

            return LiquidityEvaluation(
                case_id=case_id,
                available_spendable_cash=available_cash,
                funding_shortfall=funding_shortfall,
                reserve_shortfall=reserve_shortfall,
                cash_before_payment=cash_before,
                cash_after_payment=cash_after,
            )

        # Non-cash accepted methods can draw from digital accounts
        total_available = accounts.total_all + actual_cash_receipt
        shortfall = max(Money(0), obligation.amount - total_available)
        return LiquidityEvaluation(
            case_id=case_id,
            available_spendable_cash=available_cash,
            funding_shortfall=shortfall,
            reserve_shortfall=max(Money(0), cash_reserve - (total_available - obligation.amount)),
        )

    @staticmethod
    def execute_cashout(
        accounts: AccountBalances,
        from_channel: str,
        principal: Money,
        fee: Money,
    ) -> Tuple[AccountBalances, Money]:
        """
        Calculates accounts after illustrative permitted cashout.
        Debits principal + fee from digital wallet, credits principal to physical cash.
        """
        if from_channel == "nagad":
            new_nagad = accounts.nagad - (principal + fee)
            new_cash = accounts.cash + principal
            new_accounts = AccountBalances(cash=new_cash, nagad=new_nagad, bkash=accounts.bkash)
        elif from_channel == "bkash":
            new_bkash = accounts.bkash - (principal + fee)
            new_cash = accounts.cash + principal
            new_accounts = AccountBalances(cash=new_cash, nagad=accounts.nagad, bkash=new_bkash)
        else:
            raise ValueError(f"Unsupported cashout channel: {from_channel}")

        total = new_accounts.total_all
        return new_accounts, total
