# Phase 20 Evidence: Receiving, Returns, and Credit Recovery

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 20 — Receiving, Returns, and Credit Recovery  

---

## 1. Executive Summary
Phase 20 implements operational delivery intake, discrepancy detection, usable stock updates, and credit recovery lifecycle for Shongoti:
- **Physical Count Independence & Usable Inventory:**
  - `GoodsReceiptModel` records ordered quantity, actual received quantity, damaged cartons, and shortage.
  - Usable inventory stock is updated strictly on physical verification: `usable_units = received_quantity - damaged_quantity`.
- **Automatic Discrepancy Detection & Credit Claims:**
  - Shortages and damaged goods automatically create a `CreditNoteModel` in `status="suspected"` with calculated claim value (`discrepant_units * unit_price_paisa`).
- **Strictly Exactly-Once Credit Application:**
  - Agreed credit notes can be applied to bills or future invoices.
  - Applying an already applied credit note is strictly rejected (`400 Bad Request: already been applied`), preventing double-credit deductions and revenue inflation.
- **Tenant Isolation:**
  - Goods receipts and credit notes enforce strict `tenant_id` boundaries.
- **Accessible Bilingual Web UI:**
  - `ReceivingTracker.tsx` displays intake receipts, shortage/damage counts in Bengali/English, credit recovery status, and one-click invoice application.

---

## 2. API Endpoints
- `POST /api/v1/receiving/receipts`: Records physical delivery receipt, updates usable stock, and flags discrepancies.
- `GET /api/v1/receiving/receipts`: Lists receipts for tenant.
- `GET /api/v1/receiving/credits`: Lists credit claims/notes.
- `POST /api/v1/receiving/credits/{id}/apply`: Applies credit note to invoice (strictly exactly-once).

---

## 3. Test & Verification Results
- Pytest Suite (`apps/api/tests/test_receiving_and_returns.py`): 3/3 PASSED (1.89s)
- Vitest Web Suite (`apps/web/src/tests/ReceivingTracker.test.tsx`): 2/2 PASSED
- TypeScript Typecheck (`tsc --noEmit`): PASSED (0 errors)
