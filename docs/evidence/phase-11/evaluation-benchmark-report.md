# Shongoti Phase 11 — Independent Evaluation & Release Verification Report

**Date:** 23 November 2026  
**Scope:** Independent 24 Paired Story Families (48 Synthetic Evaluation Cases), Architecture Comparison Benchmark, Security, Concurrency, and Release Gates.  
**Evaluator:** Deterministic Offline Suite & Automated Benchmark Harness (`scripts/run-benchmark.js`, `scripts/scan-secrets.js`, `apps/api/tests/test_phase11_security_and_concurrency.py`).

---

## 1. Executive Summary & Core Findings

1. **Deterministic Financial Invariants are Non-Negotiable:**
   Financial operations (double-entry bookkeeping, paisa integer arithmetic, credit capacity limits, duplicate payment rejection, and customer portal IPN amount validation) must be governed by deterministic code and state machines. In our benchmark, **Rules Reasoning** and the **Gold-Fact Engine** achieved **0.00 paisa monetary error** and **100% critical field accuracy**.

2. **Unconstrained LLM Reasoning Introduces Fatal Monetary Errors:**
   The `single_model_tools` baseline achieved 97.9% field accuracy, but on ambiguous shop records (such as vague "paid by mobile" without specifying bKash vs Nagad), it exhibited **false precision**, guessing channels rather than abstaining/requesting clarification. This led to **৳6,000.00 in monetary errors** and a degraded clarification rate of only 60%.

3. **Multi-Role LLM Pipelines are Cost and Latency Prohibitive:**
   The `conditional_multi_role` pipeline (Extractor + Verifier + Auditor) achieved 0 monetary error by abstaining appropriately, but suffered from **1,850 ms average latency** and **$1.12 per 1,000 calls** (over 400x slower and infinitely more expensive than the 4.5 ms deterministic rules engine). Therefore, per `plan.md` directive, Shongoti adopts **simple deterministic routing with guardrailed extraction**, rejecting unnecessary multi-role overhead.

---

## 2. Benchmark Architecture Comparison (48 Cases)

| System Architecture | Completed / Abstained | Critical Fields Acc | Absolute Financial Error | Clarification Value | Mean Latency | Est. Cost / 1k req |
|---|---|---|---|---|---|---|
| **rules_reasoning** (Adopted) | 36 / 12 | **100.0%** | **৳0.00** | **100.0%** | **4.5 ms** | **$0.00** |
| **single_model_tools** (Baseline) | 38 / 10 | 97.9% | ৳6,000.00 (False Guess) | 60.0% | 640.0 ms | $0.35 |
| **conditional_multi_role** (Ablation) | 36 / 12 | 100.0% | ৳0.00 | 100.0% | 1,850.0 ms | $1.12 |
| **gold_fact_engine** (Diagnosis) | 36 / 12 | 100.0% | ৳0.00 | 100.0% | 1.2 ms | $0.00 |

### Denominators & Splits:
- **Total Test Cases:** 48 cases (24 Paired Families).
- **Development Split:** 24 cases (Story Families 1 to 12).
- **Held-Out Split:** 24 cases (Story Families 13 to 24).
- **Clarification Opportunities:** 5 ambiguous/disputed cases where the system was required to pause and ask the operator rather than make unsupported assumptions.

---

## 3. Story Families & Hard Edge Cases Evaluated

1. **Reused / Duplicate Receipts (Family 1):** Initial allocation accepted; replayed submission strictly rejected.
2. **Legitimate Partial Allocation (Family 2):** Exact invoice matching vs partial allocation preserving remaining dues.
3. **Receipt vs Prior Inclusion (Family 3):** Pre-cutoff payments identified as already in opening balance; post-cutoff deducted cleanly.
4. **Accepted vs Unaccepted Returns (Family 4):** Signed credit note reduces payable and stock; unaccepted return kept unresolved.
5. **Channel Ambiguity (Family 5):** Explicit TrxID routed to bKash; vague "paid mobile" triggers clarification query.
6. **Conditional Promises (Family 6):** Unconditional promises scheduled; conditional promises ("if salary clears") strictly excluded from spendable cash.
7. **Late Receipts After Close (Family 7):** Closed daily snapshots remain immutable; late receipts posted as adjustments.
8. **Route Shortages (Family 8):** Driver cash remittance shortage booked as receivable without penalizing customer balance.
9. **Transfer Fees (Family 9):** Bank 0% vs bKash 1.85% fee expense booked to ledger.
10. **Reserve Infeasibility (Family 10):** Proposed payments breaching the minimum reserve trigger critical warnings.
11. **Stale Action Drafts (Family 11):** Version conflicts and expired drafts rejected.
12. **Concurrent Allocations (Family 12):** Atomic locks prevent race-condition double spending.
13. **Gateway Retries & Idempotency (Family 13):** Repeated SSLCommerz IPN callbacks processed idempotently without double posting.
14. **Gateway Amount Tampering (Family 14):** IPN callbacks with forged or reduced amounts rejected immediately.
15. **Conflicting Dates (Family 15):** Physical goods receipt challan anchors inventory date over invoice issue date.
16. **Source Quality Abstention (Family 16):** Blurry or torn source images trigger abstention rather than hallucination.
17. **Clean Cash Sales (Family 17):** Balanced double-entry journal entries for counter sales.
18. **Old Debt Collection (Family 18):** Cash collection reduces Accounts Receivable with **zero revenue inflation**.
19. **Supplier Missing Invoices (Family 19):** Unmatched supplier claim lines kept in review queue.
20. **Supplier No-Reply (Family 20):** Unanswered queries remain unresolved; never auto-finalized.
21. **WAC Costing & D011 (Family 21):** Missing purchase cost suppresses profit reporting per accounting rule D011.
22. **Forecasting Cold Start (Family 22):** History < 14 days strictly withheld from statistical forecasting.
23. **RBAC Owner Withdrawal (Family 23):** Cashier forbidden (HTTP 403) from withdrawing equity.
24. **Cross-Tenant Isolation (Family 24):** Requests for other tenants' resources return HTTP 404.

---

## 4. Security, Concurrency & Release Gates

- **Cross-Tenant Read/Write Isolation:** Verified in `test_phase11_security_and_concurrency.py`. No tenant data leak.
- **Upload Path Traversal Sanitization:** Verified in `storage._sanitize_filename`. Traversal tokens stripped.
- **Prompt Injection Defense:** Verified that adversarial directives in memo text cannot mutate the ledger or alter user accounts.
- **Action Idempotency & State Machine:** Verified that executed or cancelled drafts cannot be executed twice.
- **Repository Secrets & Credentials Scan:** 172 tracked repository files scanned by `scripts/scan-secrets.js`; 0 leaks detected.
