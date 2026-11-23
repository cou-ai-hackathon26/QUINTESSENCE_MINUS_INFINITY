# Phase 17 Evidence: Bounded Multi-Agent Collaboration and Visible Teamwork

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 17 — Bounded Collaboration & Visible Teamwork  

---

## 1. Executive Summary
Phase 17 delivers bounded multi-agent collaboration and transparent specialist execution for Shongoti:
- **Strict Role Specialization:** Four distinct agent roles operating under bounded tasks:
  1. `Coordinator`: Drafts the investigation plan, checks complexity, dispatches specialists, or resolves simple queries directly without spawning heavy agents.
  2. `TermsEvidenceSpecialist`: Executes hybrid search against document chunks, supplier agreements, and invoice records, returning citation counts and evidence packs.
  3. `ReconciliationSpecialist`: Evaluates canonical payable hypotheses (REC 001–004) against double-entry ledger state.
  4. `SkepticSpecialist`: Independently audits candidate claims for conflicts, unverified receipts, or duplicate credit allocations without inheriting the proposer's confirmation bias.
- **Strict Call & Financial Budgeting:** Configurable call budgets (`budget_calls_max`, default 8). Halts execution with explicit reason `budget_exhausted` when limits are reached, preventing infinite loops and runaway inference costs.
- **Tenant Isolation:** All runs, tasks, and audit events are strictly bound to `tenant_id`. Cross-tenant reads and cancellations return HTTP 404.
- **Visible Timeline & Bilingual UI:** React component `AgentTimeline.tsx` renders real-time execution states, Bengali numerals for budgets, role icons, skeptic alerts, tool receipts, and an explicit cancellation control.

---

## 2. API Endpoints
- `POST /api/v1/agents/runs`: Starts an investigation run with `case_type`, `case_id`, `query`, and `budget_max`.
- `GET /api/v1/agents/runs/{run_id}`: Retrieves run status, budget used/max, and full list of tasks.
- `GET /api/v1/agents/runs/{run_id}/events`: Ordered timeline of granular lifecycle events (`plan_created`, `tool_receipt`, `skeptic_critique`, etc.).
- `POST /api/v1/agents/runs/{run_id}/cancel`: Safely cancels an active investigation.

---

## 3. Test & Verification Results

### 3.1 Pytest Suite (`apps/api/tests/test_agents.py`)
- `test_compound_case_multi_specialist_collaboration`: PASSED
- `test_simple_query_optimization_skips_unnecessary_specialists`: PASSED
- `test_budget_exhaustion_halts_execution`: PASSED
- `test_run_cancellation`: PASSED
- `test_cross_tenant_isolation`: PASSED

### 3.2 Vitest Web Suite (`apps/web/src/tests/AgentTimeline.test.tsx`)
- `renders agent collaboration timeline with coordinator plan and budget`: PASSED (Bengali numerals "৪ / ৮", role cards, skeptic warning)
- `renders cancel button when running and invokes onCancel callback`: PASSED

### 3.3 Full Offline Verification Gate
- Frontend Typecheck (`tsc --noEmit`): PASSED (0 errors)
- Domain Golden Contracts: 34/34 PASSED
- API, Persistence & Security Tests: 100/100 PASSED
- Web Unit & Workflow Tests: 13/13 PASSED
- Web Production Build (`vite build`): PASSED
- CSS & Accessibility Static Scan: PASSED
- Security & Secrets Scan: PASSED (235 files clean)
- Benchmark Fixtures: PASSED
