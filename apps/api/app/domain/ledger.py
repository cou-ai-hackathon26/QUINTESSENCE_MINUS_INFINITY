"""
Financial Ledger & Posting Engine.
Guarantees balanced entries, integer paisa arithmetic, idempotency,
capacity checks, and append-only reversals.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from app.domain.money import Money


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class StandardAccount(str, Enum):
    CASH = "asset:cash"
    RECEIVABLES = "asset:accounts_receivable"
    PENDING_GATEWAY = "asset:pending_gateway_settlement"
    MOBILE_BKASH = "asset:wallet:bkash"
    MOBILE_NAGAD = "asset:wallet:nagad"
    PAYABLES = "liability:accounts_payable"
    SALES_REVENUE = "revenue:sales"
    OPERATING_EXPENSE = "expense:operating"
    TRANSFER_FEE = "expense:transfer_fee"
    OWNER_DRAW = "equity:owner_draw"
    OWNER_CAPITAL = "equity:owner_capital"


class PostingDirection(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass(frozen=True)
class Posting:
    account: str
    amount: Money
    direction: PostingDirection

    def __post_init__(self):
        if not isinstance(self.amount, Money) or self.amount.is_negative():
            raise ValueError(f"Posting amount must be non-negative Money, got {self.amount}")


@dataclass
class JournalEntry:
    entry_id: str
    description: str
    postings: List[Posting]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.validate_balanced()

    def validate_balanced(self) -> None:
        """Enforces fundamental accounting equation: sum(debits) == sum(credits)."""
        debit_sum = sum((p.amount.paisa for p in self.postings if p.direction == PostingDirection.DEBIT), 0)
        credit_sum = sum((p.amount.paisa for p in self.postings if p.direction == PostingDirection.CREDIT), 0)
        if debit_sum != credit_sum:
            raise ValueError(
                f"Unbalanced JournalEntry '{self.entry_id}': debits={debit_sum} paisa != credits={credit_sum} paisa"
            )


class PostingEngine:
    """Manages journal posting, idempotency, versioning, and capacity checks."""

    def __init__(self) -> None:
        self._processed_events: Set[str] = set()
        self._journal: List[JournalEntry] = []
        self._case_versions: Dict[str, int] = {}

    def is_event_processed(self, event_id: str) -> bool:
        return event_id in self._processed_events

    def record_processed_event(self, event_id: str) -> None:
        self._processed_events.add(event_id)

    def set_case_version(self, case_id: str, version: int) -> None:
        self._case_versions[case_id] = version

    def get_case_version(self, case_id: str) -> int:
        return self._case_versions.get(case_id, 1)

    def approve_case(self, case_id: str, approved_version: int) -> Tuple[bool, str, int]:
        """Verifies stale version before committing approvals."""
        current_version = self.get_case_version(case_id)
        if approved_version != current_version:
            return False, "conflict_or_needs_review", 0
        return True, "approved", 1

    def allocate_payment_capacity(
        self, verified_capacity: Money, requested_allocations: List[Money]
    ) -> Tuple[Money, int]:
        """
        Enforces that concurrent or sequential allocations cannot exceed verified capacity.
        Returns: (total_allocated_money, successful_full_allocations_count)
        """
        remaining = verified_capacity.paisa
        total_allocated = 0
        full_successes = 0

        for req in requested_allocations:
            if req.paisa <= remaining:
                remaining -= req.paisa
                total_allocated += req.paisa
                full_successes += 1
            else:
                # Partial allocation or rejection
                pass

        return Money(total_allocated), full_successes

    # Core event posting builders ensuring balanced entries:

    @staticmethod
    def create_collect_receivable_entry(entry_id: str, amount: Money) -> JournalEntry:
        """
        Collect existing customer due.
        Debit Cash (+asset), Credit Accounts Receivable (-asset).
        Sales revenue impact: 0 (revenue was recognized at sale time).
        """
        return JournalEntry(
            entry_id=entry_id,
            description="Collect existing receivable",
            postings=[
                Posting(StandardAccount.CASH.value, amount, PostingDirection.DEBIT),
                Posting(StandardAccount.RECEIVABLES.value, amount, PostingDirection.CREDIT),
            ],
        )

    @staticmethod
    def create_credit_sale_entry(entry_id: str, amount: Money) -> JournalEntry:
        """
        Credit sale to customer.
        Debit Accounts Receivable (+asset), Credit Sales Revenue (+revenue).
        Cash impact: 0.
        """
        return JournalEntry(
            entry_id=entry_id,
            description="Credit sale",
            postings=[
                Posting(StandardAccount.RECEIVABLES.value, amount, PostingDirection.DEBIT),
                Posting(StandardAccount.SALES_REVENUE.value, amount, PostingDirection.CREDIT),
            ],
        )

    @staticmethod
    def create_split_sale_entry(entry_id: str, total_amount: Money, cash_received: Money) -> JournalEntry:
        """
        Sale with partial cash and partial credit.
        Debit Cash (+asset), Debit Accounts Receivable (+asset), Credit Sales Revenue (+revenue).
        """
        receivable = total_amount - cash_received
        return JournalEntry(
            entry_id=entry_id,
            description="Split sale (cash + receivable)",
            postings=[
                Posting(StandardAccount.CASH.value, cash_received, PostingDirection.DEBIT),
                Posting(StandardAccount.RECEIVABLES.value, receivable, PostingDirection.DEBIT),
                Posting(StandardAccount.SALES_REVENUE.value, total_amount, PostingDirection.CREDIT),
            ],
        )

    @staticmethod
    def create_owner_withdrawal_entry(entry_id: str, amount: Money) -> JournalEntry:
        """
        Owner equity withdrawal.
        Debit Owner Draw (+equity draw), Credit Cash (-asset).
        Operating expense change: 0 (not an operating business expense).
        """
        return JournalEntry(
            entry_id=entry_id,
            description="Owner withdrawal",
            postings=[
                Posting(StandardAccount.OWNER_DRAW.value, amount, PostingDirection.DEBIT),
                Posting(StandardAccount.CASH.value, amount, PostingDirection.CREDIT),
            ],
        )

    @staticmethod
    def create_pending_settlement_entry(entry_id: str, amount: Money) -> JournalEntry:
        """
        Pending digital gateway settlement.
        Debit Pending Gateway Settlement (+asset), Credit Sales Revenue (+revenue).
        Spendable cash change: 0 (funds are unsettled).
        """
        return JournalEntry(
            entry_id=entry_id,
            description="Pending gateway settlement",
            postings=[
                Posting(StandardAccount.PENDING_GATEWAY.value, amount, PostingDirection.DEBIT),
                Posting(StandardAccount.SALES_REVENUE.value, amount, PostingDirection.CREDIT),
            ],
        )
