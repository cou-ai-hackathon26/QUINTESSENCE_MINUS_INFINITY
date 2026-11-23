# Shongoti — full product UI redesign

**Prepared: 23 November 2026 · Asia/Dhaka**  
**Status: EXECUTION AUTHORIZED on 23 November 2026. The owner requested merging the preview into main, then completing the remaining UI there, with agentic features and AI voice chat emphasized.**  
Source baseline: `87ec050f6c852da7a12560e9fa2057a75382ff61`. See [audit and verification](docs/ui-redesign-2026-11-23/AUDIT.md) and the [source inventory](docs/ui-redesign-2026-11-23/source-audit.json).

## 1. সহজে সিদ্ধান্তটা

Landing-এর পছন্দ করা **cream–forest green–lime** design-ই থাকবে। Login-এর পরে সেই পরিচয়ে একটি **ব্যবসার কাজের টেবিল** বানাব: আজ কী করতে হবে, কোন টাকা বাস্তবে আছে, কোন সিদ্ধান্ত আটকে আছে এবং সংগতি কোন প্রমাণ নিয়ে কাজ করছে—একসঙ্গে বোঝা যাবে।

সব screen-কে একই রকম card-এর dashboard বানাব না। বিক্রি হবে দ্রুত entry screen, ক্রয় হবে comparison desk, হিসাবের বিরোধ হবে evidence workspace, আর ভবিষ্যৎ পরিকল্পনা হবে baseline ও বিকল্পের তুলনা। AI-এর কাজ দেখাব প্রমাণ থেকে প্রশ্ন, যাচাই এবং সিদ্ধান্তে যাওয়ার মাধ্যমে। Animation এই পরিবর্তন বুঝতে সাহায্য করবে।

তিনটি প্রধান দৃশ্য:

1. **আজকের দোকান:** জরুরি কাজ, বাস্তব টাকা, দ্রুত বিক্রি/আদায়/বিল যোগ এবং ছোট agent activity strip।
2. **সংগতির তদন্ত:** বিলের নির্দিষ্ট অংশ → সংশ্লিষ্ট দাবি → specialist-এর কাজ → আটকে থাকা প্রশ্ন → মালিকের review।
3. **এই সিদ্ধান্ত নিলে:** আজকের খরচ বা ক্রয়ের কারণে আগামী দিনের নগদ অবস্থার পরিবর্তন, পাশে কারণ ও শর্ত।

এই plan-এ **১০টি implementation phase: UIR-00–UIR-09**। পুরোনো Phase 00–26 বা তাদের completion ইতিহাস বদলানো হবে না। প্রথমে foundation এবং তিনটি representative screen যাচাই; তারপর বাকি product-এ rollout। সম্পূর্ণ redesign approval-এর পরে শুরু হবে।

## 2. Execution contract for the implementing agent

1. Read `AGENTS.md`, `plan.md` financial rules, `EXTENSION_PLAN.md` sections on confidence/provenance/actions, current progress and this document. User instructions have priority. This is an additive UI proposal; it does not certify or replace backend phases.
2. **Before approval:** research/documentation only. After explicit approval, inspect the current tree, status, history and remote again. Another developer may have changed this baseline. Preserve unrelated work.
3. Current owner instruction overrides the earlier isolated-worktree proposal: preview was fast-forwarded into `main` at `436f449`, published and remotely verified. Continue in main, preserving unrelated changes, especially the owner's `docs/DATABASE_SETUP.md`. Do not rewind to the older landing branch or copy its backend history.
4. The approved visual reference is the isolated landing at branch `design/landing-preview`, commit `4edb747027b7ec0a980d3377209b43d05b840723`, directory `landing-preview/`, currently in `E:/mu idea/Shongoti-landing-preview`. Inspect the files and existing tests. Port selected visuals/interactions to React; **do not merge the old branch wholesale over current backend work**. The preview is a synthetic demonstration, not an existing React app or verified live agent service.
5. Do not use the teammate's Downloads HTML or the four-direction study as replacement authority. Preserve the locked palette, typography direction, receipt illustration language and editorial composition. No coral accent, new serif identity or palette reset has been approved.
6. Every new path in this plan is **proposed**, unless explicitly listed as existing. Every API must be checked against its actual request/response schema and authorization. A decorator inventory does not establish runtime compatibility.
7. Refactor existing behavior; preserve exact-money and tenant boundaries. Backend changes are limited to necessary, separately tracked interface blockers. Major model/retrieval/orchestration replacement requires its own scoped implementation decision and evaluation; UI polish cannot declare it complete.
8. No fake success, fabricated agent traffic, timer-generated progress, invented citations, default transaction amounts or live-provider badges from fixture data. Preserve user input on failed requests. No automatic customer messages or payments.
9. Keep a separate UI tracker, created in UIR-00: `docs/UI_REDESIGN_PROGRESS.md` and `docs/ui-redesign-progress.json`. Each task needs state, owner, source revision, dependencies, evidence paths and exact next action. Do not overwrite the original/extension trackers with UI estimates.
10. After each verified UI phase, follow `docs/GIT_CHECKPOINTS.md`: milestone **commit AND normal GitHub push**, verify remote ancestry, publish the checkpoint receipt and verify the final tip. Use footer `Shongoti-UI-Phase: UIR-XX`; retain the repository's checkpoint evidence fields. Do not present a UI identifier as an original `Shongoti-Phase: 00–26` milestone. If automation expects numeric phase IDs, extend the parser explicitly and test it rather than mislabeling the phase. A blocked publication remains blocked; no force-push.
11. Finish only from observed checks. Source audit, component test, browser test, real provider call and merchant usability test are different evidence. Missing access does not stop independent UI work; it does prevent corresponding live claims.

## 3. Current application: what actually needs redesign

The audit covers all 14 routed frontend screens, the eight new feature components, shared styling/i18n, API declarations and critical agent/copilot/retrieval/confidence paths. It is **not** an exhaustive security review, backend regression certification or rendered usability study. The inventory snapshots 130 source/test/script files and 98 API declarations; hashes establish the inspected revision, not correctness.

