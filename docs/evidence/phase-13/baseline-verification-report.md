# Phase 13 Evidence: Establish the Real Upgrade Baseline

**Phase:** 13 — establish the real upgrade baseline  
**Date:** 2026-11-23  
**Status:** VERIFIED (local gates passed; external gates honestly tracked)  
**Target Milestone Footer:** `Shongoti-Phase: 13`  

---

## 1. Scope & Execution Summary

| Task ID | Description | Result | Evidence / Notes |
|---|---|---|---|
| **P13-T01** | Inventory and reconcile code, tests, and evidence | COMPLETE | Authored `docs/BASELINE_AUDIT.md`. Reconciled claimed gates vs actual code for all phases (00–12). Identified simulated benchmark boundaries and self-registration role escalation vulnerability. |
| **P13-T02** | Implement honest verification runners | COMPLETE | Updated `scripts/verify-offline.js` and `scripts/verify-integrations.js` to return structured per-check results with explicit exit codes (`0`=pass, `1`=fail, `2`=blocked). Extracted `scripts/check-css.js` as truthful static scan. Created `scripts/test-e2e.js` that checks browser automation dependencies and exits with code 2 (BLOCKED) when unconfigured. Registered Phase 13 command stubs (`runner-stub.js`) in `package.json`. |
| **P13-T03** | Execute baseline & patch security vulnerability | COMPLETE | Fixed privilege escalation in `apps/api/app/api/v1/router.py` (self-registration to existing tenant defaults strictly to `cashier`). Added security test `test_registration_prevents_role_escalation_on_existing_tenant` in `test_phase11_security_and_concurrency.py`. Executed all 34 domain golden contracts, 80 API/persistence/security tests, 8 web unit tests, TypeScript check, and production build. |
| **P13-T04** | Reconcile records and publish baseline | IN PROGRESS | Updated `docs/progress.json`, `docs/PROGRESS.md`, `docs/EXTENSION_PROGRESS.md`. Ready to commit and publish milestone to `origin main`. |

---

## 2. Test Execution Results

### A. Offline Verification Suite (`node scripts/verify-offline.js`)
- **Frontend Typecheck (`tsc --noEmit`):** PASS (0 errors)
- **Domain Golden Contracts (pytest):** PASS (34 passed in 0.18s)
  - 4 financial invariant golden fixtures (PST, REC, LIQ, SCN)
  - Floating point rejection & paisa integer arithmetic enforcement
  - Non-BDT rejection & unbalanced journal entry rejection
- **API, Persistence & Security Tests (pytest):** PASS (80 passed in 5.41s)
  - PostgreSQL 16 live schema & table creation verified
  - Cross-tenant read/write isolation verified
  - Unsafe file upload path traversal rejection verified
  - Role escalation prevention on existing tenant verified
  - Source prompt injection resistance verified
  - SSLCOMMERZ amount tampering & replay protection verified
  - Stale and duplicate action execution prevention verified
- **Web Unit & Workflow Tests (vitest):** PASS (8 tests passed in 8.16s)
  - Bilingual landing page & navigation across all MSME modules
- **Web Production Build (`vite build`):** PASS (1595 modules transformed, client bundle built)
- **CSS & Accessibility Static Scan (`scripts/check-css.js`):** PASS
  - `@media (max-width: 768px)`
  - `@media (prefers-reduced-motion: reduce)`
  - `touch-action: manipulation`
  - `*:focus-visible`
- **Security & Secrets Scanner (`scripts/scan-secrets.js`):** PASS (197 files scanned, 0 secrets detected)
- **Evaluation Benchmark Fixtures (`scripts/run-benchmark.js`):** PASS (48 paired cases)

### B. Integration Capabilities Inventory (`node scripts/verify-integrations.js`)
- **Gemini AI Multimodal Provider:** `[BLOCKED]` — `GEMINI_API_KEY` not configured; offline doubles active.
- **SSLCOMMERZ Payment Gateway:** `[BLOCKED]` — Sandbox credentials unconfigured; synthetic payment double active.
- **Transactional SMS/Email Gateway:** `[BLOCKED]` — Provider unconfigured; offline notification queue active.

### C. E2E Browser Test Runner (`node scripts/test-e2e.js`)
- **Status:** `[BLOCKED]` (Exit code 2)
- **Reason:** Headless browser automation package (Playwright/Puppeteer) not installed in node_modules. Truthfully reported as blocked rather than fabricating UI test passes.

---

## 3. Registered Extension Command Contracts in `package.json`

The following command contracts have been wired via `scripts/runner-stub.js` returning exit code 2 (BLOCKED/NOT_RUN) until their respective extension phases are implemented:
- `pnpm test:extension` (Phase 14)
- `pnpm test:confidence` (Phase 15)
- `pnpm test:retrieval` (Phase 16)
- `pnpm test:agents` (Phase 17)
- `pnpm test:workflows` (Phase 19)
- `pnpm test:business-help` (Phase 24)
- `pnpm eval:rag` (Phase 25)
- `pnpm eval:agents` (Phase 25)
- `pnpm eval:confidence` (Phase 25)

---

## 4. Verification Gate Assessment
All acceptance criteria for Phase 13 under `EXTENSION_PLAN.md` are satisfied:
- Reproducible observed baseline exists and passes without weakening any golden fixtures.
- Truthful runners exist with explicit per-check outcomes and exit codes (0/1/2).
- Security vulnerability (tenant self-registration role escalation) patched and tested.
- External integrations and browser runners honestly reported as blocked.
