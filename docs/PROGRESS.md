**Shongoti progress — evidence controls completion**

Current state: **Phase 00 work is verified; its newly mandatory GitHub checkpoint is pending. Application implementation has not started.**

| Phase | Name | State | Evidence / dependency |
|---|---|---|---|
| 00 | Repository and verified handoff | in_progress | Work verified; milestone and receipt publication pending |
| 01 | Environment, contracts and executable skeleton | not_started | Inspect environment, choose maintained versions, establish commands |
| 02 | Exact financial domain and golden cases | not_started | Requires 01 |
| 03 | Database, authentication and tenant isolation | not_started | Requires 01 and 02 |
| 04 | Evidence ingestion and real AI boundary | not_started | Requires 03; live calls may need a provider key |
| 05 | Supplier reconciliation and clarification | not_started | Requires 02, 03 and 04 |
| 06 | Connected daily merchant workflow | not_started | Requires 02 and 03 |
| 07 | Liquidity outlook and spending-impact scenarios | not_started | Requires 05 and 06 for integrated acceptance |
| 08 | Action center, customer portal and one real connector | not_started | Requires 03, 05, 06 and 07; provider access gate |
| 09 | Stock, supported forecasts and operating reports | not_started | Requires 06 and 07; statistical claims need evaluated history |
| 10 | Product UI, responsive/accessibility and failure states | not_started | Requires integrated feature paths; shell starts in 01 |
| 11 | Evaluation, security and complete validation | not_started | Relevant earlier phases complete or explicitly blocked |
| 12 | Deployment, release documentation and handover | not_started | Requires 11; actual hosting/access gates |

**Next action:** publish and verify the Phase 00 checkpoint under `GIT_CHECKPOINTS.md`. Then continue the next implementation task.

**Next implementation task:** P01-T01 — inspect tools and repository; record versions and runtime constraints; create the application command/dependency contracts before feature implementation.

**External unknowns:** model credentials/quota; payment sandbox/merchant access; hosting; optional OAuth/sender setup; repository public-release decision. See `INTEGRATIONS.md`. None are verified live.

**Session log**

- 22 November 2026: cloned an empty private repository, connected `origin`, prepared the build contract, agent instructions, curated references, golden fixtures and truthful phase tracking. No production application or live integration is claimed.

At each session end add: phase/task IDs, changed files, actual checks/evidence, unresolved blockers and the next exact task. Update `progress.json` at the same time. Completion must be tied to acceptance criteria, not hours spent or number of files.

**Mandatory phase publication:** each phase requires verified work, a milestone commit pushed to origin, and a published checkpoint receipt. Routine phase pushes to this repository already have user authorization. On every start, audit source/tests/evidence and actual Git state before trusting this tracker.