| Observed at this baseline | Product/design consequence | Required response |
|---|---|---|
| `App.tsx` exposes 14 routes. Eight extension components have no production imports. | Buying, Receiving, Copilot, Agent Timeline, Demand, Inbox, Operations and Help are not reachable through the actual application router. | Build real route containers, navigation and data adapters before calling them shipped screens. |
| Legacy pages repeat Navbar/Sidebar and many inline blue/slate styles. | A palette change alone leaves inconsistent density, states and navigation. | Introduce three shells and reusable tokens/primitives; migrate incrementally. |
| OperationsHub/BusinessHelpDesk rely on utility class names; no Tailwind stylesheet/build is present. | Mounting them does not deliver the intended styling. | Rebuild their presentation in the selected styling system; do not add a framework just to mask this gap. |
| Login advances locally; onboarding navigates without persisting its values. | A polished entrance would still fail to establish the expected session/setup. | Verify auth/setup contracts and distinguish local demo from actual sign-in. No pretend OTP delivery. |
| Today starts with hardcoded balances; errors can leave those visible. Some quick actions have no handler. | A shop owner cannot know whether the numbers/action are real. | Explicit data modes and real CTA wiring; no synthetic fallback in a real tenant. |
| Reconciliation uses local fixed hypotheses and a success toast claiming posting without an API call. Its inclusion labels conflate concepts. | The signature product story currently risks showing the wrong financial meaning. | Replace with source-backed case/evaluate/clarify/action workflow; exact inclusion language. |
| Sales collection/link routes differ from server routes; several catches claim success. Planner's failed save claims local save. | Good-looking confirmations could hide failures. | Central typed requests; observed persistence/transaction receipt required for success. |
| Agent POST runs synchronously and returns completed history; some role results are fixed text. | Current source does not establish live parallel model collaboration or real-time cancellation. | Show recorded task history accurately; gate live/parallel animation on actual backend events. |
| Copilot is primarily keyword/templated routing; missing payment amount can default to BDT 5,000. Retrieval can use a lexical embedding double. | Chat appearance must not imply general model intelligence, neural dense retrieval or a verified payment proposal. | Expose actual capability mode; require missing facts; track engine blockers independently. |
| Confidence policy uses strong >=85 and critical cap59; Copilot/UI fallbacks can use >=80. Badge styling prioritizes strong over blockers. | A positive color can overstate support and readiness. | Use one canonical assessment, blocker-first rendering; no local invented score/band. |
| Browser runner exits successfully after detecting a driver without running a journey. | Existing e2e command cannot establish full UI acceptance. | Implement real browser journeys and verify failure detection. |

Frontend baseline: **27 tests in 11 files passed; TypeScript + production build passed**. These do not resolve the above gaps. React Router future warnings and DemandTracker `act(...)` warnings were observed. Browser, live AI, gateway and real-user tests were not run in this review. Details and commands are in the audit.

## 4. Design direction: Modern Khata + Evidence Lab

The visual story is a contemporary merchant's workbench: paper, receipts, annotations, connected evidence and deliberate ink. Landing can be expressive; daily entry remains fast and readable. The AI areas share the same identity with a deep-forest work surface and lime task signals.

### Locked and proposed decisions

| Element | Direction |
|---|---|
| Locked brand colors | Paper `#F7F7EF`, forest `#163E30`, deep forest `#0E2E23`, ink `#183C2E`, lime `#DEEF9B`, line `#DCE1D4`, white `#FFFEF9`. |
| Locked type direction | Anek Bangla + Inter, with appropriate Bengali system fallbacks. Verify font files, actual available weights, licenses and conjunct rendering during implementation. |
| Proposed app surfaces | Light paper workspace, white editing surfaces, restrained dark navigation/AI work areas. Large dark blocks reserved for a meaningful investigation/brief, not every card. |
| Proposed semantic colors | Separate tested danger/warning/info tokens with text/icons. These are state colors, not a new decorative brand accent. Lime never means “financially verified” by itself. |
| Type scale | App body16px, labels14px, financial totals28–40px; Bangla line-height roughly1.6–1.75 after testing. Marketing headings fluid and larger. No tight Latin tracking on Bangla. |
| Geometry | 4/8px spacing rhythm, compact controls8–10px radius, panels14–18px, thin rules. Avoid rounding every surface into a pill. |
| Layout | Desktop max workspace1440px, flexible 12-column grid; readable prose max~70 characters. Tables can be denser without shrinking text illegibly. |
| Illustration | Original receipt, shop shelf, stamped source and cash-route motifs, SVG where suitable. No stock robot heads, generic glowing brains, emoji agent avatars or copied award-site assets. |
| Numbers | Exact paisa internally. Format only at display boundary with `Intl`/existing formatter after verifying unit contract. Tabular numerals; BDT/৳ explicit. Bangla/English number preference must not alter values. |

A recognizable signature is **a thin evidence spine**: a source marker follows a claim into a question, a decision and its outcome. Use this across capture, cases, copilot citations and credit recovery. Different screen compositions share that visual grammar.

### Why this should feel authored

- Each screen has a business verb and one dominant action. The layout follows that task, rather than repeating three KPIs + six cards everywhere.
- Large/small scale contrast, asymmetric editorial sections on landing, restrained rules and locally appropriate Bangla copy give rhythm.
- AI presence comes from grounded behavior: noticing an unknown, locating evidence, comparing alternatives and updating a decision.
- Use concrete descriptions such as “এই ৪,০০০ টাকা কি ২৫,০০০-এর দাবিতে আগেই বাদ আছে?” instead of “Unlock intelligent financial synergy.”
- No manufactured customer logos, savings claims, awards or fake review counts. Synthetic competition examples are labeled.

These are design judgments. No real merchant access is currently available, so preference, learning time and day-to-day efficiency remain hypotheses to validate.

## 5. Research and what we apply

Sources checked 23 November 2026. Official documentation/galleries support the facts below; Shongoti applications are our recommendations. The reference sites' full interactive behavior was not browser-tested here. Some award-page refreshes timed out; earlier retrieved gallery information is not a current performance audit.

