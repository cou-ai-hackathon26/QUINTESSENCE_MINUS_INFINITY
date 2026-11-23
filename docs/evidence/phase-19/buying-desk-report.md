# Phase 19 Evidence: Buying Desk and Landed Cost Comparison

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 19 — Buying Desk  

---

## 1. Executive Summary
Phase 19 delivers the Buying Desk module for Shongoti:
- **Offer Ingestion & Bonus Validation:**
  - `SupplierOfferModel` stores SKU, pack size, base unit price (integer paisa), minimum order quantity, cash discount percent, credit period, delivery fees, and bonus conditions.
  - Bonus condition eligibility: If an offer advertises "10 cartons gives 1 free" but the bonus SKU or condition is unverified, confidence is capped strictly at 59 (`has_critical_blocker = True`).
- **Deterministic Landed Cost Arithmetic:**
  - `total_landed_paisa = (base_price * qty * (1 - discount)) + delivery_fee`
  - `effective_units = (qty + verified_bonus) * pack_size`
  - `effective_unit_cost_paisa = total_landed_paisa // effective_units` (integer paisa arithmetic).
- **Cash Liquidity Feasibility Enforcement:**
  - Compares required purchase amount against available liquid cash in `asset:cash` and digital wallet accounts (`asset:wallet:bkash`/`nagad`).
  - Cash-only offers with insufficient funds are flagged as `infeasible_insufficient_cash` with exact shortfall BDT.
- **Order Draft & Non-Mutation:**
  - Creates reviewable purchase order draft in `ActionModel` (`status="draft"`).
  - Explicit owner/manager approval required in Action Center before any ledger or stock mutation.
- **Accessible Bilingual Web UI:**
  - `BuyingDesk.tsx` displays side-by-side supplier cards, best-value badges, effective unit costs in BDT, bonus badges, and cash shortfall alerts.

---

## 2. API Endpoints
- `POST /api/v1/buying/offers`: Ingests supplier offer with bonus condition validation.
- `GET /api/v1/buying/offers`: Lists offers for tenant.
- `POST /api/v1/buying/compare`: Compares landed costs and cash feasibility.
- `POST /api/v1/buying/orders/draft`: Creates purchase order draft.

---

## 3. Test & Verification Results
- Pytest Suite (`apps/api/tests/test_buying_desk.py`): 4/4 PASSED (1.92s)
- Vitest Web Suite (`apps/web/src/tests/BuyingDesk.test.tsx`): 2/2 PASSED (212ms)
- Full Offline Verification Gate: 109 API tests, 34 domain contracts, 17 web tests, build, and static scans passing.
