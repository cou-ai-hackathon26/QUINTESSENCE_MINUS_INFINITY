# Real merchant workflow handoff

23 November 2026. Read this before relying on older Phase 00–26/UI reports. The approved interface is preserved; the fixture-only execution path has been removed. The current repair tracker is `docs/real-workflow-progress.json` and the contract is `docs/REAL_WORKFLOW_PLAN.md`.

## What actually works

- Judge entry creates a fresh isolated merchant tenant with explicitly sample starting records. Judge and registered merchant accounts use the same database/API/inference paths. Refresh restores persisted work. Register/password sign-in are real; the legacy shared demo/OTP test endpoints are disabled by default.
- New text, images, native/scanned PDFs and audio go to actual configured Groq inference. Original private sources remain downloadable. Extraction errors preserve the source and unknown values. Retry reuses the original source ID; human-reviewed claims cannot be overwritten.
- Copilot answers from current tenant records and retrieved documents, stores citations, typed proposals and actual provider receipts. Whisper separates old-debt collection from a new credit sale. No inference directly posts money.
- The agent investigation returns HTTP 202, persists queued/running/finished tasks, and exposes actual polled progress. An evidence-reader model, deterministic reconciliation tool, independent skeptic model and report model execute sequentially. Three genuine model calls have separate receipts. Facts/quotes/payable alternatives are validated; cancellation, budgets and stale case versions are checked. The visual replay is explicitly replay.
- Real local multilingual E5 embeddings combine with Unicode-aware BM25 and RRF. Exact invoice identity retains priority; tenant/revoked-source filtering precedes ranking. Official artifact revision and checksum are recorded. Missing model means disclosed keyword-only search, never hash vectors presented as semantic inference.
- A voice/chat proposal opens an explicit review page. Supported internal bookkeeping records require party/account/amount verification and owner confirmation. A unique source-operation key prevents recording that same interpretation twice. Balanced integer-paisa postings and actual due/balance guards are enforced in code.
- Ordinary sale, collection, transfer, expense, owner draw and supplier-payment records have atomic guarded posting and retry-safe keys. The review dialog keeps the same key for retries of that pending request. A new key means a new event. Missing/foreign parties, oversold stock, duplicate stock-line overuse, over-collection and unfunded outflows are rejected without partial writes. Opening customer/supplier dues now also create balanced opening-ledger entries.
- Delivery intake adds only usable units to a registered SKU and uses retry keys. Supplier acceptance requires an original private source plus explicit owner review, stored in an audit record. Accepted credit and prior bill deduction remain distinct. Applying a credit stores the owner's bill-reference tracking record exactly once; it does **not** automatically adjust the payable ledger or transfer cash. A complete bill-linked credit posting workflow is still a separate gap.
- Generated customer invoice links read actual scoped records and persist review/dispute notes. Actual exports, daily briefs and internal notifications remain available. Connections reports configured/observed/unavailable capability states instead of assuming every provider exists.

## Run the current local app

From the repository root, use the existing ignored local `.env`; do not print it or request keys in chat. The supplied Groq key is configured locally, never committed. Another machine needs its own valid secret.

```powershell
pnpm.cmd install --frozen-lockfile
uv pip install --python apps/api/.venv/Scripts/python.exe -e apps/api
pnpm.cmd db:migrate
node scripts/run-python.js scripts/setup-semantic-model.py
pnpm.cmd dev
```

The install command assumes the documented Python 3.12 virtual environment already exists. For a fresh machine create it with `uv venv --python 3.12 apps/api/.venv` first. Node/pnpm and uv are runtime prerequisites. Semantic preparation downloads the official model into ignored local data; it must finish once before `SEMANTIC_ENABLED=true`. The app never downloads weights during a user request.

The frontend is `http://127.0.0.1:5173`; the API is `http://127.0.0.1:8000`. Keep the API working directory at the repository root so relative `.env`, storage and SQLite paths agree. This machine uses a new migrated `apps/api/data/shongoti_app.db`; previous development databases are preserved. The running app needs actual outbound provider access and quota; a restricted-shell connection failure is not successful inference. Restart the owned API process after backend/settings changes. Do not reset another developer's database or overwrite `docs/DATABASE_SETUP.md`.

