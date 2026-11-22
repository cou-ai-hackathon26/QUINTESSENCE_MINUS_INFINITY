"""
Golden Contract Executable Tests for Shongoti Financial Domain.
Directly loads and verifies the exact contracts from tests/fixtures/contracts/:
- posting.json (PST-001 to PST-008)
- reconciliation.json (REC-001 to REC-008)
- liquidity.json (LIQ-001 to LIQ-006)
- cash-scenarios.json (SCN-001 to SCN-004)
Includes failing invalid inputs and accounting invariants.
"""
import json
import os
import pytest

from app.domain.money import Money
from app.domain.ledger import (
    Posting,
    JournalEntry,
    PostingEngine,
    PostingDirection,
    StandardAccount,
)
from app.domain.reconciliation import (
    ReconciliationEngine,
    DemandFact,
    PaymentFact,
    ReturnFact,
    AllocatedCreditFact,
)
from app.domain.liquidity import (
    LiquidityEngine,
    AccountBalances,
    Obligation,
    Promise,
)
from app.domain.scenarios import (
    ScenarioEngine,
    ConditionalPromise,
)

FIXTURES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests", "fixtures", "contracts")
)


def load_fixture(name: str) -> dict:
    filepath = os.path.join(FIXTURES_DIR, name)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. Posting Contracts (posting.json)
# ==============================================================================

class TestPostingContracts:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.data = load_fixture("posting.json")
        self.engine = PostingEngine()

    def test_pst_001_collect_existing_receivable(self):
        # {"id": "PST-001", "operation": "collect_existing_receivable", "amount": 50000,
        #  "expected_cash_change": 50000, "expected_receivable_change": -50000, "expected_new_sales_revenue": 0}
        amount = Money(50000)
        entry = self.engine.create_collect_receivable_entry("E-001", amount)
        assert entry.entry_id == "E-001"
        
        # Debits and credits
        debit = next(p for p in entry.postings if p.direction == PostingDirection.DEBIT)
        credit = next(p for p in entry.postings if p.direction == PostingDirection.CREDIT)
        
        assert debit.account == StandardAccount.CASH.value
        assert debit.amount == Money(50000)
        assert credit.account == StandardAccount.RECEIVABLES.value
        assert credit.amount == Money(50000)
        
        # Verify no sales revenue account is affected
        assert not any(p.account == StandardAccount.SALES_REVENUE.value for p in entry.postings)

    def test_pst_002_credit_sale(self):
        # {"id": "PST-002", "operation": "credit_sale", "amount": 32000,
        #  "expected_cash_change": 0, "expected_receivable_change": 32000, "expected_sales_revenue_change": 32000}
        amount = Money(32000)
        entry = self.engine.create_credit_sale_entry("E-002", amount)
        debit = next(p for p in entry.postings if p.direction == PostingDirection.DEBIT)
        credit = next(p for p in entry.postings if p.direction == PostingDirection.CREDIT)
        
        assert debit.account == StandardAccount.RECEIVABLES.value
        assert debit.amount == Money(32000)
        assert credit.account == StandardAccount.SALES_REVENUE.value
        assert credit.amount == Money(32000)
        assert not any(p.account == StandardAccount.CASH.value for p in entry.postings)

    def test_pst_003_split_sale(self):
        # {"id": "PST-003", "operation": "split_sale", "amount": 32000, "cash_received": 20000,
        #  "expected_cash_change": 20000, "expected_receivable_change": 12000, "expected_sales_revenue_change": 32000}
        total = Money(32000)
        cash_rec = Money(20000)
        entry = self.engine.create_split_sale_entry("E-003", total, cash_rec)
        
        cash_p = next(p for p in entry.postings if p.account == StandardAccount.CASH.value)
        rec_p = next(p for p in entry.postings if p.account == StandardAccount.RECEIVABLES.value)
        rev_p = next(p for p in entry.postings if p.account == StandardAccount.SALES_REVENUE.value)
        
        assert cash_p.direction == PostingDirection.DEBIT and cash_p.amount == Money(20000)
        assert rec_p.direction == PostingDirection.DEBIT and rec_p.amount == Money(12000)
        assert rev_p.direction == PostingDirection.CREDIT and rev_p.amount == Money(32000)

    def test_pst_004_repeat_verified_provider_event(self):
        # {"id": "PST-004", "operation": "repeat_verified_provider_event", "provider_event_id": "SYNTHETIC-EVT-1",
        #  "attempts": 2, "expected_posted_receipts": 1}
        evt_id = "SYNTHETIC-EVT-1"
        posted_count = 0
        for _ in range(2):
            if not self.engine.is_event_processed(evt_id):
                posted_count += 1
                self.engine.record_processed_event(evt_id)
        assert posted_count == 1

    def test_pst_005_concurrent_allocation(self):
        # {"id": "PST-005", "operation": "concurrent_allocation", "verified_payment_capacity": 400000,
        #  "requested_allocations": [400000, 400000], "expected_max_total_allocated": 400000, "expected_successful_full_allocations": 1}
        capacity = Money(400000)
        requests = [Money(400000), Money(400000)]
        total_allocated, full_successes = self.engine.allocate_payment_capacity(capacity, requests)
        assert total_allocated == Money(400000)
        assert full_successes == 1

    def test_pst_006_approve_stale_case(self):
        # {"id": "PST-006", "operation": "approve_stale_case", "approved_version": 1, "current_version": 2,
        #  "expected_committed_postings": 0, "expected_state": "conflict_or_needs_review"}
        case_id = "CASE-101"
        self.engine.set_case_version(case_id, 2)
        success, state, committed = self.engine.approve_case(case_id, approved_version=1)
        assert success is False
        assert state == "conflict_or_needs_review"
        assert committed == 0

    def test_pst_007_owner_withdrawal(self):
        # {"id": "PST-007", "operation": "owner_withdrawal", "amount": 100000,
        #  "expected_cash_change": -100000, "expected_operating_expense_change": 0}
        amount = Money(100000)
        entry = self.engine.create_owner_withdrawal_entry("E-007", amount)
        draw = next(p for p in entry.postings if p.account == StandardAccount.OWNER_DRAW.value)
        cash = next(p for p in entry.postings if p.account == StandardAccount.CASH.value)
        
        assert draw.direction == PostingDirection.DEBIT and draw.amount == Money(100000)
        assert cash.direction == PostingDirection.CREDIT and cash.amount == Money(100000)
        assert not any(p.account == StandardAccount.OPERATING_EXPENSE.value for p in entry.postings)

    def test_pst_008_pending_gateway_settlement(self):
        # {"id": "PST-008", "operation": "pending_gateway_settlement", "verified_amount": 100000, "available_now": false,
        #  "expected_spendable_cash_change": 0, "expected_pending_asset_change": 100000}
        amount = Money(100000)
        entry = self.engine.create_pending_settlement_entry("E-008", amount)
        pending = next(p for p in entry.postings if p.account == StandardAccount.PENDING_GATEWAY.value)
        assert pending.direction == PostingDirection.DEBIT and pending.amount == Money(100000)
        assert not any(p.account == StandardAccount.CASH.value for p in entry.postings)


