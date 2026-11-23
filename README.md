# Shongoti (সংগতি)

**UI redesign, 23 November 2026:** The approved landing design and connected workbench are integrated on `main`. Start with [the current UI handoff](docs/UI_REDESIGN_HANDOFF.md), [UI progress](docs/UI_REDESIGN_PROGRESS.md), and [verification evidence](docs/evidence/ui-redesign/UIR-09/). Historical delivery claims below are not a certification of live AI, payments or legal applicability.

**Current development handoff:** Extend the existing application using [EXTENSION_PLAN.md](EXTENSION_PLAN.md), [START_EXTENSION.md](START_EXTENSION.md) and [extension progress](docs/EXTENSION_PROGRESS.md). New Phase 13–26 covers the approved product/AI expansion. Existing AI/evaluation/browser completion claims require reconciliation; new features are not implemented by this handoff.

**A Bilingual (Bangla/English) Financial Workspace for Small Businesses & MSMEs**

Shongoti empowers local shop owners and MSMEs in Bangladesh to capture source evidence, verify supplier obligations, manage daily liquid money, stress-test future spending consequences, and execute reviewed actions safely.

---

## Current Status & Verification

- **Historical delivery report, not a current certification:** the source review reopened AI/reconciliation/evaluation gates, and the extension begins with a reproducible audit. See [current progress](docs/PROGRESS.md). The old test counts and browser/architecture claims below were not independently revalidated by this documentation session; simulated benchmarks and source/CSS scans are not empirical AI/browser evidence.
- **Bilingual Support:** 100% of UI screens support both Bengali (বাংলা) as the first-class default experience and instant toggle to English.
- **Offline Verification Gate:** Passed 100% via `pnpm verify:offline`:
  - 34 Domain Golden Contracts
  - 45 Backend API, Persistence, Security, and Concurrency Tests
  - 8 Web Unit and Workflow Tests
  - 24 Paired Story Families / 48 Cases Architecture Benchmark
  - 172-File Repository Secrets & Leaks Scan (0 leaks)
  - E2E & Browser UI Responsive Verification (360px mobile, 768px tablet, 1440px desktop)
  - Production Vite Web Bundle & Production Dockerfiles

For comprehensive architecture details, test credentials, and reproduction instructions, see **[HANDOVER.md](HANDOVER.md)**.

---

## Key Modules & Features

1. **আজকের হিসাব (Today Dashboard):** Real-time liquid cash, bKash wallet, bank balances, counter sales, credit dues, and cash drawer close with discrepancy tracking.
2. **ভবিষ্যতের পরিকল্পনা (Future Planner & Decision Lab):** 7-day spending impact scenarios, reserve buffer breach warnings (Day 3), and cash shortfall projections (Day 5).
3. **টাকা ও মাধ্যম (Money & Channels):** Channel transfers with 1.85% digital cashout fees and owner equity withdrawals with strict cashier RBAC prohibition.
4. **বিক্রয় ও কাস্টমার (Sales & Customers):** Cash, credit, and split sales; customer debt collection (with **zero revenue double-counting**); 1-click customer payment portal link generator.
5. **পার্টি খাতা (People & Khata):** Customer Khata (বাকি খাতা) and Supplier Khata (মহাজন খাতা) tracking itemized transaction histories.
6. **পাওনা ও মহাজন মিলকরণ (Supplier Reconciliation):** Interactive resolution of 4 golden hypotheses (REC 001 - 004) against supplier statements with credit note allocations.
7. **মজুদ ও মালপত্র (Stock & Inventory):** Stock units, purchase drafts, lead-time cover, customer/supplier return tracking, and Weighted Average Costing (WAC) per accounting rule D011.
8. **রিপোর্ট ও হিসাব বিবরণী (Operating Reports):** 4 strictly separated reports (Cash Statement, Accrual Profit & Loss with incomplete cost suppression, Inventory Valuation, Customer/Supplier Dues), and daily executive briefing.
9. **কানেকশন ও গেটওয়ে (Connections):** SSLCOMMERZ sandbox payment gateway with Order Validation, IPN callback verification, amount tamper defense, and transactional SMS/WhatsApp gating per D009.
10. **কাস্টমার পেমেন্ট পোর্টাল (Public Customer Portal):** Scoped token view (`/pay/:token`) allowing customers to view itemized invoices, submit dispute notes, or pay securely online.

---

## Quick Start Commands

```bash
# 1. Install workspace dependencies
pnpm install

# 2. Run database migrations
pnpm db:migrate

# 3. Run all verification gates
pnpm verify:offline

# 4. Run deployment smoke checks
node scripts/smoke-test.js

# 5. Start concurrent development servers
pnpm dev
```

---

## Core Engineering Invariants

- **D001:** Strict integer paisa arithmetic (৳1.00 = 100 paisa). Floating-point arithmetic is strictly prohibited.
- **D002:** Balanced double-entry general ledger; all debits equal credits.
- **D003:** Actual liquid funds are strictly separated from future customer promises or scenario projections.
- **D004:** Preserves 4 golden supplier reconciliation hypotheses; prevents reusing credits already allocated to other invoices.
- **D007:** Forecasts are cold-start gated (< 14 days of history); rolling-origin backtests evaluate accuracy when history is adequate.
- **D011:** WAC inventory valuation; incomplete cost data suppresses unsupported profit claims rather than assuming ৳0 cost.

---

## Team & Authors

**Team:** Quintessence Minus Infinity  
- Sakibul Hassan Shovon  
- Sabbir Ahmed  
- Sanjid Talukder  

**Repository:** `https://github.com/sakibul-shovon/Shongoti.git`  
**License:** Private
