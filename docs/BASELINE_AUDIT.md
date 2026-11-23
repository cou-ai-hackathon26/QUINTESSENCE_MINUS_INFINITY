# Shongoti Baseline Audit & Gap Reconciliation

**Audit Date:** 23 November 2026  
**Audited Baseline SHA:** `8d4c122d712edbca4adad998090727779bef1dd0` (Phase 12 checkpoint receipt)  
**Governing Contract:** [EXTENSION_PLAN.md](../EXTENSION_PLAN.md) (Phase 13, Task P13-T01)  
**Auditor:** Antigravity Autonomous Agent

---

## 1. Executive Summary

This audit establishes a truthful, empirical baseline of the Shongoti codebase prior to initiating the Phase 13–26 product extension. The project contains a substantial, verified foundation—including an exact double-entry ledger in integer paisa, full PostgreSQL and SQLite persistence, bilingual React UI, and deterministic business rules. However, several previously published claims exceeded actual empirical boundaries (notably live AI extraction, forecasting rolling evaluation, and benchmark execution).

This document establishes the exact line between:
1. **Implemented & Verified:** Truly built, executed, and covered by meaningful tests.
2. **Deterministic Test Doubles (Mocks):** Local simulated adapters that verify business rules but do not prove external provider readiness.
3. **Reopened Legacy Work:** Capabilities where synthetic success was previously reported but actual implementation or live testing was missing.
4. **Blocked Gates:** Tasks requiring external credentials, cloud hosting, or live services that remain unconfigured.

---

## 2. Phase-by-Phase Claim vs Reality Audit

| Phase | Original Name | Claimed Status | Audited Reality | Disposition |
|---|---|---|---|---|
| **00** | Repo & Handoff | Complete | Clean repository, private origin, structured tracker. | **Verified** |
| **01** | Foundation & Skeleton | Complete | Command runners, TypeScript configs, FastAPI skeleton, health check pass. | **Verified** |
| **02** | Exact Financial Domain | Complete | 34 golden contract tests pass (Money paisa primitive, balanced journal entries, capacity allocation, 4 reconciliation hypotheses, 7-day scenarios). | **Verified** |
| **03** | Database & Persistence | Complete | Alembic migration `001_initial_schema.py`, PostgreSQL 16 & SQLite support, JWT session validation, tenant data isolation. | **Verified** |
| **04** | Evidence & Real AI | Blocked / Partial | Intake, SHA-256 storage, and native PDF extraction (`pypdf`) verified. **Gap:** `AIModelAdapter` raises an exception when `GEMINI_API_KEY` is present; unconfigured path returns hardcoded synthetic responses. Image and audio bytes are not routed to real multimodal endpoints. | **Reopened as In-Progress** (Repaired in Phase 14) |
| **05** | Supplier Reconciliation | Blocked | Local domain logic for 4 hypotheses is complete. **Gap:** End-to-end live extraction of unparsed supplier claims into the hypothesis engine is blocked on Phase 04. | **Blocked** (Repaired in Phase 14) |
| **06** | Daily Merchant Workflow | Complete | Sales (cash/credit/split), debt collection without revenue double-counting, wallet transfers with 1.85% fee, stock deductions, cash close discrepancies, cashier RBAC denial (HTTP 403). 24 API tests pass. | **Verified** |
| **07** | Liquidity Scenarios | Complete | `ScenarioModel`, migration `004_scenarios_schema.py`, non-mutation of actual books verified, Day 3 reserve breach and Day 5 cash shortfall alerts verified. | **Verified** |
| **08** | Action Center & Portal | Complete | Action approvals, cashier prohibition, idempotency, scoped customer portal (`/pay/:token`), dispute notes, and SSLCommerz sandbox callback tamper rejection verified. | **Verified** |
| **09** | Stock & Reports | Complete | WAC recalculation per D011, lead-time cover, accepted customer/supplier returns, cash-aware reorders, 4 operating reports with D011 profit suppression, CSV import with SKU deduplication. **Gap:** Forecast adapter uses a single 7-day holdout rather than a true rolling-origin evaluation; prediction intervals lack calibrated coverage proof. | **Partially Verified** (Forecast rolling evaluation repaired in Phase 21) |
| **10** | Product UI & Accessibility | Complete | 14 dedicated React pages, complete bilingual support (বাংলা/English), responsive styles (360/768/1440px), focus-visible, and touch targets. **Gap:** `scripts/test-e2e.js` asserts CSS regexes and unit tests rather than driving a real headless browser. | **Partially Verified** (Real browser gate added in Phase 13/25) |
| **11** | Evaluation & Security | Complete | 24 paired story families (48 cases) fixture exists; security tests pass (tenant isolation, traversal sanitization, prompt injection, idempotency, SSLCommerz tampering); secrets scan passes (0 leaks). **Gap:** `scripts/run-benchmark.js` assigned synthetic constants/latencies rather than executing real model architectures. | **Reopened as In-Progress** (Real benchmark comparison executed in Phase 25) |
| **12** | Deployment & Handover | Complete | `Dockerfile.api`, `Dockerfile.web`, `docker-compose.yml`, `.env.production.example`, smoke-test suite, and `HANDOVER.md`. Local containerization verified; cloud hosting deferred per contract. | **Verified (Local Scope)** |

