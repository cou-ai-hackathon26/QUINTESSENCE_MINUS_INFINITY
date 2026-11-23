# Phase 18 Evidence: Copilot and Compound Voice Transaction Review

**Date:** 2026-11-23  
**Status:** PASSED & VERIFIED  
**Phase:** 18 — Copilot and Compound Voice Transaction Review  

---

## 1. Executive Summary
Phase 18 implements the scoped copilot and voice transaction review engine for Shongoti:
- **Scoped Conversation Persistence:** All copilot sessions and messages are strictly tenant-isolated (`copilot_sessions` and `copilot_messages` tables via Alembic migration `010_copilot_workspace`). Context switching preserves tenant boundary and entity focus.
- **Intent Router:**
  - `canonical_query`: Accurately queries live double-entry accounts (Account `asset:cash` and digital wallet `asset:wallet:bkash`/`nagad`) with 100/100 confidence score and explicit timestamped ledger citations.
  - `hybrid_retrieval`: Searches document chunks (supplier agreements, return policies) via `HybridRetriever`. Missing evidence caps the confidence score strictly at 59 (`band: limited`, `readiness: needs_clarification`) with an honest absence statement instead of fabricated hallucination.
  - `action_draft`: Previews action proposals (recipient, BDT amount, status `draft`) without direct ledger writes. Model text never serves as an authorization token; ledger changes require explicit owner/manager approval through the Action Center.
  - `scenario_simulation` & `agent_investigation`: Integrates what-if spending analysis and multi-agent coordination for complex disputes.
- **Compound Voice Parsing:**
  - Ingests real audio/voice notes via `AIModelAdapter` multimodal boundaries.
  - Decomposes compound merchant speech (e.g. debt collection vs new sale) into separate draft operations.
  - Detects ambiguous allocations and requests clarification rather than guessing financial amounts.
- **Accessible Bilingual Web UI:**
  - `CopilotChat.tsx` renders chat messages, inline `ConfidenceBadge`, citations drawer, draft action notice cards, and voice audio upload controls with Bengali/English bilingual support.

---

## 2. API Endpoints
- `POST /api/v1/copilot/sessions`: Creates an isolated session.
- `GET /api/v1/copilot/sessions`: Lists sessions for the tenant.
- `GET /api/v1/copilot/sessions/{session_id}`: Retrieves session details and message history.
- `POST /api/v1/copilot/sessions/{session_id}/messages`: Submits user query and receives routed sourced response.
- `POST /api/v1/copilot/sessions/{session_id}/voice`: Uploads audio file and receives transcribed compound drafts.

---

## 3. Test & Verification Results

### 3.1 Pytest Suite (`apps/api/tests/test_copilot.py`)
- `test_copilot_session_creation_and_cross_tenant_isolation`: PASSED
- `test_canonical_query_cash_balance`: PASSED (score 100, ledger account citation)
- `test_hybrid_retrieval_and_confidence_capping`: PASSED (capped at 59 when missing, >=70 when indexed)
- `test_action_draft_does_not_mutate_ledger`: PASSED (draft status created, ledger unmutated)
- `test_voice_compound_transaction_parsing`: PASSED (split collection + sale, draft actions created)

### 3.2 Vitest Web Suite (`apps/web/src/tests/CopilotChat.test.tsx`)
- `renders chat messages with confidence badge and action draft notices`: PASSED
- `triggers onSendMessage when user types and submits message`: PASSED

### 3.3 Full Offline Verification Gate
- Frontend Typecheck (`tsc --noEmit`): PASSED (0 errors)
- Domain Golden Contracts: 34/34 PASSED
- API, Persistence & Security Tests: 105/105 PASSED
- Web Unit & Workflow Tests: 15/15 PASSED
- Web Production Build (`vite build`): PASSED
- CSS & Accessibility Static Scan: PASSED
- Security & Secrets Scan: PASSED (243 files clean)
- Benchmark Fixtures: PASSED
