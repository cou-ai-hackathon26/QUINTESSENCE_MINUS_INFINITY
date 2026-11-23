# Shongoti — product workbench design review

**Local review build, 23 November 2026.** Isolated worktree/branch: `Shongoti-product-preview` / `design/product-preview`, based on application commit `87ec050`. Main application source, its database, dependencies and original phase trackers were not changed.

Open **http://127.0.0.1:4318/#/login**. Select **এক ক্লিকে Judge workspace** / **Open judge workspace in one click**. No password or setup is needed for the judge entry. A fresh server-issued judge session opens six predefined synthetic scenarios.

```powershell
node product-preview/server.mjs
```

Keep this process running while reviewing. The default loopback port is4318; `SHONGOTI_PRODUCT_PORT` can select another free port. No package installation is needed to serve the design. Optional Google Fonts have Bengali/system fallbacks.

## What changed after feedback

The first card-heavy direction was replaced with a work queue, a persistent contextual agent panel, a source-document review workspace and a purchasing comparison table. The locked landing's paper/forest/lime identity remains. Read [research and decisions](RESEARCH_V2.md).

Four core screens:

- **Overview:** financial summary, actionable review queue, cashflow chart, account-mix chart and visible agent work.
- **Agent workspace:** switch source documents, inspect task receipts, play/pause a bounded example workflow, answer an inclusion question, inspect support and review a draft.
- **Purchasing:** compare normalized quotes, select supplier/quantity, inspect original terms, see exact totals and open the related cash scenario.
- **Cash planning:** modify spending/conditional collection, inspect baseline vs alternative and their exact daily values. Actual funds remain separate.

Additional entry screens: Login, Register, Judge scenario library. Global local-example Copilot, actionable inbox, source dialogs, opt-in device voice brief and motion preference are available in the judge workspace.

Six predefined scenarios:

| Scenario | Interaction / outcome |
|---|---|
| Supplier prior payment inclusion | Unknown critical fact retains22,000/18,000 alternatives; clarification selects the supported example balance; no payment is executed. |
| Purchase cash impact | Change spend/promise assumptions; view reserve/shortfall and date/value table. |
| Conditional6+1 quotation | Bonus excluded until eligibility is known; unit/quantity/shipping change deterministic totals. |
| Partial/damaged receiving | Inspect ordered10/received8/damaged1/usable7; pending credit does not reduce payable. This exception inspector is a fixed fixture, not a stock-writing feature. |
| Duplicate payment | Inspect original reference/blocked duplicate outcome. This is a fixed fixture, not an actual gateway test. |
| Unverified notice deadline | Inspect missing source date/jurisdiction and abstention. This is not substantive legal advice or a verified legal corpus. |

The last three are predefined **inspection scenarios**, not production workflows. This library covers this design review's capabilities; it does not claim all Phase00–26 features are integrated into the new UI.

## Authentication: real local verification, bounded scope

Registration/login are verified by the local Node server, not by navigating after an arbitrary password. Accounts use random salts and scrypt (`N=16384,r=8,p=5`); earlier local test hashes upgrade after successful login. Session IDs are random, stored hashed server-side, expire after12hours, use HttpOnly/SameSite Strict cookies and are revoked on logout/replacement. Mutating auth requests require the exact loopback origin and JSON; basic rate limits and body bounds apply.

Accounts persist privately in ignored `product-preview/.runtime/accounts.json`. Sessions are memory-only and end on server restart. Never commit the `.runtime` directory or its Chrome profiles. Registration creates a distinct merchant identity; **no synthetic judge balances are shown as that merchant's actual records**. A normal account currently has an explicit empty/unconnected merchant workspace.

This is not the application's production authentication. Phone ownership is unverified; there is no SMS, password recovery or deployed TLS. The local server is bound to127.0.0.1. Do not deploy this account store as a public identity service. The approved full product should integrate registration/session flows with the existing FastAPI user/tenant/role model and its migration/testing requirements, rather than keep a second financial identity store.

Judge reset creates a new synthetic principal and revokes the previous session. Fixture state is browser-session-local; no real merchant data is loaded. External messages, money movement and posting are absent.

## Agent/AI truthfulness

The agent view is an **explicit synthetic workflow playback**. Its pacing/loading/paused/waiting/completed states make the interaction reviewable, but it performs no real model calls. Role cards and source text are fixtures; exact arithmetic executes locally in `domain.js`. Copilot's small set of example answers is labeled local/deterministic. Neither is a verified production multi-agent or RAG integration.

No AI-provider secret was provided or used. The original backend's real inference adapter and existing domain services have not been wired into this local design build. That integration remains a separate implementation/verification task after design approval. Do not relabel playback as live inference when porting to React.

## Checks and evidence

```powershell
node --test product-preview/preview.test.mjs product-preview/auth.test.mjs
node product-preview/http-check.mjs
node product-preview/browser-check.mjs
```

Component tests resolve existing JSDOM from this checkout's web dependencies, or the sibling main checkout when using a Git worktree. Browser checks use installed Chrome in a separate headless test profile; they do not use existing tabs. They verify actual rendered layouts at360/768/1440px, judge entry, register/login/rejected password, source/question transitions, replay states and English/reduced-motion behavior. `browser-report.json` records code hashes, errors and screenshots. HTTP tests operate only on synthetic sessions and do not print tokens.

See [evidence](evidence/) and [progress](progress.json). Browser tests are not real AI, legal, payment, screen-reader, merchant-usability or full backend certification. No UIR-00–09 phase is marked complete by this prototype checkpoint.

## Resume after review

Preserve this branch and the approved landing reference. Collect concrete screen feedback. On approval, port selected components into the latest React app in the full-redesign worktree under `FULL_UI_REDESIGN_PLAN.md`; inspect its current source/contracts again. Reuse canonical domain/services, not this preview's local auth/financial fixtures, for production. Preserve main/Antigravity changes and use normal phase checkpoints. Do not merge the older landing branch wholesale.
