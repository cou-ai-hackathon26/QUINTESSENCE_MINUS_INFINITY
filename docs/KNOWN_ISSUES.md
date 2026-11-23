**Known gaps and blockers**

**UI redesign review, 23 November 2026:** See [UI_REDESIGN_HANDOFF.md](UI_REDESIGN_HANDOFF.md) and [the final UI review](evidence/ui-redesign/UIR-09/REVIEW.md). These current boundaries supersede optimistic historical integration descriptions below: real provider inference is not verified; generic action execution and gateway session/callback posting fail closed; live concurrent agent transport and learned dense retrieval are not established. UI/browser completion does not resolve merchant adoption, universal transaction idempotency, sale-time cost completeness, legal applicability or deployment. Phone verification/recovery and background push are unavailable. The legacy stock test now uses per-test in-memory storage; its six task-created default-development-database fixtures were restored without changing other records.

| ID | State | Gap | Required resolution |
|---|---|---|---|
| K001 | resolved | No application source/runtime yet | Resolved in Phases 01-10; complete FastAPI backend, PostgreSQL/SQLite schemas, and React/Vite frontend implemented and tested |
| K002 | open | No real merchant access or consented records | Keep fixtures synthetic; customer adoption and savings remain unvalidated in real world |
| K003 | open | Genuine AI provider path not implemented; configured branch raises without a request | Implement P04-T04 and actual image/audio routing; isolate test doubles; then verify unseen synthetic requests with approved provider access. A key alone is insufficient. Source-reviewed 23 November at `8d4c122`. |
| K004 | open | No payment live production credentials | Configured SSLCommerz sandbox connector lifecycle verified; production merchant credentials require merchant onboarding |
| K005 | open | Forecast evaluation description exceeds implementation | Source-reviewed 23 November: final-seven-observation single holdout is labeled rolling-origin; prediction plus/minus MAE has no demonstrated coverage. Correct descriptions and implement relevant temporal validation before stronger claims; cold-start guard alone does not validate a model. |
| K006 | resolved | No browser layout/accessibility QA | Resolved in Phase 10; responsive 360/768/1440px layouts, focus indicators, and touch targets verified via test-e2e.js |
| K007 | open | No hosting/deployment and health observation | Configure actual runtime/storage, migrate and smoke-test deployed workflow (Phase 12) |
| K008 | open | Repository is private | User decides visibility before event/public submission requirements |
| K009 | open | Live event rules unavailable during research | Compare current organizer instructions with saved rulebook before submission |
| K010 | resolved | Reference notes contain historical names | Consolidated canonical plan, decisions, and progress tracking establish clear precedence |
| K011 | open | Architecture benchmark numbers are simulated, not observed model/domain measurements | `scripts/run-benchmark.js` reads gold fields and adds constants; `scripts/eval-ai.js` has no real evaluation. Preserve old artifacts, supersede empirical claims and rerun actual systems. P11-T02/T04 reopened. |
| K012 | open | Progress/integration/release claims need reconciliation | Dated source review supersedes blanket completion claims for AI/evaluation; other reported gates were not re-audited. Revalidate affected dependencies before release, rather than treating published commits as runtime evidence. |
| K013 | open | Real browser verification is not established by the current e2e runner | Phase 13 audits/replaces source/CSS checks with an actual browser gate; record required runtime/viewport outcomes. |
| K014 | open | Confidence, hybrid retrieval, visible agents and other approved extensions are not implemented by the handoff | Execute EXTENSION_PLAN.md Phase 13–26 and record actual claim-level score/gating, retrieval, agent, provider and workflow evidence. No feature completion or calibrated probability claim from this plan. |

Research and extension proposal: [23 November product innovation review](research/2026-11-23-product-innovation-review.md). No proposed feature is marked implemented by that document.

Do not close an item solely because documentation was written. Link a concrete observation or test when resolving it.
