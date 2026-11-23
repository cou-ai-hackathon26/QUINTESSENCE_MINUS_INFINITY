**Verification protocol — claims require observations**

**Extension contract:** Phase 13–26 gates and new command interfaces are defined in [EXTENSION_PLAN.md](../EXTENSION_PLAN.md), especially D/F/G/H. Existing commands and earlier claimed results must be audited, not assumed absent or verified. `node scripts/validate-extension-handoff.cjs` validates documentation/tracker/fixture consistency only; it never passes application, model, browser, RAG or integration gates.

The initial handoff has documentation/fixture checks only. Application commands listed in `plan.md` must be implemented in Phase 01. No command is deemed to exist or pass merely because it is mentioned here.

**Evidence record contract**

Store sanitized structured reports under `docs/evidence/phase-XX/`. Each result must contain:

```json
{
  "task_id": "P02-T04",
  "check_id": "domain-golden-cases",
  "status": "not_run",
  "command": "pnpm test:domain",
  "working_directory": "repository root",
  "ran_at_utc": null,
  "code_revision": null,
  "working_tree_description": null,
  "mode": "offline",
  "exit_code": null,
  "summary": "Template only; no execution claimed.",
  "evidence_paths": [],
  "blocked_reason": null
}
```

Allowed result states: `passed`, `failed`, `blocked`, `not_run`. Populate real timestamps, commands, revisions/tree context and exit codes only after execution. If no Git commit exists, say `unborn` and record relevant file hashes or a working-tree description. Never copy a previous result across code changes as if it were freshly run. Redact tokens, personal/merchant data and credentials before saving logs or screenshots.

**Required behavior checks**

| Area | Minimum meaningful verification |
|---|---|
| Money | Paisa/exact decimal, currency rejection, rounding, no NaN/float balance drift |
| Ledger | Balanced postings, actual/promise distinction, transfer fee and old-debt collection behavior |
| Allocations | Partial capacity, receipt reuse, simultaneous requests and idempotent replay |
| Reconciliation | All original hypotheses; return acceptance; payment received versus prior inclusion; unknown/no/contradictory reply |
| Plans | Golden seven-day balances; reserve versus fund shortfall; method/time constraints; fee/settlement and stale-input behavior |
| Persistence | Fresh PostgreSQL migration, persist/reload and actual database transaction/race tests |
| Identity | Valid session, demo isolation, cross-tenant read/write denial and role restrictions |
| Ingestion | Real PDF/image/audio paths when claimed; source opening, correction, invalid/poor input and bounded failures |
| AI | Real call receipts plus field/gold comparison; independent single-model baseline and correct unknown handling |
| Actions | Exact recipient/amount/version, expiry, cancellation and unauthorized execution denial |
| Providers | Authentic configured sandbox lifecycle, validated response, duplicate/forged callback, amount/currency/merchant mismatch |
| Forecasts | No invoice/promise/actual duplication; cold-start gating; rolling historical evaluation for statistical claims |
| Browser | Actual critical journey, source review, changed-input scenario, error states and 360/768/1440px layouts |
| Release | Actual type checks, tests and production build; secrets/private-data scan; deployed smoke checks if deployed |

**Gate interpretation**

- Unit/mock tests prove the declared local behavior, not provider access or model quality.
- A test skipped for missing configuration leaves its acceptance gate unverified.
- A real provider request proves execution, not correctness; score the output against reviewed facts.
- A browser screenshot proves an observed rendering, not correct posting or data persistence.
- A known financial/execution invariant violation blocks release. Do not downgrade it to a cosmetic issue.
- A phase with a required blocked task remains blocked/partial. Independent work can continue when its own dependencies permit it.
- After relevant checks pass, do not repeat unrelated broad suites without a new change or unresolved concern.

**Completion evidence**

Each completed task links its result reports in `docs/progress.json`. Each completed phase has all required tasks complete, a verified published milestone and checkpoint receipt, and a human-readable summary in `PROGRESS.md`. Follow `GIT_CHECKPOINTS.md`; a local commit alone does not complete the phase. `KNOWN_ISSUES.md` and `INTEGRATIONS.md` must agree with the claimed scope. Local results must not be presented as deployed results.
