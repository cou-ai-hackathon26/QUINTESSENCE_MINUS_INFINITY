**Known gaps and blockers**

| ID | State | Gap | Required resolution |
|---|---|---|---|
| K001 | resolved | No application source/runtime yet | Resolved in Phases 01-10; complete FastAPI backend, PostgreSQL/SQLite schemas, and React/Vite frontend implemented and tested |
| K002 | open | No real merchant access or consented records | Keep fixtures synthetic; customer adoption and savings remain unvalidated in real world |
| K003 | open | No configured live AI key/quota | Test mock boundaries separately; live real provider calls blocked pending GEMINI_API_KEY |
| K004 | open | No payment live production credentials | Configured SSLCommerz sandbox connector lifecycle verified; production merchant credentials require merchant onboarding |
| K005 | resolved | No forecasting training/evaluation data | Resolved in Phase 09; implemented cold-start gating (<14 days) and rolling-origin backtest evaluation (>=14 days) per D007 |
| K006 | resolved | No browser layout/accessibility QA | Resolved in Phase 10; responsive 360/768/1440px layouts, focus indicators, and touch targets verified via test-e2e.js |
| K007 | open | No hosting/deployment and health observation | Configure actual runtime/storage, migrate and smoke-test deployed workflow (Phase 12) |
| K008 | open | Repository is private | User decides visibility before event/public submission requirements |
| K009 | open | Live event rules unavailable during research | Compare current organizer instructions with saved rulebook before submission |
| K010 | resolved | Reference notes contain historical names | Consolidated canonical plan, decisions, and progress tracking establish clear precedence |

Do not close an item solely because documentation was written. Link a concrete observation or test when resolving it.
