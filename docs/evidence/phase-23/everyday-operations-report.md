# Phase 23 Evidence: Additional Everyday Operations

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 23 — Additional Everyday Operations  

---

## 1. Executive Summary
Phase 23 implements everyday store operational workflows and shift reconciliations for Shongoti:
- **Customer Reservation & Picking Lists:**
  - `CustomerReservationModel` records customer orders and picking requirements (`items_json`, `status: reserved | picked | expired | cancelled`).
  - Evaluates stock availability against real-time product quantities (`ready` vs `needs_substitution`).
  - **Financial Invariant Enforced:** Reserving items NEVER generates revenue, accounts receivable, or ledger entries.
- **Returnable Container & Deposit Tracking:**
  - `ReturnableContainerModel` tracks crates, bottles, and drums issued and returned.
  - Maintains `outstanding_count = issued_count - returned_count` and held refundable deposit paisa.
  - **Financial Invariant Enforced:** Refundable deposits are strictly isolated from goods sales revenue.
- **Shift Handover & Cash Close Hypotheses:**
  - `ShiftHandoverModel` records shift cash declared vs system expected cash.
  - Formulates factual, non-accusatory discrepancy hypotheses referencing unresolved delivery shortages and unapplied credit notes.
- **Scoped Supplier Change Watch:**
  - Evaluates supplier delivery delay and price change proposals strictly scoped to the specific order without global order rewrites.
- **Accessible Bilingual Web UI:**
  - `OperationsHub.tsx` provides dedicated tabs for order reservations & picking lists, returnable container deposit balances, and shift handover discrepancy reviews.

---

## 2. API Endpoints
- `POST /api/v1/operations/reservations`: Creates an order reservation without booking sales.
- `GET /api/v1/operations/reservations`: Lists active reservations and expires stale orders.
- `POST /api/v1/operations/reservations/{id}/pick`: Confirms picked status.
- `POST /api/v1/operations/containers/movement`: Records crate/bottle issue or return.
- `GET /api/v1/operations/containers`: Lists tracked containers and held deposits.
- `POST /api/v1/operations/handovers`: Records shift handover and calculates variance hypotheses.
- `GET /api/v1/operations/handovers`: Lists historical shift handovers.
- `POST /api/v1/operations/supplier-change-check`: Evaluates scoped supplier change proposals.

---

## 3. Test & Verification Results
- Pytest Suite (`apps/api/tests/test_operations.py`): 5/5 PASSED (5.09s)
- Vitest Web Suite (`apps/web/src/tests/OperationsHub.test.tsx`): 2/2 PASSED
- TypeScript Typecheck (`tsc --noEmit`): PASSED (0 errors)