# ==============================================================================
# 2. Supplier Reconciliation Contracts (reconciliation.json)
# ==============================================================================

class TestReconciliationContracts:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.data = load_fixture("reconciliation.json")
        facts = self.data["source_facts"]
        self.demand = DemandFact(facts["demand"]["invoice_id"], Money(facts["demand"]["amount"]))
        self.payment = PaymentFact(facts["eligible_payment"]["event_id"], facts["eligible_payment"]["invoice_id"], Money(facts["eligible_payment"]["amount"]))
        self.ret = ReturnFact(facts["accepted_return"]["event_id"], facts["accepted_return"]["invoice_id"], Money(facts["accepted_return"]["amount"]))
        self.unavailable = {
            facts["unavailable_other_receipt"]["event_id"]: AllocatedCreditFact(
                facts["unavailable_other_receipt"]["event_id"],
                Money(facts["unavailable_other_receipt"]["amount"]),
                facts["unavailable_other_receipt"]["allocated_invoice_id"],
                Money(facts["unavailable_other_receipt"]["allocated_amount"]),
            )
        }

    def test_rec_001_all_unresolved(self):
        res = ReconciliationEngine.evaluate("REC-001", self.demand, self.payment, self.ret, self.unavailable, payment_included=None, return_included=None)
        assert res.expected_payables == [1800000, 2100000, 2200000, 2500000]
        assert res.expected_state == "unresolved"

    def test_rec_002_both_included(self):
        res = ReconciliationEngine.evaluate("REC-002", self.demand, self.payment, self.ret, self.unavailable, payment_included=True, return_included=True)
        assert res.expected_payables == [2500000]
        assert res.expected_state == "supported"

    def test_rec_003_payment_included_return_excluded(self):
        res = ReconciliationEngine.evaluate("REC-003", self.demand, self.payment, self.ret, self.unavailable, payment_included=True, return_included=False)
        assert res.expected_payables == [2200000]
        assert res.expected_state == "supported"

    def test_rec_004_payment_excluded_return_included(self):
        res = ReconciliationEngine.evaluate("REC-004", self.demand, self.payment, self.ret, self.unavailable, payment_included=False, return_included=True)
        assert res.expected_payables == [2100000]
        assert res.expected_state == "supported"

    def test_rec_005_both_excluded(self):
        res = ReconciliationEngine.evaluate("REC-005", self.demand, self.payment, self.ret, self.unavailable, payment_included=False, return_included=False)
        assert res.expected_payables == [1800000]
        assert res.expected_state == "supported"

    def test_rec_006_payment_unknown_return_excluded(self):
        res = ReconciliationEngine.evaluate("REC-006", self.demand, self.payment, self.ret, self.unavailable, payment_included=None, return_included=False)
        assert res.expected_payables == [1800000, 2200000]
        assert res.expected_state == "unresolved"
        assert res.missing_fact is not None and "TX-B" in res.missing_fact

    def test_rec_007_attempt_reuse_credit_allocated_to_other_invoice(self):
        res = ReconciliationEngine.evaluate("REC-007", self.demand, self.payment, self.ret, self.unavailable, payment_included=False, return_included=False, attempt_reuse_event_id="TX-A")
        assert res.expected_payables == [1800000]
        assert res.applied_credits_paisa == 0

    def test_rec_008_no_reply_remains_unresolved(self):
        res = ReconciliationEngine.evaluate("REC-008", self.demand, self.payment, self.ret, self.unavailable, payment_included=None, return_included=False)
        assert res.expected_payables == [1800000, 2200000]
        assert res.expected_state == "unresolved"


