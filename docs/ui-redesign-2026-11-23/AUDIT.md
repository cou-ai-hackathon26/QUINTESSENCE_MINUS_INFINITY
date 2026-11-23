# UI redesign audit — 23 November 2026

Baseline `87ec050f6c852da7a12560e9fa2057a75382ff61` on the current application branch. Working tree was clean before this planning work. Origin observed: `https://github.com/sakibul-shovon/Shongoti.git`. No remote publication, application edit, migration, dependency install or live-provider call was performed for this plan.

Read the [full redesign proposal](../../FULL_UI_REDESIGN_PLAN.md). [source-audit.json](source-audit.json) records route declarations, currently unmounted features, API decorators and source hashes. Its 130-file snapshot is a revision inventory, not a claim that every file was exhaustively reviewed. It excludes private records/configuration and dependency trees. API entries are static declarations, not runtime/OpenAPI validation.

## Scope and principal anchors

All routed page sources and the eight extension UI components were inspected along with shared components/style/i18n and the relevant API/domain boundaries. Particular attention was given to the original reconciliation, confidence, agents, copilot, retrieval, provider ingestion and browser runner. Backend suites and actual application journeys were not run in this review.

| Finding | Source anchor | Evidence type |
|---|---|---|
| 14 existing page routes; no imports/mounts for8 new feature components | `apps/web/src/App.tsx`; inventory production-import scan | Static source |
| Repeated shell and blue/slate inline presentation | `pages/*.tsx`, `components/Navbar.tsx`, `Sidebar.tsx`, `src/index.css` | Static source, not screenshot |
| Utility-class styling without Tailwind stylesheet pipeline | `OperationsHub.tsx`, `BusinessHelpDesk.tsx`, web manifest/global CSS | Static source; exact rendered result not inspected |
| Login/onboarding local navigation rather than session/setup requests | `pages/LoginPage.tsx`, `OnboardingPage.tsx` | Static handler review |
| Seed balances and silent failure paths; unhandled quick actions | `pages/TodayDashboard.tsx` | Static source |
| Fixed reconciliation hypotheses and local posting-success toast | `pages/ReconciliationPage.tsx`, especially `handleApproveAction` | Static source |
| Mismatched collection, portal-link and callback URLs | `SalesPage.tsx`, `ConnectionsPage.tsx` vs `api/v1/merchant.py`, `actions_and_portal.py` | Static client/server comparison |
| Planner failed-save message claims local save | `pages/FuturePlannerPage.tsx` | Static catch handler |
| Synchronous run start and recorded history; fixed specialist summaries | `api/v1/agents.py:66`, `agents/orchestrator.py:67`, `:197`, `:230` | Static critical path; not proof all capabilities unavailable |
| Lexical embedding double fallback, not verified neural dense retrieval | `retrieval/engine.py:57`, `:171`, `:204` | Static source; no retrieval quality benchmark run |
| Default unstated payment amount and divergent confidence threshold | `copilot/engine.py:200`, `:262`; `CopilotChat.tsx:175` | Static source |
| Canonical strong85/critical cap59; presentation precedence issue | `confidence/policy.py:15`, `:16`; `ConfidenceBadge.tsx:54` onward | Static source |
| Real provider REST path now exists | `ingestion/adapters.py`, `generateContent` call | Static source only; supersedes older implementation-absence notes, not proof configured/live |
| E2E runner does not execute a journey after package detection | `scripts/test-e2e.js` | Entire runner inspected; not executed as browser evidence |
| Progress/integration prose retains older initial/reopened claims next to later completion reports | `docs/PROGRESS.md`, `EXTENSION_PROGRESS.md`, `INTEGRATIONS.md` | Documentation consistency gap; no tracker rewritten |

Older research statements that inference is entirely unimplemented must not be repeated as current facts: this revision has a provider request path. Conversely, its existence does not prove a successful live request, appropriate quality or customer readiness.

## Verification actually executed

| Command | Outcome | Limits |
|---|---|---|
| `pnpm --filter @shongoti/web test` and `... build` through PowerShell default resolution | Exit1, PowerShell script execution policy prevented `pnpm.ps1` | Environment invocation issue, not a test failure. No policy changed. |
| `pnpm.cmd --filter @shongoti/web test` | Exit0, 11 files /27 tests passed, Vitest2.1.9 | Existing component/JSDOM tests, not real browser/API/provider certification. Router future warnings; DemandTracker act warnings. |
| `pnpm.cmd --filter @shongoti/web build` | Exit0, TypeScript then Vite5.4.21 build;1595 modules | Compiles existing tree; does not prove routed feature reachability or data truthfulness. |
| Static Node inventory | Exit0;14 routes,8 unmounted features,98 API declarations,130 source hashes | Regex declaration/import inventory; must inspect actual DTOs/runtime before implementation. |

Production build output: `dist/index.html`0.85kB (gzip0.54); CSS1.45kB (gzip0.68); JS313.34kB (gzip85.24). These are build-reported transfer estimates, not field performance measurements. Build artifacts are generated/ignored; no source mutation from build was intended.

Not run: real browser render/responsive/motion/screen-reader checks, backend regression, real AI, neural retrieval evaluation, gateway, notifications delivery, deploy and merchant usability. Previous browser tooling initialization was unavailable; no current visual QA is claimed. No secrets or private user data were read for this audit.

## Locked visual reference

Landing worktree: `E:/mu idea/Shongoti-landing-preview`, branch `design/landing-preview`, commit `4edb747027b7ec0a980d3377209b43d05b840723`, `landing-preview/`. The standalone CSS/HTML/JS is the approved visual foundation. It is not mounted in current React LandingPage and must be ported deliberately. The older branch must not replace newer application history.

The referenced preview itself uses synthetic deterministic examples and illustrative agent roles. Neither its design approval nor its previous local tests establishes live backend/model behavior. Current approval request concerns the new full-product proposal only.