Relevant non-secret settings are in `.env.example`: `AI_PROVIDER=groq`, provider model IDs, timeout/output limits, `SEMANTIC_ENABLED`, and `SEMANTIC_MODEL_PATH`. Keep `ALLOW_LEGACY_TEST_AUTH=false`. Offline pytest explicitly disables real inference and enables only its isolated legacy identity fixtures; that is not the runtime authentication policy.

## Evidence and checks

- `docs/evidence/real-workflow/JR-01/`: persistent Judge/API repair.
- `docs/evidence/real-workflow/JR-02/`: genuine unseen text/image/PDF/audio/chat requests and browser evidence.
- `docs/evidence/real-workflow/JR-03/`: pinned encoder, actual semantic probes, genuine specialist requests, failed initial quality observation, corrected fact contracts, reviewed-posting/race tests and browser evidence.
- `docs/evidence/real-workflow/JR-04/`: final daily-workflow/security checks, receipt retry, credit review, actual portal/registration and 21 routes at three viewport widths.

```powershell
node scripts/run-python.js -m pytest apps/api/tests/ -q -p no:cacheprovider
pnpm.cmd test:web
pnpm.cmd build
node scripts/check-real-workflows-browser.mjs
```

The browser script requires installed Windows Chrome, this local app and genuine inference quota; it creates only synthetic test tenants and sources. Paid provider checks are separate from offline test doubles. Git milestone and receipt files identify the published revision for each verified scope. No static preview, historical mock report or successful-looking button proves a live provider.

The old `eval:agents`, `eval:rag`, `eval:confidence`, `test:workflows` and `eval:ai` runners previously printed simulated or misleading results. They now execute actual isolated contract tests and propagate failure. `eval:agents --live`, `eval:rag --live` and `eval:ai --live` invoke the separate genuine app/model probes. They are smoke checks, not comparative benchmarks. `run-benchmark.js` now reports NOT_RUN and exits nonzero rather than fabricating architecture scores. `verify:integrations` inventories configuration without displaying secrets or claiming provider verification; its strict mode remains nonzero while external integrations are unavailable.

## Remaining boundaries and next work

The owner explicitly deferred payment setup on 23 November: no sandbox account is available; finish other work first. Therefore JR-04 publishes verified local scope, **not** a claim that external integrations are complete.

1. Online payments: real SSLCOMMERZ session creation, durable payment attempts, public HTTPS callbacks, server-to-server Order Validation, transaction/merchant/amount/currency/risk matching and exactly-once pending-settlement postings still need implementation and genuine sandbox verification. The previous generated checkout URL and callback-only validation have been removed. Existing payment endpoints fail closed. Credentials alone will not complete this work. Approved sandbox fields are `SSLCOMMERZ_STORE_ID`, `SSLCOMMERZ_STORE_PASSWD` and a chosen public HTTPS callback origin; store secrets only locally. Production payments are outside the current verified scope.
2. SMS/WhatsApp delivery and phone verification/recovery: no verified sender/account/receipts are configured. Reminder drafts are real stored drafts; they are not sent messages. Select the exact permitted provider/use case before asking for its credentials.
3. Bangla spoken playback: Groq Whisper handles transcription; Groq Bangla TTS is not established. Browser playback requires an installed matching-language voice. A cloud Bangla TTS provider and actual playback verification are separate work. English synthetic speech tests do not certify Bangla recognition quality.
4. Deployment: this is a verified local app, not a qualified production deployment. Durable background jobs, crash recovery, production PostgreSQL concurrency/storage/backup, quotas/abuse controls and live health observation remain. In-process agent tasks are not a durable queue. SQLite race tests do not certify PostgreSQL deployment behavior.
5. Financial/product gaps: bill-linked credit posting, sale-time historical item costs, comprehensive purchase/inventory accounting and remaining import/operations mutation concurrency need their own contracts and checks. Offer arithmetic now uses exact decimal discount rounding and required-account capacity, but does not certify negotiated credit eligibility. An optimistic draft is never permission to pay.
6. Grounding/validation: retrieval threshold and evidence-support index are explicitly uncalibrated product policies. Model prose may still be wrong despite schema/fact checks. Legal references need a reviewed current jurisdiction-scoped corpus. Real-user adoption, Bengali audio quality, forecast accuracy and savings remain unvalidated without applicable data.

Resume the next unblocked item from source/tests/evidence. Preserve original financial golden contracts, the approved UI and published history. Do not restart the app as a new project, silently restore fixture interception, infer missing provider access, or mark these external gates complete from code inspection.