# ==============================================================================
# 3. Liquidity & Channel Shortfall Contracts (liquidity.json)
# ==============================================================================

class TestLiquidityContracts:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.data = load_fixture("liquidity.json")
        self.accounts = AccountBalances(
            cash=Money(self.data["accounts"]["cash"]),
            nagad=Money(self.data["accounts"]["nagad"]),
            bkash=Money(self.data["accounts"]["bkash"]),
        )
        self.obligation = Obligation(
            amount=Money(self.data["obligation"]["amount"]),
            accepted_methods=self.data["obligation"]["accepted_methods"],
            due_at=self.data["obligation"]["due_at"],
        )

    def test_liq_001_no_receipt_no_promise(self):
        res = LiquidityEngine.evaluate_immediate_obligation(
            "LIQ-001", self.accounts, self.obligation, actual_cash_receipt=Money(0), promise=None, cash_reserve=Money(0)
        )
        assert res.available_spendable_cash == Money(0)
        assert res.funding_shortfall == Money(100000)

    def test_liq_002_promise_is_not_spendable_cash_now(self):
        promise = Promise(Money(100000), "cash", "2026-11-22T15:00:00+06:00")
        res = LiquidityEngine.evaluate_immediate_obligation(
            "LIQ-002", self.accounts, self.obligation, actual_cash_receipt=Money(0), promise=promise, cash_reserve=Money(0)
        )
        assert res.available_spendable_cash == Money(0)
        assert res.funding_shortfall == Money(100000)

    def test_liq_003_sufficient_cash_receipt(self):
        res = LiquidityEngine.evaluate_immediate_obligation(
            "LIQ-003", self.accounts, self.obligation, actual_cash_receipt=Money(100000), promise=None, cash_reserve=Money(0)
        )
        assert res.cash_before_payment == Money(100000)
        assert res.cash_after_payment == Money(0)
        assert res.funding_shortfall == Money(0)

    def test_liq_004_reserve_shortfall_when_zero_left(self):
        res = LiquidityEngine.evaluate_immediate_obligation(
            "LIQ-004", self.accounts, self.obligation, actual_cash_receipt=Money(100000), promise=None, cash_reserve=Money(50000)
        )
        assert res.cash_after_payment == Money(0)
        assert res.reserve_shortfall == Money(50000)

    def test_liq_005_permitted_cashout_from_nagad(self):
        new_accs, total = LiquidityEngine.execute_cashout(
            self.accounts, from_channel="nagad", principal=Money(100000), fee=Money(2000)
        )
        assert new_accs.cash == Money(100000)
        assert new_accs.nagad == Money(398000)
        assert new_accs.bkash == Money(200000)
        assert total == Money(698000)

    def test_liq_006_future_digital_promise_does_not_satisfy_cash_obligation(self):
        promise = Promise(Money(400000), "bkash", "2026-11-23T10:00:00+06:00")
        res = LiquidityEngine.evaluate_immediate_obligation(
            "LIQ-006", self.accounts, self.obligation, actual_cash_receipt=Money(0), promise=promise
        )
        assert res.available_spendable_cash == Money(0)
        assert res.funding_shortfall == Money(100000)


