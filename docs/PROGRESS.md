**Shongoti progress — evidence controls completion**

Current state: **Phase 00 and 01 complete and verified. Phase 02 tasks verified; milestone publication pending.**

| Phase | Name | State | Evidence / dependency |
|---|---|---|---|
| 00 | Repository and verified handoff | complete | Work verified; milestone `6c6d389`; see `evidence/phase-00/git-checkpoint.json` |
| 01 | Environment, contracts and executable skeleton | complete | Work verified; milestone `3808c0e`; see `evidence/phase-01/git-checkpoint.json` |
| 02 | Exact financial domain and golden cases | in_progress | All 34 domain tests pass; milestone publication pending |
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

**Next action:** continue Phase 02 with P02-T01 (exact financial domain).

**Next implementation task:** P02-T01 — implement money/currency/rounding, financial event and account types; separate available, pending, obligation, promise and scenario states.

**External unknowns:** model credentials/quota; payment sandbox/merchant access; hosting; optional OAuth/sender setup; repository public-release decision. See `INTEGRATIONS.md`. None are verified live.

**Session log**

- 22 November 2026: cloned an empty private repository, connected `origin`, prepared the build contract, agent instructions, curated references, golden fixtures and truthful phase tracking. No production application or live integration is claimed.
- 23 November 2026: Phase 01 completed and verified. Executable foundation, command contracts (typecheck, test:domain, test:api, test:web, db:migrate, build, verify:offline), API skeleton with health/readiness, and routed web shell implemented. Milestone `3808c0e` pushed to origin.

At each session end add: phase/task IDs, changed files, actual checks/evidence, unresolved blockers and the next exact task. Update `progress.json` at the same time. Completion must be tied to acceptance criteria, not hours spent or number of files.

**Mandatory phase publication:** each phase requires verified work, a milestone commit pushed to origin, and a published checkpoint receipt. Routine phase pushes to this repository already have user authorization. On every start, audit source/tests/evidence and actual Git state before trusting this tracker.

- Phase checkpoint policy update: mandatory tested commit/push and remote verification established. Phase 00 milestone `6c6d389` was pushed and its remote SHA was observed. Receipt publication is verified from actual branch state before handover.