| Primary source | Relevant finding | Apply to Shongoti |
|---|---|---|
| [Linear March2026 UI refresh](https://linear.app/changelog/2026-03-12-ui-refresh) | Emphasizes consistent navigation/view controls and information scanning. | Stable shell; task focus; progressive detail rather than permanent dashboard clutter. |
| [Linear agent interaction](https://linear.app/developers/agent-interaction) | Distinguishes working, waiting, errors, completion and stale sessions through activities. | Separate run status, evidence readiness and owner approval. Use emitted activity, not invented movement. We do not adopt Linear's API/state names as existing Shongoti DTOs. |
| [Oryzo AI gallery](https://www.awwwards.com/sites/oryzo-ai), [Why Zero gallery](https://www.awwwards.com/sites/why-zero) | 2026 award references with distinctive interactive/narrative treatments. | One memorable evidence interaction and a coherent story. Do not copy their assets or import WebGL into routine transaction entry. |
| [Motion for React](https://motion.dev/docs/react), [reduced motion](https://motion.dev/docs/react-use-reduced-motion) | React motion and responsive reduced-motion hooks. | Shared layout/state transitions with a system/user motion preference. No requirement for paid components. |
| [GSAP React](https://gsap.com/resources/React/) | React-oriented scoped animation/cleanup guidance. | Optional for a measured landing sequence only; not a second default engine for the app. |
| [Radix accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility) | Primitives address focus and keyboard behavior; labels remain the implementer's responsibility. | Use small unstyled primitives for difficult interactions, styled in our brand and tested in context. |
| [React Flow performance](https://reactflow.dev/learn/advanced-use/performance) | Graph rendering needs deliberate component/state optimization. | Only consider a lazy-loaded graph when actual graph data and complexity justify it. Start with accessible list + small SVG. |
| [W3C status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Important changes should be announced without unnecessary focus interruption. | Summarized polite activity updates; focused alerts only for meaningful blocking errors. |
| [W3C pause/stop/hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | Ongoing automatic movement/updates need appropriate user control. | Motion-off and pause visual feed. Pausing animation must not imply cancelling a financial/backend operation. |
| [Web Vitals](https://web.dev/articles/vitals) | Good thresholds: LCP<=2.5s, INP<=200ms, CLS<=0.1 at p75. | Track field metrics when traffic exists; use reproducible lab budgets before launch and label them lab results. |

The references support usability and implementation principles; they do not establish hackathon scoring criteria or guarantee a win. More animation does not establish more AI capability.

## 6. Navigation: fewer destinations, complete coverage

Three shells: **PublicShell** (landing/auth/demo), **MerchantShell** (authenticated tenant/role/context), **PortalShell** (public scoped customer token). Names are proposed components.

Desktop MerchantShell: narrow forest sidebar, paper header with page context/date/search, global **যোগ করুন**, inbox, language and Copilot. A collapsed activity strip appears only for relevant real work; it never blocks entry. Mobile: Today, Sales, Capture, Cases, More; side destinations through More and contextual links. No twenty-item sidebar.

| Main group | Existing paths to preserve | Proposed deep links / views |
|---|---|---|
| আজ / Today | `/app` | Daily brief and actionable work |
| বিক্রি ও মানুষ / Sales & people | `/app/sales`, `/app/people` | Party detail route `/app/people/:partyId` if an authorized detail contract exists; otherwise a linked drawer |
| কেনা ও পাওয়া / Buy & receive | — | `/app/buying`, `/app/receiving`; purchase drafts, returns and credits as tabs |
| মজুত ও চাহিদা / Stock & demand | `/app/stock` | `/app/demand`, SKU detail drawer |
| টাকা ও আগামী / Money & future | `/app/money`, `/app/planner` | Commitments and scenarios as contextual tabs |
| হিসাবের তদন্ত / Cases | `/app/reconciliation` | `/app/cases`, `/app/cases/:caseId`, `/app/agents/:runId`; keep existing reconciliation link operational |
| আরও / More | `/app/reports`, `/app/connections` | `/app/operations`, `/app/help`, `/app/inbox`, `/app/actions`, `/app/evidence`, `/app/settings` |
| Global Copilot | — | Context drawer and `/app/copilot`; same session state, not duplicate chats |
| Public and customer | `/`, `/login`, `/onboarding`, `/demo`, `/pay/:token` | Preserve URL semantics; separate shells and tenant boundaries |

New routes are navigation proposals, not new API promises. Cases/actions/evidence can reuse list/detail APIs where present; settings/onboarding/party detail/source file viewing may require explicit missing contracts. Register blocked functionality honestly; never create an editable screen whose save only changes local memory while claiming persistence.

### Existing extension components: explicit integration map

These components already exist under `apps/web/src/components/`, but currently have no production imports. Reuse their useful contracts/domain intent; redesign presentation and validate adapters rather than treating their component tests as route integration evidence.

| Existing component | Proposed owner / entry | Existing API boundary to inspect |
|---|---|---|
| `AgentTimeline` | Case workspace and `/app/agents/:runId` container | Agents run/detail/events/cancel; map `event_seq` and `task_id` explicitly |
| `CopilotChat` | Shared session owner for drawer and `/app/copilot` | Copilot sessions/messages/voice; canonical confidence and citation adapters |
| `BuyingDesk` | `/app/buying` | Buying offers/compare/orders-draft; verify amount/unit DTOs |
| `ReceivingTracker` | `/app/receiving` credit/recovery view | Receiving receipts/credits/apply; reconcile stock-receive ownership before writes |
| `DemandTracker` | `/app/demand`, contextual SKU view | Demand unmet records/analysis; counts are not revenue |
| `ActionableInbox` | Global inbox and `/app/inbox` | Notifications list/read/snooze/resolve/brief; add actual destination context where absent |
| `OperationsHub` | `/app/operations` | Operations reservations/pick, containers/movement, handovers, supplier-change-check; wire unused movement callback |
| `BusinessHelpDesk` | `/app/help` | Helpdesk checklist/documents/guidance/corpus; verify upload contract rather than assuming multipart support |

`ConfidenceBadge` must become the shared canonical assessment presentation within these containers, not a second confidence policy. `Navbar`, `Sidebar`, `Card`, `Button`, `Badge` and `EmptyState` are migration inputs for shells/primitives; remove old variants only after all consumers migrate.

## 7. Page-by-page design specification

### 7.1 Landing `/`

Port the locked landing composition rather than redesigning it again: editorial Bangla hero, original receipts/evidence illustration, daily workflow story, dark investigation section, owner voice example, trust explanation/FAQ and final CTA. Preserve mobile navigation, language switching and motion controls. Remove preview-only chrome only when the destination's demo status is still clear.

Hero primary CTA opens an actually isolated synthetic demo; secondary explains the workflow. Do not silently open a real merchant session. Interactive supplier question uses deterministic synthetic fixtures, labeled “উদাহরণ”; it does not claim a live model call. Route links and CTA outcomes must work. Keep initial content visible before animation/JS enhancement and preserve native scrolling.

### 7.2 Login and onboarding `/login`, `/onboarding`

Split editorial/compact form on desktop; single-column on mobile. Phone/OTP flow gets real request/verification/error/resend states only where sender capability exists. Local demo authentication is explicitly named; advancing a screen is not sending an OTP.

Onboarding is a short checklist: shop identity, opening balances by account, existing dues/evidence import, review. Separate optional imports from necessary setup. Require server receipt for saved values; show unconfigured setup honestly if API missing. Store no false “all set” state. Successful sign-in returns to intended authorized route; tenant/role/session expiry are handled consistently.

### 7.3 Today `/app` — the operating desk

Top: “আজ দোকানে আগে কোন কাজটা?” plus date/as-of. First row has actual available funds by account and a prioritized next-action list. Receivables and promises are visibly separate from funds. Show source freshness; no green “Live” without verified context.

Center-left is an **opening-to-closing work ribbon**: receive → sell → collect/pay → close. Each step opens the actual tool with context, no empty buttons. Center-right is one investigation/decision needing attention, not a wall of competing AI widgets. Lower area: concise recent receipts and stock issues.

Daily brief has a user-triggered listen control and complete transcript. If voice unavailable, retain text; no autoplay in a shop. Source links lead to the underlying case/transaction. A run that's already completed appears as an outcome, not a looping working indicator.

```text
Today                              [Search] [+ Add] [Inbox] [Copilot]
------------------------------------------------------------------
Actual funds / accounts             What needs your decision (max3)
Cash | wallets | pending separate   Supplier question / due deadline
------------------------------------------------------------------
Opening -> Receive -> Sell -> Collect -> Close     [Today's brief]
Recent real records                           [Relevant case + source]
```

### 7.4 Sales `/app/sales` and people `/app/people`

Sales uses a focused two-column entry/cart or ledger form, with recent records beside it. Keyboard-friendly amounts, party selection, payment account and partial credit. “Record sale” and “Collect existing due” are distinct modes with different explanations. A sale receipt can be reviewed and linked to a party; collection must not create revenue twice. Failure retains all input and permits safe retry.

People is a searchable directory/table, opening a party account drawer with balances, source-linked transactions, promises and disputes. Separate **amount due** from **promised date** and **risk interpretation**. Communication drafts show recipient/channel/content and require existing authorization; unavailable channels remain unavailable. Creating a portal link is different from actually sending it.

Motion: entry confirmation connects the saved receipt to its actual ledger row; brief highlight only after server success. No falling coins or financial amount count-up. Do not fabricate history or delivery ticks.

### 7.5 Buying `/app/buying`

An **offer comparison desk**, not generic product cards: SKU/quantity header, supplier quote columns, normalized unit/landed cost, MOQ/bonus/expiry terms and source markers. Cost arithmetic is deterministic. AI interprets ambiguous terms, matches messy quote units and identifies missing conditions; show that evidence explicitly.

Selected offer opens a decision tray: payment account, known obligations, scenario delta, unsupported conditions and **Draft order**. Highlight cheapest and most feasible separately; do not turn “recommended” into an order or assume conditional bonuses. No live supplier price claim from uploaded quotes alone.

### 7.6 Receiving, returns and credits `/app/receiving`

A **receiving bench**: expected vs physically received vs usable vs damaged/missing, represented by labeled quantity bars and a count table. One screen must not create two overlapping inventory receipts through the old stock receive API and the extension receipt API. UIR-00 must decide the authoritative receiving write path and link the other view read-only until consistency is proved.

For discrepancy, attach source and open a claim. The recovery rail preserves suspected → reviewed → accepted by supplier → applied to invoice, or rejected. Accepted is not applied. A stamped visual appears only from persisted status. Apply-credit dialog displays target invoice, remaining capacity, amount and record version; duplicate clicks/version changes cannot allocate twice.

### 7.7 Stock `/app/stock` and demand `/app/demand`

Stock is an inventory table with search, low/zero-stock filters and a SKU detail drawer. Include usable quantity, cost completeness, recent movement and reorder explanation. Purchase/receiving actions deep-link to the unified bench. CSV import opens mapping/preview/errors before confirmation; no optimistic “imported” from a client parse alone.

Demand is a **missed-request notebook** with quick text/voice capture, normalized SKU suggestion and source. Counts are unmet requests, not sales revenue. Analysis shows observation period, stockout availability, sparse-history state and assumptions. Reorder proposal connects to Buying/Planner as a draft; forecasts get their own uncertainty/freshness labels.

### 7.8 Money `/app/money`

An **account and movement ledger**: each cash/wallet/bank account clearly separate, pending settlement adjacent but excluded from spendable total. Common actions are transfer, expense, withdrawal, supplier payment and cash close. Actual available account funds and due amount remain independent.

Payment review shows source account, verified destination, amount, fees, obligation and remaining balance; displayed cash shortage does not reduce amount owed. The system can propose collection drafts/scenarios, but cannot claim it moved money between personal wallets without real supported provider operations.

Cash close compares counted cash with expected ledger balance; a discrepancy opens an evidence question, not an automatic accusation. Motion highlights the changed line after real posting and exposes its receipt.

### 7.9 Planner `/app/planner` — the decision lens

Two aligned views: baseline and proposed decision, with exact delta and affected dates. A large readable cash runway chart uses distinct line/pattern/text for actual, committed, conditional and predicted values. Reserve threshold and due dates are labeled. The chart has an accessible date/value table.

Merchant asks “আজ ৮,০০০ টাকার মাল কিনলে বৃহস্পতিবার supplier payment-এ কী হবে?” The response separates the deterministic scenario result from AI's explanation and unresolved inputs. A crosshair/date selector links the chart to each inflow/outflow source. Scenario editing is explicit; never recompute on every keystroke with unbounded calls. Saved is shown only after persistence confirmation.

Promised collection is a separate conditional lane. Toggle that lane to compare assumptions; it does not add to actual funds. No invented forecast accuracy or causal claim beyond the model/scenario inputs.

### 7.10 Cases, reconciliation and agent workspace

Cases list: business question, supplier/party, age, next needed fact, readiness and latest actual run status. Open case detail as a three-part **evidence workspace**:

```text
Case / version / question                 [Run history] [Review draft]
-------------------------------------------------------------------
Sources              Investigation / claims            Decision
Bill page3           Terms / reconciliation / checks    Alternatives
Payment receipt ---> Supported / contradicted / ? ---> Support + gaps
Return message       One critical question             Owner review
-------------------------------------------------------------------
Event history (actual sequence)  [Pause visual feed] [Sources] [Replay]
```

Sources open the real authorized page/line/audio timestamp when available. When only extracted text exists, say so; no invented bounding box. Selecting a claim highlights linked sources and the affected alternative. Rejected/superseded evidence remains visible with reason, excluded from active support.

Canonical example: supplier demand BDT25,000; applicable payment BDT4,000 and accepted applicable return BDT3,000. **Only amounts not already included in that demand can be deducted again.** With those prerequisites established, possible balances are25,000 /22,000 /21,000 /18,000. Applicability, acceptance and prior inclusion are separate questions. Unknown prerequisites remain unknown; no default18,000 or guessed answer. Backend evaluates in integer paisa.

Signature moment: answer the critical inclusion question → reassessment returns a new case version → show exactly which alternative/support changed and why. Old draft becomes stale; re-review required. The UI must not imply that a clarification itself posted money.

Agent view provides both **task map and chronological list** from the same data. Coordinator plans, terms specialist retrieves, reconciliation tool evaluates and skeptic checks contradictions **only when those operations actually occurred**. A role label is not proof of a separate model inference. Show bounded task summaries, tool receipts and reasons; do not expose or invent private chain-of-thought.

### 7.11 Copilot `/app/copilot` and global drawer

Context strip identifies current shop/page/case and scope. Composer supports text, user-controlled recording/upload and selected attachments with clear upload/parse/failure stages. Allow transcript correction before a compound financial draft. Preserve unsent input and attachments on error; cancellation/size/type limits are visible.

Answers use structured blocks: direct answer → relevant source citations → evidence support and missing facts → proposed next action. Citations are openable references, not just a count. An unavailable score still shows sources, limitations and next question. Do not stamp “Verified Ledger Connection” independent of actual access.

Quick prompts are contextual business tasks, not canned responses labeled AI. Opening a long investigation links to its case/run without blocking the chat. Transaction drafts need all critical fields; no default BDT5,000 when the merchant omits an amount. Owner reviews a separate proposal before any execution.

### 7.12 Inbox `/app/inbox`, voice brief and approvals `/app/actions`

Inbox groups **Need your answer**, **Review a draft**, **Time-sensitive**, **Updates** with business links and actual unread counts. Resolve only when its business state is resolved; snooze changes delivery timing, not the underlying obligation. Duplicate alerts use actual notification identity/deduplication.

Brief combines a concise transcript with source links/as-of and user-initiated audio controls, replay/pause and volume preference. Missing Bangla voice or provider keeps transcript and an honest unavailable state. No autoplay and no audio-only critical alert. Avoid reading sensitive amounts aloud without user intent.

Approvals are a focused queue: draft → reviewable → approved → executing → succeeded/failed/cancelled, mapped from actual server states. Display role, version and consequences. Approve is separate from execute. Failed/unknown execution requires status reconciliation before retry; never label it “safe to retry” by assumption.

### 7.13 Operations `/app/operations`

Task-focused tabs: reservation pick list, returnable containers/deposits, shift handover and supplier-detail-change check. Quantity checkboxes and count forms dominate; AI explanations appear where ambiguity/contradiction needs review.

Pick is not automatically sold; container quantity and deposit money are separate records. Handover shows expected/counted/difference with neutral hypotheses and evidence. Supplier destination changes receive an explicit verification gate; no AI badge authorizes a new payment destination.

### 7.14 Business help `/app/help`

Document/checklist-first screen: outstanding items, uploaded documents, notice/deadline review and a question pane. Each answer shows jurisdiction, publication/effective/review dates where actually known and official source links. Stale/unreviewed/out-of-scope material is labeled and cannot look like current binding guidance.

AI helps find obligations in documents, compare records and draft a question for a professional. UI does not claim filing completion, guaranteed compliance or personalized legal authority. This redesign does not add substantive legal advice or assume an operational official corpus exists.

### 7.15 Reports `/app/reports`

Readable report canvas with filters, date/as-of and export. Separate cash movement, sales revenue, collections and operating result; retain incomplete-cost notices. Charts explain a business question, with exact table alternatives. Share/export uses real export endpoints and excludes unsupported/confidential fields; no success on failed download.

AI commentary is source-linked interpretation; deterministic totals stay deterministic. Unavailable forecasting remains unavailable, not a smooth synthetic chart.

### 7.16 Connections `/app/connections` and settings

Capability register by operation: disconnected/configured/unverified/sandbox/live/degraded/revoked, as supported by actual data. Distinguish gateway checkout from wallet balance access, payouts and messaging. Last checked date/result and required setup are explicit; secrets never appear in UI or screenshots.

Move IPN callback crafting to authorized development diagnostics; a merchant-facing “connect wallet” button cannot simulate an IPN as a connection. Proposed settings hold language/numerals/motion/voice preferences and authorized shop/account configuration only after persistence/permission contracts exist.

### 7.17 Customer portal `/pay/:token` and demo `/demo`

Portal: very lightweight branded document view, amount/reference, dispute, supported pay flow, processing/verified result. No merchant sidebar, agent logs or global tenant tools. Invalid/expired/revoked links get clear states. Redirect alone is not payment verification; use authoritative server/provider status.

Demo: guided entry into an isolated synthetic tenant, reset/exit controls and persistent demo label. It tells the same evidence story as the real app while marking fixture/replay/provider modes. A demo card must not deep-link into a user's real merchant data or fabricate a real session.

## 8. Agentic behavior: data before animation

### Three separate state axes

| Axis | Meaning | Never infer from |
|---|---|---|
| Execution | Task/run queued, running, waiting, completed, failed, cancelled or stale where supported | Visual spinner duration or score |
| Evidence/readiness | Supported claims, critical unknowns, contradictions, review needed | Run completion or a specialist's name |
| Authority/action | Who may review, approve, execute; actual posting/delivery outcome | High support score, chat answer or optimistic UI |

Current DTO states must be mapped explicitly; proposed waiting/stale/queued states require backend support or a clearly derived client connectivity condition. Never serialize invented statuses into existing APIs.

### Agent capability gate

**Available presentation path now:** fetch persisted run/task/events; order by real sequence, show summaries/source links and the result; offer clearly labeled **Replay recorded activity**. Fetching history is not receiving a live stream. The current `budget_calls_used` counter must be labeled as the verified step/counter meaning, not measured model calls, tokens or currency cost.

**Live presentation path requires separate verified work:** background run lifetime, actual tool/model receipts, durable incremental events, task dependencies, validated execution mode, meaningful cancellation and failure/reconnect behavior. Polling can be a first transport when runs truly progress independently; SSE is optional and must have an actual endpoint before use. Do not invent `/stream`.

Proposed event view model, **not an existing DTO**: run/task/event IDs, monotonic sequence, operation kind (tool/model/retrieval/review), mode, timestamps, public summary, source/claim references, dependency IDs when known, result status and optional measured usage. Existing events lacking fields render “not recorded”; do not estimate them.

Map existing `event_seq` to the frontend sequence field and `task_id` to its task; validate duplicates/out-of-order input. Draw dependency edges only when actually known. Parallel lanes need overlapping actual execution intervals; chronological order alone does not establish concurrency. Historical `created_at` timestamps are not sufficient to prove separate live model calls.

Hide unknown token/cost values as “not recorded”, not zero. Stop/pause visual playback leaves the backend unchanged; real cancel has a separate control and confirmation from the server. Late/stale updates cannot overwrite a newer case version. All graph content is available in keyboard-readable list form.

## 9. Confidence is a product contract

Use `apps/api/app/confidence/policy.py` / evidence-support-v1, not retrieval similarity, model self-rating or UI arithmetic. Initial versioned thresholds: strong>=85, review>=60, otherwise limited; critical unsupported fact caps at59 and blocks readiness as defined by policy. These are policy bands, **not calibrated correctness probabilities**.

Canonical presentation: **প্রমাণের সমর্থন ৭২/১০০** + readiness text + “কেন?” disclosure. Explain the score version, underlying claims/source locators, contradictions, critical blockers, assessment time and invalidating changes. Show original and capped score only if supplied by the policy result. A null result is “মূল্যায়ন হয়নি/পাওয়া যায়নি,” never0 or secretly100.

Precedence: permission/execution block or critical blocker → stale/unavailable → ordinary support band. Even a high score must not paint a blocked decision as ready. Readiness and support can both be displayed without overriding each other. Field mapping (`critical` vs `is_critical`, snake/camel case) is a typed adapter responsibility.

No auto-approval, low-score auto-payment or invented confidence animation. On new evidence, mark old assessment stale until reassessment returns. Cash calculations do not need an AI probability badge; show their data completeness/as-of separately. Scores must affect the available next step: ask missing fact, review evidence, prepare a reviewable draft, or block unsafe action.

## 10. Motion system and unique interactions

We want many carefully designed interactions across the product, with few simultaneous movements. All durations below are proposed starting tokens, to tune with actual hardware and reduced-motion checks.

| Interaction | Trigger and visual effect | Duration / fallback |
|---|---|---|
| Control feedback | Press, selection, disclosure | ~120–180ms; immediate selected state |
| Panel/layout | Open inspector, switch contextual view | ~180–280ms; reduced motion instant/short fade |
| Evidence trace | User selects a source/claim; one connector reveals its relationship | ~350–650ms once; static highlighted line/list fallback |
| Agent handoff | Actual new event/task receipt updates its lane | ~200–350ms; no invented travel between unrelated roles |
| Decision delta | New assessed version replaces old; changed facts and amount line highlighted | ~250–400ms; exact amount appears immediately, no count-up |
| Scenario lens | Explicit simulate response; baseline/alternative overlay resolves | ~300–450ms; static chart/table fallback |
| Receiving split | Confirm actual counts; usable/damaged/short bars update | ~200–350ms; numbers never depend on transition completion |
| Landing story | Finite source-to-question-to-decision sequence | ~600–900ms per deliberate step; native scroll, no forced delay |

Additional requirements:

- System reduced-motion plus persistent in-app preference; honor changes during use. No parallax/large translation in reduced mode.
- Long-running visual feed can be paused/hidden; summary announces meaningful status at controlled frequency. Do not put every event/token into an assertive live region.
- Motion only on transform/opacity where practical. Never animate entire large tables or cause repeated reflow on keystrokes. Offscreen/hidden-tab decorative work pauses.
- No cursor followers, global tilt, floating money, endless glowing agent orbs, scroll hijack, delayed form input, fake progress percentages or staggered reveal that hides financial data.
- User focus stays with the task. New events do not steal focus, scroll the whole page or move a button under a pointer. Returning from a drawer restores focus.
- Voice is explicitly started, with visible speaking/paused/unavailable state and transcript. Activity transitions have a silent equivalent.

## 11. Technical implementation approach

Preserve React18 / TypeScript / Vite and FastAPI modular monolith. Do not introduce a second financial store or rebuild in a new framework for visual polish.

| Area | Recommendation | Decision gate |
|---|---|---|
| Styling | CSS custom properties + CSS Modules or well-scoped existing CSS. Central semantic tokens and primitives. | No Tailwind/framework migration solely for this redesign. Replace uncompiled utility-dependent component presentation. |
| Motion | `motion` for React for app transitions + native CSS/SVG for simple states. | Verify actual stable package/version/React18 compatibility and API types; pin in lockfile; no prerelease assumption. |
| Complex landing sequence | Existing CSS/SVG first; GSAP only if authored sequence genuinely benefits. | Small isolated module; cleanup on unmount; do not animate the same DOM property with both engines. |
| Accessible overlays | Minimal unstyled Radix primitives where warranted; native controls elsewhere. | Validate labels, focus, portal stacking and keyboard; library choice is not an accessibility pass. |
| Agent diagram | Small SVG + semantic list first. Optional lazy React Flow for larger actual dependency graphs. | No graph dependency solely to display four fixed role cards. |
| Charts | SVG for small runway/quantity views; assess a chart library only after real interaction/accessibility needs. | Table fallback and measured bundle cost. No chart package assumed installed. |
| API client | Typed boundary and common error/session handling. Inspect existing DTOs; generate/validate contracts where practical. | Do not manually invent response fields from a screenshot. Reuse existing backend paths. |
| Server state | Shared request/cache layer with cancellation, tenant-keyed caches and explicit freshness. | First assess existing needs; add one query library only with recorded benefit/version review. No cache shared across tenants. |
| Testing | Existing Vitest/Testing Library plus real browser journeys. | Install/verify driver and browser only during approved implementation; package detection is not a test. |

Proposed frontend organization (create only after verifying current structure):

```text
src/design/                 tokens, typography, semantic motion tokens
src/layouts/                PublicShell, MerchantShell, PortalShell
src/components/ui/          controls, dialogs, tables, state panels
src/components/evidence/    source viewer, claim, assessment, decision diff
src/components/agents/      activity strip, run list/map, task detail
src/features/<domain>/      page container, API adapter, view models, views
src/lib/api/                typed transport, error/session handling
src/i18n/                   existing language contract extended consistently
```

This is a migration target, not a requirement to move every file before shipping a vertical slice. Preserve existing imports via small explicit steps; no cosmetic mass rename.

### API mismatches and missing contracts to resolve first

Existing audited routes include:

- Collection: `POST /api/v1/merchant/collect-due`, not `/merchant/debt-collection`.
- Portal link: `POST /api/v1/portal/generate-link`, not `/actions/customer-portal-links`.
- Gateway callback: `POST /api/v1/payments/sslcommerz/ipn`, not `/actions/sslcommerz/ipn`; this is not a merchant connection UI action.
- Cases: `/api/v1/cases`; agents: `/api/v1/agents/runs` and `/{run_id}/events`; copilot: `/api/v1/copilot/sessions` and its messages/voice routes.
- Existing APIs also cover buying, receiving, demand, notifications, operations, helpdesk, evidence and search. See the complete declaration inventory before creating any endpoint.

UIR-00 must verify DTOs, role checks, units and errors with contract tests. Explicitly resolve source-file viewing/authorized download, setup/settings persistence, party detail/history, reliable receiving linkage, event mode/usage semantics and action-version behavior. Metadata/extracted text alone may exist where a source binary viewer is proposed. Do not guess these contracts or send secret storage paths to the browser.

## 12. Responsive, Bangla and failure behavior

- Validate360,390,768,1024,1440px. At narrow widths use task list/drawer instead of squeezed three-column case graph. Tables scroll within their labeled region or switch to task-specific rows; no whole-page horizontal overflow.
- Bangla is default where current product specifies it. Complete English parity, localized dates/currency/accessible labels, no clipped conjuncts. Bengali is left-to-right. Avoid fixed-height text boxes and image-rendered UI text.
- Prefer44px touch targets as product policy; measure keyboard reach, 200% zoom and relevant WCAG2.2 AA criteria. Text contrast4.5:1 (3:1 for qualifying large text); UI/state contrast checked separately. Measure palette pairs; do not assume lime-on-paper passes.
- Every domain supports loading, meaningful empty, validation error, request failure, permission denied, expired session, stale/partial data and disconnected capability. Error details help recovery without leaking private data.
- Demo data only in explicit demo context. In a real tenant, missing/error data is unavailable; it is not seeded financial activity. No fabricated offline saved status. An offline draft, if implemented, states storage scope/sync state and never claims posting.
- Mutations retain inputs, use idempotency/version boundaries, handle duplicate click/timeout/unknown result, and refresh related views from authoritative state. Disable unsupported execution while permitting independent read/capture work.

## 13. Implementation phases — gated and trackable

All tasks below are **not_started**. Preparing this plan does not complete UIR-00. Each phase needs actual evidence and the required Git checkpoint. Dependencies refer to verified deliverables, not dates or optimistic percentage estimates.

### UIR-00 — Reconcile reality and lock interface contracts

Dependency: explicit user approval. Tasks:

- [ ] UIR00-T01 Reinspect latest Git/source/checkpoints; create isolated worktree and UI trackers. Reconcile changed audit findings without erasing previous history.
- [ ] UIR00-T02 Build route/component/API capability matrix: reachable, wired, mode, permissions, DTO, financial units, state, test and missing contract. Cover all14 existing routes +8 unmounted features +global tools.
- [ ] UIR00-T03 Resolve auth/setup, endpoint mismatches, false-success paths, authoritative receiving write path, confidence adapter and source viewer contracts. Track backend blockers separately with exact acceptance checks.
- [ ] UIR00-T04 Classify agent/copilot/retrieval capabilities from executed evidence. Choose history/replay or verified live mode; no unsupported marketing claim.

Gate: every proposed screen has a data owner, real contract or explicit blocker; baseline tests/build recorded. No live-agent/semantic-search readiness inferred from component presence. Publish checkpoint/receipt with audit, not a false “entire product verified” claim.

### UIR-01 — Brand system, shells and primitives

Dependency: UIR-00. Tasks:

- [ ] UIR01-T01 Port locked tokens/fonts/logo/illustration conventions; create style catalogue with actual states and Bengali text.
- [ ] UIR01-T02 Build Public/Merchant/Portal shells; route guard/session boundary, grouped navigation, mobile More/capture and focus behavior.
- [ ] UIR01-T03 Build buttons/forms, table/list, drawer/dialog, toasts/state panels, source marker and canonical confidence presentation.
- [ ] UIR01-T04 Establish motion tokens/preference, typography/contrast measurements, typed request/session handling and tenant cache reset.

Gate: browser screenshots at360/768/1440 for all shells, Bangla/English, focus/overlay/zoom/reduced-motion checks; component tests verify blocker/null precedence and request failure handling. Missing browser means gate incomplete. Checkpoint.

### UIR-02 — Signature vertical slice before broad rollout

Dependency: UIR-01 and relevant UIR-00 contracts. Tasks:

- [ ] UIR02-T01 Port approved landing to React, preserve design/interaction semantics; real demo/login links and responsive states.
- [ ] UIR02-T02 Redesign Today using actual or explicitly isolated demo tenant data, working quick actions and brief.
- [ ] UIR02-T03 Build one end-to-end case workspace: source → claim → critical question → assessed alternative → reviewable draft, plus honest event history/replay.
- [ ] UIR02-T04 Produce a review pack: desktop/mobile screenshots, short actual interaction recording, mode ledger, accessibility/performance report and original golden-case checks.

Gate: no static local success claims; actual persisted/contract-tested case transitions and source links; four original payable outcomes preserved. Demonstrate clear state difference between recorded workflow, model operation and owner authority. This slice establishes quality for subsequent screens. Review pack is concrete; do not stop at wireframes. Checkpoint.

### UIR-03 — Complete AI/evidence workspace and global Copilot

Dependency: UIR-02; real-agent upgrades, if chosen, need independently verified backend prerequisites. Tasks:

- [ ] UIR03-T01 Cases list/detail, evidence capture/review and authorized source viewer with available locators; safe unsupported-format states.
- [ ] UIR03-T02 Run detail/list+map, real event ordering, stale/error/budget/cancel semantics where supported; deliberate replay and mode disclosure.
- [ ] UIR03-T03 Copilot drawer/full-page shared session, attachments/voice transcript, source citations and missing-field clarification.
- [ ] UIR03-T04 Action review queue, version invalidation, approval/execution separation, canonical assessment shared across every AI surface.

Gate: deep links reload correctly; keyboard sources/citations; duplicate/out-of-order events handled; no forbidden UI inference; failed send preserves draft; unknown payment amount blocks. Genuine live mode requires real receipt evidence, not merely a browser animation. Checkpoint.

### UIR-04 — Daily commerce and money

Dependency: UIR-01/02 and relevant contracts. Tasks:

- [ ] UIR04-T01 Sales and due collection workflows with persisted receipts and accurate account updates.
- [ ] UIR04-T02 People directory/account detail, promises/disputes and portal-link workflow.
- [ ] UIR04-T03 Money accounts, transfer/expense/withdrawal/supplier payment and cash-close review.
- [ ] UIR04-T04 Auth/onboarding completed against actual supported setup; session expiry/role/tenant recovery through these workflows.

Gate: sale vs collection totals remain distinct; account-specific shortages; failure/timeout/double-click and permissions verified; no fake offline success; source-backed receipt after refresh. Checkpoint.

### UIR-05 — Buy, receive, stock and demand

Dependency: UIR-03/04 contracts and authoritative receiving decision. Tasks:

- [ ] UIR05-T01 Buying comparison and draft order with interpreted terms, exact normalized costs and cash scenario link.
- [ ] UIR05-T02 Receiving count/discrepancy/return/credit recovery with one authoritative inventory write boundary.
- [ ] UIR05-T03 Stock table/SKU details/import preview/reorder links and incomplete-cost states.
- [ ] UIR05-T04 Demand capture/normalization/analysis linked to buying; no unmet-request revenue.

Gate: quote conditions stay conditional; received vs usable preserved; rejected/unapplied credits cannot reduce payable; duplicate allocations rejected; draft/reorder is not received stock; tables and forms work at mobile widths. Checkpoint.

### UIR-06 — Planner, reports and decision explanations

Dependency: UIR-04/05 usable canonical data. Tasks:

- [ ] UIR06-T01 Baseline/alternate runway chart+table, actual/commitment/promise/prediction separation and source/date inspection.
- [ ] UIR06-T02 Spending/purchase scenario edits, exact deltas, save/load and stale-baseline behavior.
- [ ] UIR06-T03 Reports/CSV exports and source-backed optional commentary, cost-data completeness.
- [ ] UIR06-T04 Cross-links from Buying/Money/Copilot preserve context and scenario assumptions.

Gate: promise toggle does not alter actual balances; no synthetic failure fallback; exact results agree with domain fixtures; incomplete history has honest state; chart keyboard/table equivalence and exports tested. Checkpoint.

### UIR-07 — Inbox, voice and everyday operations

Dependency: UIR-03/04. Tasks:

- [ ] UIR07-T01 Actionable inbox/deep links/read/snooze/resolve and actual unread status.
- [ ] UIR07-T02 Daily brief and opt-in voice/recording controls with transcript, language/availability/failure preferences.
- [ ] UIR07-T03 Reservation pick list, containers/deposits, handover and supplier-change review with real adapters.
- [ ] UIR07-T04 Link underlying business resolution to notifications/briefs without falsely resolving obligations.

Gate: snooze != paid; pick != sale; transcript always usable; no audio autoplay; unavailable speech/permission gracefully handled; movements/deposit units and callbacks verified. Checkpoint.

### UIR-08 — Help, connections, portal, demo and settings

Dependency: UIR-03/04 and per-operation capability contracts. Tasks:

- [ ] UIR08-T01 Document/checklist Business Help with scoped, dated, source-linked guidance and corpus limitations.
- [ ] UIR08-T02 Connection capabilities, diagnostics boundary and supported preferences/settings persistence.
- [ ] UIR08-T03 Lightweight customer portal with verified payment/dispute/error states.
- [ ] UIR08-T04 Isolated guided demo/reset/exit and remaining route/failure/translation coverage.

Gate: no unsupported live connector/legal claim; public token cannot access merchant tools; payment redirect not final success; preferences survive as specified; demo cannot expose real tenant data. Checkpoint.

### UIR-09 — Competition-quality validation and handoff

Dependency: all applicable earlier gates. Tasks:

- [ ] UIR09-T01 Actual browser regression across critical journeys, BN/EN and360/390/768/1024/1440; screenshots and interaction recordings from current build.
- [ ] UIR09-T02 Keyboard/screen-reader/zoom/contrast/motion checks; low-end/slow-network lab profile and bundle/performance report.
- [ ] UIR09-T03 Verify provider/runtime modes and run applicable domain/API/component tests. Mark unavailable live capability blocked; do not pass it using a mock.
- [ ] UIR09-T04 Final route/state/CTA audit, competition walkthrough, known limitations and resume handoff; checkpoint and receipt publication.

Gate: every screen/feature in sections6–7 accounted for; no console/runtime blockers in exercised flows; no generic placeholder screen or unmounted approved feature. Real browser runner fails on deliberately broken assertion. Measured results tied to code revision and fixture/mode. UI completion and external integration completion remain distinct. No automatic deployment/visibility change.

## 14. Verification and evidence protocol

Relevant command baseline (inspect current manifests before execution):

```powershell
pnpm.cmd --filter @shongoti/web test
pnpm.cmd --filter @shongoti/web build
pnpm.cmd check:css
pnpm.cmd test:domain
```

Run affected backend suites for actual behavior/contract changes (`test:confidence`, `test:agents`, `test:copilot`, buying/receiving/etc.) and broader API regression when shared financial/session paths change. Do not run live providers/payments merely for screenshots. A mocked API test and an authenticated real API journey need separate labels. Replace/implement the browser-runner contract before using `test:e2e` as a gate; no command here claims that journey already exists.

Required journey evidence:

1. Landing → isolated demo/auth → Today → real quick action → persisted receipt after reload; network failure retains input.
2. Evidence upload/review → source-linked case → missing inclusion clarification → correct alternatives → new assessment → owner review; stale draft cannot execute.
3. Copilot missing-amount request asks clarification; source links open; null/blocked confidence does not disappear or become positive.
4. Quote → order draft → partial/damaged receiving → accepted credit → exactly-once invoice allocation; inventory and payable not conflated.
5. Expense/purchase scenario → reserve/deadline delta; promise lane changes only scenario, not actual funds.
6. Notification → underlying task → actual resolution; brief voice opt-in and unavailable voice fallback.
7. Permission/tenant boundary, expired session, public portal token and demo isolation across direct URL/deep-link reload.
8. Completed run displays history; replay is labeled; live/cancel claims only with corresponding actual runtime evidence.

Each phase stores under `docs/evidence/ui-redesign/UIR-XX/`: command/cwd/exit code, revision and dirty-tree context, sanitized summary, screenshots/recording references, fixture/mode, exact limitations, checkpoint and receipt. Capture no secrets or real merchant PII. A screenshot proves appearance at that state, not posting accuracy or model quality.

Proposed performance budgets, to measure and ratify at UIR-01: avoid >10% regression to baseline initial compressed JS (85.24kB from this build) without a documented reason; route-split noncritical graph/voice/chart tooling. Keep fonts/images separately budgeted. Web Vitals targets are LCP<=2.5s, INP<=200ms, CLS<=0.1 at field p75 when available. Lab runs document device/network/build/cache profile; no field-quality claim from one Lighthouse score. Prefer responsive controls over decorative motion under load.

Design review checks: visible hierarchy, distinct task layouts, Bangla legibility, original illustration consistency, immediate financial data, meaningful agent states, readable sources and owner authority. Automated accessibility scores alone do not pass keyboard, screen reader or cognitive usability.

## 15. Scope and approval

This is a full UI/interaction redesign on the existing product, with necessary feature wiring and explicit contract repairs. It does not authorize a new ledger, unrestricted autonomous money movement, copied reference assets, new paid subscriptions, public deployment or claims of real merchant validation.

Approval would lock this overall direction and phase structure. The first implementation deliverable is UIR-00's verified contract map, then the shared system and signature vertical slice. Where backend facts contradict the desired live AI experience, the implementer must report and address the real prerequisite or ship an explicitly limited history mode; decoration is not a substitute.

**Current state: plan prepared; all UIR tasks not_started; no application UI, dependency, existing progress tracker or landing branch was changed by this planning work.**