---

## 3. Implemented vs Tested vs Simulated vs Blocked Matrix

```
[Implemented & Tested]
  ├── Exact Money Domain (Integer paisa arithmetic, no floating-point)
  ├── Double-Entry Ledger (Balanced debit/credit postings)
  ├── Multi-Tenant Database (PostgreSQL 16, SQLite test pool, Alembic 001-006)
  ├── JWT Auth & Role Permissions (Owner vs Cashier authorization)
  ├── Evidence Storage (Tenant isolated, SHA-256 integrity, path traversal stripping)
  ├── Native PDF Extraction (pypdf text extraction)
  ├── Merchant Daily Workflows (Sales, collections, drawer close, discrepancies)
  ├── Scenario Engine (7-day simulation, reserve breach alerts, zero actual ledger mutation)
  ├── Action Lifecycle (Drafting, approvals, cancellation, idempotency)
  ├── Customer Portal & Disputes (Public scoped token view, dispute note intake)
  ├── SSLCommerz Gateway Adapter (Order validation, IPN callback verification, amount tamper defense)
  ├── Stock & WAC Costing (Weighted Average Costing, returnrestocking, D011 profit suppression)
  ├── Operating Reports (Cash, P&L, Inventory, Dues, CSV import/export)
  └── Bilingual Web App (14 React pages with instant BN/EN switch)

[Simulated / Test Doubles]
  ├── AI Extraction Boundary (AIModelAdapter hardcoded branches for "হক ট্রেডার্স" and "বকেয়া ৫০০")
  └── Benchmark Runner (run-benchmark.js assigns pre-calculated latency and cost metrics)

[Blocked External Gates]
  ├── Real AI Provider Call (Blocked pending GEMINI_API_KEY with genuine SDK/HTTP implementation)
  ├── Production Payment Gateway (Live merchant credentials require real merchant onboarding)
  └── External Cloud Hosting (Local containers verified; public cloud hosting requires infra credentials)
```

---

## 4. Identity, Demo, and RBAC Security Audit

### Current Findings in `app/core/auth.py` and `app/api/v1/router.py`:
1. **Token Verification:**
   `decode_access_token` strictly validates HMAC-SHA256 signatures using `settings.SECRET_KEY`. User identity cannot be forged without the secret key.
2. **Tenant Scoping:**
   All queries for parties, accounts, products, actions, and evidence explicitly filter by `current_user.tenant_id`. Cross-tenant data leaks are verified to return HTTP 404/400.
3. **Identified Risk (Registration Authorization):**
   In `router.py`, the `login` endpoint creates new users if a phone number is unseen. If a request supplies an existing `tenant_id` alongside a new phone, it creates the user under that tenant with `role=req.role or "owner"`. This allows an unauthenticated user to register themselves as an `owner` of an existing tenant if they guess or know the `tenant_id`.
   - **Remediation for Phase 13:** If `tenant_id` is specified during self-registration, the new user's role must strictly default to `cashier` unless an explicit invite token or owner verification is presented.

---

## 5. Actual API Endpoints & Data Contracts Inventory

