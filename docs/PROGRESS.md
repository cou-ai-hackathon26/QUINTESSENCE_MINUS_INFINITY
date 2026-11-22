**Shongoti progress — evidence controls completion**

Current state: **Phase 00, 01, 02, 03, 06 complete and verified. Phase 04 partially implemented and blocked on live AI key. Phase 07 verified; checkpoint pending.**

| Phase | Name | State | Evidence / dependency |
|---|---|---|---|
| 00 | Repository and verified handoff | complete | Work verified; milestone `6c6d389`; see `evidence/phase-00/git-checkpoint.json` |
| 01 | Environment, contracts and executable skeleton | complete | Work verified; milestone `3808c0e`; see `evidence/phase-01/git-checkpoint.json` |
| 02 | Exact financial domain and golden cases | complete | Work verified; milestone `8b34a32`; see `evidence/phase-02/git-checkpoint.json` |
| 03 | Database, authentication and tenant isolation | complete | Work verified; milestone `0c9cada`; see `evidence/phase-03/git-checkpoint.json` |
| 04 | Evidence ingestion and real AI boundary | blocked | P04-T01..T03 verified; milestone `8e15789`; P04-T04 blocked pending GEMINI_API_KEY |
| 05 | Supplier reconciliation and clarification | blocked | Blocked on Phase 04 completion (live AI provider gate) |
| 06 | Connected daily merchant workflow | complete | Work verified; milestone `af708cb`; see `evidence/phase-06/git-checkpoint.json` |
| 07 | Liquidity outlook and spending-impact scenarios | in_progress | All 4 tasks verified offline; checkpoint publication pending |
| 08 | Action center, customer portal and one real connector | not_started | Requires 03, 05, 06 and 07; provider access gate |
| 09 | Stock, supported forecasts and operating reports | not_started | Requires 06 and 07; statistical claims need evaluated history |
| 10 | Product UI, responsive/accessibility and failure states | not_started | Requires integrated feature paths; shell starts in 01 |
| 11 | Evaluation, security and complete validation | not_started | Relevant earlier phases complete or explicitly blocked |
| 12 | Deployment, release documentation and handover | not_started | Requires 11; actual hosting/access gates |

**Next action:** publish Phase 07 milestone and checkpoint receipt, then proceed with Phase 08.

**Next implementation task:** Phase 08 — Action center, customer portal and real connector.

**External unknowns:** model credentials/quota; payment sandbox/merchant access; hosting; optional OAuth/sender setup; repository public-release decision. See `INTEGRATIONS.md`. None are verified live.

**Session log**

- 22 November 2026: cloned an empty private repository, connected `origin`, prepared the build contract, agent instructions, curated references, golden fixtures and truthful phase tracking. No production application or live integration is claimed.
- 23 November 2026: Phase 01 completed and verified. Executable foundation, command contracts (typecheck, test:domain, test:api, test:web, db:migrate, build, verify:offline), API skeleton with health/readiness, and routed web shell implemented. Milestone `3808c0e` pushed to origin.
- 23 November 2026: Phase 02 completed and verified. Exact financial domain: Money integer paisa primitive, balanced journal entries, capacity allocation, 4 supplier reconciliation hypotheses, liquidity channels, 7-day spending impact scenarios, and all 34 golden contract tests passing. Milestone `8b34a32` pushed to origin.
- 23 November 2026: Phase 03 completed and verified. Database schema, Alembic migration 001_initial_schema, live PostgreSQL 16 verification, JWT authentication with HMAC-SHA256, demo tenancy isolation, and role-based permissions enforced. Milestone `0c9cada` pushed to origin.
- 23 November 2026: Phase 04 partially implemented and verified. Tenant-isolated evidence storage, SHA-256 validation, native PDF extraction, structured claim schemas, human review/correction endpoints, and migration 002_evidence_schema completed. Task P04-T04 recorded as blocked pending live GEMINI_API_KEY.
- 23 November 2026: Phase 06 completed and verified. Connected daily merchant workflow: DailySnapshotModel, PartyModel, ProductItemModel, StockMovementModel, migration 003_merchant_workflow, cash/credit/split sales, debt collection (zero revenue inflation), wallet transfers with fees, stock deductions, cash close discrepancies, operating expenses, owner withdrawals with RBAC, supplier payments, and live TodayDashboard connected to /api/v1/merchant/today. All 24 API tests and offline gates passed.
- 23 November 2026: Phase 07 completed and verified. Liquidity outlook & decision lab: ScenarioModel, migration 004_scenarios_schema, ScenarioEngine wired to /api/v1/scenarios (simulate, save, list, baseline), FuturePlannerPage bilingual UI decision lab, verified non-mutation of actual books, Day 3 reserve breach and Day 5 cash shortfall alerts. All 29 API tests and offline gates passed.

At each session end add: phase/task IDs, changed files, actual checks/evidence, unresolved blockers and the next exact task. Update `progress.json` at the same time. Completion must be tied to acceptance criteria, not hours spent or number of files.

**Mandatory phase publication:** each phase requires verified work, a milestone commit pushed to origin, and a published checkpoint receipt. Routine phase pushes to this repository already have user authorization. On every start, audit source/tests/evidence and actual Git state before trusting this tracker.

- Phase checkpoint policy update: mandatory tested commit/push and remote verification established. Phase 00 milestone `6c6d389` was pushed and its remote SHA was observed. Receipt publication is verified from actual branch state before handover.
