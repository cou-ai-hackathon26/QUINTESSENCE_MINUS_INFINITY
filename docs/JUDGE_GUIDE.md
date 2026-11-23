# Shongoti evaluation navigation

Use the submitted commit SHA as the evaluation boundary. The root README contains the team and AI assistance disclosure. [Current verified scope and limits](READINESS_HANDOFF.md) distinguishes local observations, synthetic records, genuine provider calls and unavailable integrations.

1. Open the running app, switch to English if preferred, and choose **Judge workspace** on login. This creates a new isolated tenant with labeled sample opening records; its actions use the ordinary persistent API/inference paths. Register creates an empty merchant account.
2. Dashboard separates recorded liquid money, receivables and obligations. Reload verifies persistence. The floating voice bulletin refreshes real scoped records; unavailable data disables financial narration rather than inventing numbers.
3. Cases -> seeded supplier case -> agent investigation. Demand is 25000 BDT, applicable payment 4000 and accepted return 3000. Payment prior inclusion is unknown, so 18000/22000 alternatives remain until the missing fact is established. Four visible tasks contain three actual model calls and one exact calculation step; execution is sequential.
4. Evidence -> upload a new synthetic invoice/image/PDF. Inspect the original, extraction, uncertainty and actual provider receipt. Search combines actual local multilingual embeddings with keyword ranking when the pinned model is prepared; keyword-only fallback is disclosed.
5. Copilot -> upload/record a transaction. Old-debt collection and new credit sale are separate proposals. Posting requires the owner's explicit review; AI inference alone cannot transfer or post money.
6. Sales, people, money, buying, receiving, stock and planning retain their actual persistent workflows. The planner is a non-mutating scenario. Supplier credit acceptance is not an external transfer or automatically posted bill deduction.
7. Review [offline checks](evidence/readiness/AJ-03/final-checks.json), [genuine uploads/chat](evidence/readiness/AJ-03/live-checks.json), [agent/voice retry](evidence/readiness/AJ-03/live-remaining.json) and [browser observations](evidence/readiness/AJ-03/browser-checks.json). The first live pass's 429 is retained honestly; it is not a passing complete run.

Key implementation paths: `app/groq_provider.py` for real HTTP inference; `agents/real_orchestrator.py` for source-linked tasks; `retrieval/` for hybrid search; `domain/reconciliation.py` for payable alternatives; `domain/merchant_posting.py` and `api/v1/proposal_review.py` for guarded posting; `core/auth.py` and `core/permissions.py` for identity/roles. Backend paths are under `apps/api/app`.

No production deployment or public live/video link is supplied by this local repair checkpoint. The team must provide actual publicly accessible submission links and preserve the deadline commit. Do not treat a local address as a public deployment.