| Route | Method | Purpose | Auth / Role Scope |
|---|---|---|---|
| `/health` | GET | Basic service liveness | Public |
| `/ready` | GET | Database connectivity readiness | Public |
| `/api/v1/auth/login` | POST | Phone/OTP login & JWT issuance | Public |
| `/api/v1/auth/demo-session` | POST | Instant demo tenant session | Public |
| `/api/v1/ledger/accounts` | GET | List tenant chart of accounts | Authenticated |
| `/api/v1/ledger/journal-entries` | POST | Post balanced double-entry transaction | Authenticated |
| `/api/v1/merchant/today` | GET | Current liquid balances & sales summary | Authenticated |
| `/api/v1/merchant/sales` | POST | Record cash, credit, or split sale | Authenticated |
| `/api/v1/merchant/debt-collection` | POST | Collect customer debt (no revenue inflation) | Authenticated |
| `/api/v1/merchant/transfers` | POST | Channel transfer with 1.85% cashout fee | Authenticated |
| `/api/v1/merchant/drawer-close` | POST | Daily drawer close & discrepancy booking | Authenticated |
| `/api/v1/merchant/withdrawals` | POST | Owner equity withdrawal | Owner Role Only (Cashier 403) |
| `/api/v1/evidence/upload` | POST | Upload and hash evidence file | Authenticated |
| `/api/v1/evidence/extract/{id}` | POST | Extract claims from document | Authenticated |
| `/api/v1/scenarios/simulate` | POST | Simulate 7-day liquidity outlook | Authenticated |
| `/api/v1/scenarios/baseline` | GET | Baseline 7-day projection | Authenticated |
| `/api/v1/actions` | POST | Create versioned action draft | Authenticated |
| `/api/v1/actions/{id}/approve` | POST | Approve action | Owner Role Only (Cashier 403) |
| `/api/v1/actions/{id}/execute` | POST | Execute approved action idempotently | Authenticated |
| `/api/v1/portal/generate-link` | POST | Generate customer invoice payment link | Authenticated |
| `/api/v1/portal/{token}` | GET | View public scoped invoice | Public (Scoped Token) |
| `/api/v1/portal/{token}/dispute` | POST | Submit customer invoice dispute note | Public (Scoped Token) |
| `/api/v1/portal/{token}/pay` | POST | Initiate SSLCommerz checkout session | Public (Scoped Token) |
| `/api/v1/payments/sslcommerz/ipn` | POST | SSLCommerz IPN callback & tamper check | Public (IPN Verified) |
| `/api/v1/stock/products` | GET/POST | List and manage inventory items | Authenticated |
| `/api/v1/reports/operating-summary` | GET | Operating reports (Cash, P&L, Stock, Dues) | Owner Role Only (Cashier 403) |
| `/api/v1/reports/export/products.csv` | GET | Export catalog CSV | Owner Role Only (Cashier 403) |
| `/api/v1/reports/import/products.csv` | POST | Import catalog CSV with deduplication | Owner Role Only (Cashier 403) |

---

## 6. Legacy-to-Extension Repair Map

1. **Phase 04 / Phase 14 Repair:**
   - Replace the synthetic branch in `AIModelAdapter` with a genuine Google GenAI / Gemini API client.
   - Implement multimodal routing for JPEG, PNG, PDF, and audio formats.
   - Enforce explicit `null`/`unknown` fields instead of guessing.
2. **Phase 05 / Phase 14 Repair:**
   - Connect genuine interpreted evidence output directly into the 4 reconciliation hypotheses in `app/domain/reconciliation.py`.
3. **Phase 09 / Phase 21 Repair:**
   - Replace single-holdout evaluation in `app/adapters/forecast.py` with multi-step rolling-origin backtesting.
4. **Phase 10 / Phase 13 & 25 Repair:**
   - Separate static CSS checks from genuine browser automation.
   - Add a truthful browser runner in Phase 13 and complete interactive browser testing in Phase 25.
5. **Phase 11 / Phase 25 Repair:**
   - Supersede simulated benchmark figures in `scripts/run-benchmark.js`.
   - Execute empirical model-against-tool evaluations in Phase 25.

---

## 7. Immediate Next Actions

- **Task P13-T02:** Implement honest verification runners with distinct exit codes (0 = passed, 1 = failed, 2 = blocked), separate environment detection from capability testing, and create the required new root command stubs.
- **Task P13-T03:** Execute the unified baseline suite, patch the registration role security finding, and confirm zero regression.
- **Task P13-T04:** Reconcile progress records and publish the verified Phase 13 baseline checkpoint.
