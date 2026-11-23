# Phase 15 Evidence: Cases, Provenance, and Confidence Policy

**Phase:** 15 — cases, provenance and confidence  
**Date:** 2026-11-23  
**Status:** VERIFIED (All 11 confidence fixture cases, database migrations, Case APIs, and UI tests passed)  
**Target Milestone Footer:** `Shongoti-Phase: 15`  

---

## 1. Scope & Execution Summary

| Task ID | Description | Result | Evidence / Notes |
|---|---|---|---|
| **P15-T01** | Durable Case & Claim Contracts | COMPLETE | Authored Alembic migration `007_cases_and_confidence.py` adding `cases`, `case_versions`, `evidence_claims`, and `confidence_assessments` tables. Created SQLAlchemy models in `apps/api/app/persistence/models.py`. Migration upgraded cleanly against SQLite and PostgreSQL 16. |
| **P15-T02** | Scoring and Routing Policy | COMPLETE | Implemented `apps/api/app/confidence/policy.py` executing exact `evidence-support-v1` policy. Formula: `base = floor(100 * sum(weights of supported) / sum(weights of required) + 0.5)`. Capped at 59 on any unresolved critical claim. `readiness` deterministically routes to `ready_for_review`, `needs_review`, `needs_clarification`, `blocked`, or `unavailable`. `calibrated_probability` is explicitly `None`. |
| **P15-T03** | Accessible Confidence UI Component | COMPLETE | Built `apps/web/src/components/ConfidenceBadge.tsx` with Bengali numerals ("৮৫/১০০", "৫৯/১০০"), non-probability disclaimer, expandable claims provenance drawer, and owner authorization lock badge. |
| **P15-T04** | Behavioral Test Suite & Verification | COMPLETE | Created `apps/api/tests/test_confidence_and_cases.py` asserting all 11 cases from `confidence-policy-v1.json`, case lifecycle, and cross-tenant isolation. Created `apps/web/src/tests/ConfidenceBadge.test.tsx` (3 tests). Wired `package.json` command `"test:confidence"`. |

---

## 2. Test Execution Results

### A. Confidence Policy Fixture Verification (`pnpm test:confidence`)
All 11 test cases in `tests/fixtures/extension-handoff/confidence-policy-v1.json` evaluated and matched with zero discrepancies:
1. `all_supported_index_not_probability`: base=100, score=100, band=strong, readiness=ready_for_review [MATCH]
2. `critical_unknown_caps_67_at_59`: base=67, score=59, band=limited, readiness=needs_clarification [MATCH]
3. `critical_conflict_caps_67_at_59`: base=67, score=59, band=limited, readiness=needs_clarification [MATCH]
4. `ordinary_unknown_not_critical`: base=89, score=89, band=strong, readiness=ready_for_review [MATCH]
5. `provider_unavailable`: base=null, score=null, band=unavailable, readiness=unavailable [MATCH]
6. `source_inaccessible`: base=null, score=null, band=unavailable, readiness=unavailable [MATCH]
7. `stale_case`: base=null, score=null, band=unavailable, readiness=unavailable [MATCH]
8. `validator_blocks_high_self_rating`: base=null, score=null, band=unavailable, readiness=blocked [MATCH]
9. `all_unknown`: base=0, score=0, band=limited, readiness=needs_clarification [MATCH]
10. `no_required_claim_definition`: base=null, score=null, band=unavailable, readiness=unavailable [MATCH]
11. `review_band_noncritical_gaps`: base=73, score=73, band=review, readiness=needs_review [MATCH]

### B. Full Test Suite Summary
- **Domain Golden Contracts:** 34 / 34 PASSED
- **API, Persistence & Security Tests:** 91 / 91 PASSED
  - Including `test_confidence_and_cases.py` (3 tests passed)
  - Including `test_phase14_multimodal_and_reconciliation.py` (8 tests passed)
  - Including `test_phase11_security_and_concurrency.py` (6 tests passed)
- **Web Unit & Workflow Tests:** 11 / 11 PASSED
  - Including `ConfidenceBadge.test.tsx` (3 tests passed)
- **TypeScript Check (`tsc --noEmit`):** PASSED (0 errors)
- **Web Production Build:** PASSED (1595 modules transformed)

---

## 3. Acceptance Gate Assessment
All acceptance criteria for Phase 15 under `EXTENSION_PLAN.md` are satisfied:
- Score is derived, persisted, and explained in code.
- Confidence policy affects real case state (enters `waiting_user` on critical gap).
- No score grants automatic execution or bypasses owner approval.
- Public UI clearly identifies score as an evidence support index, never a correctness probability.
