# Final UI review — 23 November 2026

The locked landing was ported into the actual React application, followed by 20 connected authenticated workspaces, real credential auth, explicit judge entry, public invoice review and setup. Primary business pages use the same forest/paper/lime vocabulary; agent evidence and voice capture have their own task-focused layouts. The original backend and integer-paisa golden contracts remain the base.

## Observed verification

- `local-checks.json` and `api-checks.log`: 140 backend tests pass with isolated database fallback and provider keys disabled. The 34 original domain/golden contracts were not edited.
- `web-checks.log`: 29 frontend tests pass, including authentication failures, exact input and recorded-event ordering/deduplication. The final complete suite, including the additional account-availability regression, has 30 passing tests in `web-final-checks.log`. Some legacy component tests still emit React `act` and router future-flag warnings.
- `build-checks.log`: production build and TypeScript checks pass. Route code is split into independent chunks. The main JavaScript entry is about 239 KB / 79 KB gzip; the landing's authored content/styles load in separate chunks. These are build sizes, not measured production Core Web Vitals.
- `evidence/browser-report.json`: 20 routes × five widths (360/390/768/1024/1440), 25 screenshots, no document overflow or unnamed visible main buttons, actual registration, missing-amount failed-send preservation, recorded replay and invalid public invoice checks pass. Real-account checks ran against the refreshed API with current OpenAPI endpoints present.
- `evidence/accessibility-browser-report.json`: English navigation, source dialog keyboard containment, Escape/focus restoration, reduced-motion preference and mobile heading polish pass. A complete screen-reader or WCAG conformance audit is not claimed.
- `evidence/agent-replay-recording.html`: actual Chrome frame captures with recorded intervals, playable without external dependencies. The captured behavior is deliberately labeled synthetic judge replay, not live concurrent inference.
- Earlier UIR-02–08 evidence holds the scoped voice capture, financial clarification, transfer/collection, receiving, conditional scenario, inbox and public invoice checks. Browser fake-microphone evidence verifies recording/blob/review/failure boundaries, not actual STT quality.

## Why several old endpoint tests changed

The former payment tests treated local adapter-generated URLs and client `status=VALID` as a verified gateway transaction. The generic executor merely changed a database status to `completed`. Unconfigured image/audio parsing substituted deterministic sample content. A suspected supplier credit could be applied without recorded acceptance. These success paths contradict the product's existing evidence and authority rules.

Endpoint tests now require unavailable/unknown states and no money mutation for those unimplemented integrations; explicit adapter unit doubles remain distinct. Supplier credit exactly-once coverage first establishes synthetic supplier acceptance in its isolated fixture. Legacy reconciliation arithmetic still resolves to the original amount, but an action lacking a current persisted source case is blocked. No financial golden expectations were weakened.

The stock test module used the default `SessionLocal` rather than an isolated fixture. It now creates an in-memory database for every test. Before that repair, this task's failed legacy run created six synthetic `Stock Shop …` tenants in the default development database. Those exact six were identified by their names and creation timestamps. Restoration verified each had only the expected eight synthetic accounts and two synthetic users, with zero other tenant-owned records. Only these six tenants, 48 accounts and 12 users were removed transactionally; a restoration backup remains under ignored `tmp/`. Other pre-existing records were preserved. The database was not migrated or reset. Do not use the old test helper.

## Remaining limits

See `docs/UI_REDESIGN_HANDOFF.md` for capability boundaries. Real provider inference/evaluation, learned dense retrieval quality, live agent streaming, payment dispatch/server validation, current legal applicability, universal transaction idempotency, historical sale-cost completeness and real merchant adoption remain separate engineering/research gates. The UI makes their state visible; screenshots and passing local tests do not establish these capabilities.
