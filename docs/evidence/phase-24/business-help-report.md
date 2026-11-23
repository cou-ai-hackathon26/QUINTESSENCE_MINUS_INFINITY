# Phase 24 Evidence: Maintained Business Help Desk

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 24 — Maintained Business Help Desk  

---

## 1. Executive Summary
Phase 24 implements official regulatory corpus governance and the business compliance vault for Shongoti:
- **Business Document Vault:**
  - `BusinessDocumentModel` tracks core commercial documents (Trade License, e-TIN, VAT BIN, Shop Lease, Fire License).
  - Evaluates statutory expiry dates and flags status (`valid`, `expiring_soon`, `expired`, `missing`).
  - Strict tenant isolation guarantees confidential lease and registration documents are protected.
- **Official Regulatory Corpus Governance:**
  - `RegulatoryCorpusModel` maintains authoritative Bangladesh MSME statutory sources:
    1. *Trade License Renewal:* Local Government (City Corporation) Act 2009 & Model Tax Schedule (Annual renewal by 30 June / 30 September).
    2. *VAT Registration:* VAT and Supplementary Duty Act 2012 (Threshold 50 Lakh BDT for turnover tax, 3 Crore BDT for 15% VAT).
    3. *Income Tax Return:* Income Tax Act 2023 (Mandatory e-TIN for trade license; annual return by 30 November).
    4. *Commercial Shop Lease:* Transfer of Property Act 1882 & Rent Control Act (Stamped non-judicial agreements, security deposit clauses).
- **Truthful Sourced Assistance & Professional Escalation:**
  - Separates statutory rule text from advisory questions.
  - Prohibits fabricated section numbers, deadlines, or fees.
  - Out-of-scope legal disputes strictly trigger `escalation_required: True` advising referral to registered lawyers or tax practitioners.
- **Accessible Bilingual Web UI:**
  - `BusinessHelpDesk.tsx` provides a compliance checklist with expiry indicators and upload triggers, plus a verified statutory guidance query explorer with official government portal links.

---

## 2. API Endpoints
- `GET /api/v1/helpdesk/checklist`: Evaluates compliance status tailored to shop turnover.
- `POST /api/v1/helpdesk/documents`: Registers/updates compliance document metadata in the vault.
- `GET /api/v1/helpdesk/documents`: Lists tenant's vaulted documents.
- `POST /api/v1/helpdesk/guidance`: Retrieves verified primary statute citations and escalation status.
- `GET /api/v1/helpdesk/corpus`: Lists active statutory corpus records and dates.

---

## 3. Test & Verification Results
- Pytest Suite (`apps/api/tests/test_business_help.py`): 4/4 PASSED (4.22s)
- Vitest Web Suite (`apps/web/src/tests/BusinessHelpDesk.test.tsx`): 2/2 PASSED
- TypeScript Typecheck (`tsc --noEmit`): PASSED (0 errors)