# ==============================================================================
# 4. 7-Day Spending Scenarios Contracts (cash-scenarios.json)
# ==============================================================================

class TestCashScenariosContracts:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.data = load_fixture("cash-scenarios.json")
        self.dates = self.data["dates"]
        self.opening_cash = Money(self.data["opening_cash"])
        self.assumed_daily = Money(self.data["assumed_daily_cash_receipt"])
        self.planned_outflows = [Money(x) for x in self.data["planned_outflows"]]
        self.reserve_target = Money(self.data["reserve_target"])

    def test_scn_001_baseline_no_interventions(self):
        res = ScenarioEngine.simulate_7_day(
            "SCN-001", self.dates, self.opening_cash, self.assumed_daily, self.planned_outflows, self.reserve_target
        )
        assert res.closing_cash_series == [1100000, 1200000, 700000, 800000, 500000, 600000, 400000]
        assert res.first_reserve_breach is None
        assert res.first_funding_shortfall is None

    def test_scn_002_extra_expense_breach_and_shortfall(self):
        res = ScenarioEngine.simulate_7_day(
            "SCN-002", self.dates, self.opening_cash, self.assumed_daily, self.planned_outflows, self.reserve_target,
            extra_expense_day_1=Money(600000)
        )
        assert res.closing_cash_series == [500000, 600000, 100000, 200000, -100000, 0, -200000]
        assert res.first_reserve_breach == "2026-11-24"
        assert res.first_funding_shortfall == "2026-11-26"

    def test_scn_003_moderate_extra_expense_no_breach(self):
        res = ScenarioEngine.simulate_7_day(
            "SCN-003", self.dates, self.opening_cash, self.assumed_daily, self.planned_outflows, self.reserve_target,
            extra_expense_day_1=Money(100000)
        )
        assert res.closing_cash_series == [1000000, 1100000, 600000, 700000, 400000, 500000, 300000]
        assert res.first_reserve_breach is None
        assert res.first_funding_shortfall is None

    def test_scn_004_extra_expense_with_conditional_promise(self):
        promise = ConditionalPromise(date="2026-11-23", amount=Money(300000))
        res = ScenarioEngine.simulate_7_day(
            "SCN-004", self.dates, self.opening_cash, self.assumed_daily, self.planned_outflows, self.reserve_target,
            extra_expense_day_1=Money(600000), conditional_promise=promise
        )
        assert res.closing_cash_series == [500000, 900000, 400000, 500000, 200000, 300000, 100000]
        assert res.first_reserve_breach == "2026-11-26"
        assert res.first_funding_shortfall is None


# ==============================================================================
# 5. Financial Invariants & Explicit Error Rejection Tests
# ==============================================================================

class TestFinancialInvariants:
    def test_money_rejects_floating_point(self):
        with pytest.raises(TypeError):
            Money(25.50)  # Float rejected

    def test_money_rejects_non_bdt_currency(self):
        with pytest.raises(ValueError):
            Money(1000, currency="USD")

    def test_journal_entry_rejects_unbalanced_postings(self):
        with pytest.raises(ValueError, match="Unbalanced JournalEntry"):
            JournalEntry(
                entry_id="BAD-ENTRY",
                description="Unbalanced entry",
                postings=[
                    Posting(StandardAccount.CASH.value, Money(10000), PostingDirection.DEBIT),
                    Posting(StandardAccount.SALES_REVENUE.value, Money(9000), PostingDirection.CREDIT),
                ],
            )

    def test_posting_rejects_negative_amount(self):
        with pytest.raises(ValueError, match="non-negative"):
            Posting(StandardAccount.CASH.value, Money(-500), PostingDirection.DEBIT)
