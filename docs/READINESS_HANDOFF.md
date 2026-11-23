# Current readiness handoff - 24 November 2026

Preserve the approved UI and existing database. Current repair tracker: [repair-progress.json](repair-progress.json). Earlier phase reports remain dated evidence, not current runtime/provider guarantees.

Verified in this repair pass:

- Final offline regression: **188 backend tests, 39 frontend tests, production frontend build and targeted tracked secret scan passed**. Logs: [AJ-03](evidence/readiness/AJ-03/final-checks.json).
- Actual new synthetic image, native PDF and scanned PDF returned the exact 51929-paisa amount; original private bytes remained downloadable. Actual grounded chat returned citations and provider receipts.
- Actual sequential investigation completed all four tasks with three model receipts; unresolved prior inclusion correctly leaves the run waiting for owner input. The first attempt hit Groq HTTP 429 at the report call; the bounded retry passed. Both observations are retained.
- Actual Whisper separated old-debt collection and a new credit sale without changing the ledger. Actual authenticated English online speech returned 26352 audio bytes. These synthetic checks do not certify general Bangla recognition/voice quality.
- Actual browser checks passed Judge login/reload, scoped voice brief/loading and explicit network-failure behavior, plus 18 additional routes at 360/768/1440 without runtime errors or document overflow.
- Dependency lock audits found no known advisories at check time. This is not an exhaustive security audit. Current auth checks, quota bounds, private speech and exact/atomic CSV are covered by regression tests.

The application retains the same owner-reviewed financial workflows and UI. Intended failure-path changes: invalid CSV batches reject atomically, unsupported critical financial claims reject rather than appear grounded, cashiers cannot confirm financial claims, private speech requires login/POST, and unavailable brief data never becomes invented money or an all-clear.

Use Python 3.12 and Node 24. Install the complete `apps/api/requirements.lock`, then `--no-deps -e apps/api`; JavaScript uses the frozen pnpm lock. `uv pip check` passed after removing only orphaned package metadata left by an interrupted Windows update. Runtime database/inference libraries not requiring security replacement were kept at tested versions.

Production settings reject default/short signing keys and legacy test auth. Configure `SECRET_KEY`, `POSTGRES_PASSWORD`, `ALLOWED_ORIGINS`, `ALLOWED_HOSTS` and the explicit durable evidence/model/cache paths before deployment. Docker uses the same lock and root Alembic path, one API worker and private database network. No actual image deployment is certified: this host has no available Docker daemon.

Limits that remain:

- Per-process admission is intentionally for the documented one-worker deployment. Daily receipt counting is not a distributed atomic billing/quotas service; in-flight requests can overlap. Durable jobs, crash recovery and production PostgreSQL/storage/restart qualification remain separate work.
- Monetary-mention/citation/quote checks reduce known failures; they are not complete semantic entailment or a guarantee that prose is correct. Evidence support remains an uncalibrated policy index. Large held-out/ablation benchmarks were not run in this urgent repair pass.
- Financial imports retain the existing explicit absolute stock-count update behavior. Complex inventory reconciliation, import races/versioning, historical sale costs and bill-linked credit ledger posting remain existing domain follow-ups.
- Payments and message dispatch remain unavailable and owner-deferred. Pricing is a proposed commercial presentation, not verified subscriptions/entitlements. Legal corpus applicability, adoption, savings and forecast quality remain unvalidated.
- A new GitHub Actions workflow uses empty provider secrets and an ephemeral PostgreSQL 16 service. Its first remote run exposed missing service/provider-test configuration; that setup was corrected without disabling assertions. Check the actual remote run independently of local passes.

Runtime model clients: Groq text/vision/Whisper, pinned local multilingual E5 through FastEmbed/ONNX, and third-party `edge-tts` for the bulletin. Groq/Edge outages leave explicit errors/transcripts; no fixture output is substituted. Never commit `.env`, provider tokens or private merchant files.

Resume by checking Git and [REPAIR_PROGRESS.md](REPAIR_PROGRESS.md). Use only new synthetic Judge tenants for smoke tests; do not reset existing accounts or repeatedly replay financial mutations.
