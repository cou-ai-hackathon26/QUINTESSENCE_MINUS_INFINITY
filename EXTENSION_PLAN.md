# Shongoti extension build contract for Antigravity

Version: `extension-v1`, prepared **23 November 2026, Asia/Dhaka**.
Repository: `https://github.com/sakibul-shovon/Shongoti.git`.

**Build on the existing application. Do not start a new project, replace the stack, discard existing features or mark features complete from documentation.** This file implements the user's approved expansion scope through new Phase **13–26**. Existing Phase 00–12 IDs, history, financial rules and acceptance obligations remain in force. The authoring of this handoff does not complete Phase 13 or any application feature.

Read [AGENTS.md](AGENTS.md), [START_EXTENSION.md](START_EXTENSION.md), [the original plan](plan.md), [the human tracker](docs/PROGRESS.md), [the machine tracker](docs/progress.json), [extension progress](docs/EXTENSION_PROGRESS.md), [decisions](docs/DECISIONS.md), [integrations](docs/INTEGRATIONS.md), [known issues](docs/KNOWN_ISSUES.md), [validation](docs/VALIDATION.md) and [Git checkpoints](docs/GIT_CHECKPOINTS.md). Supporting rationale and dated research are in [the innovation review](docs/research/2026-11-23-product-innovation-review.md).

## A. Execution contract: discover, resume, verify, publish

1. Work inside `Shongoti`, preserving sibling `../archive/`. Inspect working-tree changes, branch/history, actual origin and remote refs when accessible. Never reset, blindly stage or overwrite other work. The source baseline inspected for this handoff was `8d4c122d712edbca4adad998090727779bef1dd0`; inspect what exists now rather than checking out that revision.
2. Read trackers, then verify their claims against actual source, migrations, meaningful tests, result timestamps/code context and published receipts. A phase commit is evidence of publication, not execution correctness. Report the current observed state and next task briefly, then do the work.
3. Select the earliest unblocked task whose actual prerequisites pass. Implement and test incrementally. All tasks start `not_started` in this extension; determine how much has subsequently been built on every resume. Reuse verified work instead of rebuilding it. Preserve reopened original P04/P05/P11 obligations and explicitly link their repairs to extension evidence.
4. Every completed task needs real evidence. Use statuses `not_started`, `in_progress`, `blocked`, `complete`. Missing credentials, runtime, browser, corpus or hosting mean the corresponding execution gate is blocked/not_run. Do not substitute fixture output or a zero exit code for a real result.
5. **After every verified phase, commit AND push to GitHub**, then publish its checkpoint receipt using `docs/GIT_CHECKPOINTS.md`. Milestone footer: `Shongoti-Phase: 13` through `26`; receipt footer: `Shongoti-Checkpoint-Receipt: XX`. Preserve earlier checkpoints and use a new amendment commit for repaired legacy work. Never force-push, change visibility, backdate, or rewrite history.
6. Publication sequence: tests → sanitized evidence/trackers → reviewed milestone commit → normal push → actual remote verification → receipt/tracker commit → normal push → verify final remote tip. Keep the phase incomplete until both work and publication gates pass. A verified but unpublished phase cannot be silently bypassed.
7. When an external gate is blocked, first finish available local work. A phase may have a clearly labeled **partial checkpoint** with a `Shongoti-Partial-Phase: XX` footer and ordinary push, but must remain incomplete. Only the explicit independent-task allowances in section J permit local work beyond an incomplete predecessor. Record the exact dependency satisfied, mode and blocker. Partial publication is never the completed-phase receipt.
8. Every session updates both human trackers, `docs/progress.json`, relevant decisions/integration/issue entries and exact next task. A completed task from a prior session must not be silently downgraded or trusted without checking evidence relevance. Continue unblocked work; do not end at another proposed plan.
9. Never read secrets into reports or commit `.env`, tokens, private merchant records or sensitive provider payloads. Use synthetic fixtures with explicit labels. No real merchant access was available during planning; adoption, savings and willingness to pay remain unvalidated.

Authority: user instructions first, then AGENTS safety/financial/publication rules. This file is the current **additive extension execution contract**; `plan.md` remains the original product/domain and Phase 00–12 contract. For extension sequencing and new feature definitions, use this file. Resolve a genuine conflict with a dated decision; do not erase either plan or invent approval.

## B. Source map and observed baseline

Existing stack recorded in D004: React/TypeScript/Vite, FastAPI/Python, SQLAlchemy/Alembic, PostgreSQL with SQLite offline boundaries. Inspect installed manifests/lockfiles before relying on versions. Do not introduce a second ledger, a new app framework or microservices to add agent labels.

| Existing area to inspect/reuse | Current source anchors | Extension responsibility |
|---|---|---|
| Merchant interface/routing | `apps/web/src/App.tsx`, `pages/TodayDashboard.tsx`, `MoneyPage.tsx`, `SalesPage.tsx`, `PeoplePage.tsx`, `StockPage.tsx`, `ReportsPage.tsx`, `FuturePlannerPage.tsx` | Preserve working routes, exact numbers, scenario distinction and bilingual behavior |
| Shared UI | `components/Navbar.tsx`, `Sidebar.tsx`, `Badge.tsx`, `Card.tsx`, `i18n/translations.ts` | Add navigation, confidence, activity and capture components consistently |
| Exact domain | `apps/api/app/domain/{money,ledger,merchant,reconciliation,liquidity,scenarios}.py` | Keep arithmetic, permissions, postings, allocation capacity and scenario tools deterministic |
| Persistence and identity | `persistence/models.py`, `core/{auth,permissions,database,config}.py`, `apps/api/alembic/versions/` | Add migrations without dropping existing data; enforce tenant/role checks on every new path |
| Evidence | `ingestion/{adapters,schemas,storage}.py`, `api/v1/evidence.py` | Implement genuine provider/modality routing, source locators and review; reuse private source storage |
| Stock/purchase/report | `api/v1/stock_and_reports.py`, `adapters/forecast.py` | Add actual/partial receiving, conditions and availability; preserve accepted returns/WAC behavior after verification |
| Action/portal/integration | `api/v1/actions_and_portal.py`, `adapters/sslcommerz.py` | Reuse approval/version/idempotency boundary; do not infer universal wallet/messaging capability |
| Tests/runners | `apps/api/tests/`, `apps/web/src/tests/`, `tests/fixtures/contracts/`, `scripts/` | Retain independent golden cases; repair runners that merely assert files/text or emit simulation |

These are observed file paths, not a certification of their behavior. Newly named files, routes and commands below are **targets to create**, not claims they already exist.

Known source findings to recheck at session start:

- Configured `AIModelAdapter` currently raises without an SDK/HTTP call; the unconfigured path can emit fixed fixture answers. A key alone cannot implement inference.
- Evidence upload currently forwards extracted native text; image/audio bytes are not sent to a real multimodal path.
- `StructuredClaimExtraction.confidence` is model self-report. It is not a calibrated confidence system and is not currently a sufficient persisted confidence record.
- `scripts/eval-ai.js` does not execute model evaluation; `scripts/run-benchmark.js` reads gold labels and assigns simulated correctness/latency/cost. Preserve old artifacts as historical simulations and supersede their empirical claims.
- `scripts/test-e2e.js` checks source/CSS and runs web unit tests/build; these do not establish real-browser workflows, layout or accessibility. Implement an actual browser gate.
- `scripts/verify-integrations.js` checks environment presence, not actual provider behavior. Configuration is distinct from verified access and task quality.
- Forecast code uses a single final-seven-observation holdout but labels it rolling-origin; prediction ± MAE is not demonstrated probability coverage.
- Current receiving takes draft quantity as received quantity; actual/partial receipt and shortage/dispute events need separate records.
- Trackers and integration register have contradictory historical completion/access claims. Phase 13 must reconcile these with observed evidence rather than silently choosing the optimistic version.

## C. Product scope: one connected merchant workflow

Keep original supplier-bill reconciliation, daily sales/dues, cash/digital account tracking, stock, reports, action approvals, portal and spending-impact scenarios. The original four payable outcomes for a BDT 25,000 demand with a BDT 4,000 payment and BDT 3,000 accepted return remain 25,000/22,000/21,000/18,000 depending on prior inclusion. Receipt acknowledgment is not proof of inclusion. A reserve cannot change what is owed.

Add all of these through the phases:

1. **Buying Desk:** compare uploaded/text/audio supplier offers, normalized packs, bonus conditions, cash/credit terms, delivery, returns and supported cash impact; draft targeted clarification and reviewable orders.
2. **Receiving & Claims:** compare promise/order, actual receipts, invoice and supplier replies; handle shortage, damage, bonus goods, partial delivery, accepted credit and exactly-once bill application.
3. **Demand Memory:** capture customers who did not buy, pack preference and stockout windows; use recorded unmet requests honestly in buying decisions and evaluated availability-aware forecasts.
4. **Return and Credit Recovery:** supplier-specific return conditions/deadlines, evidence packets and accepted-versus-applied credit follow-up.
5. **Voice Transaction Review:** parse mixed old-dues/new-sales/split-payments/returns into separate proposed events; preview corrections and approve through the existing financial boundary.
6. **Visible Agent Teamwork:** real coordinator task allocation, parallel specialists where useful, evidence findings, handoffs, waiting/retry/failure states and resumable case history.
7. **Shongoti Copilot:** text/voice chat grounded in selected shop/case context, cited records, live ledger tools, scenario tools and reviewable draft actions.
8. **Hybrid RAG:** dense semantic + real keyword/exact retrieval, rank fusion, source/version/scoped history, tenant filtering and honest insufficiency. Optional reranking must earn its complexity.
9. **Confidence system:** visible evidence-support score plus critical-field readiness; score changes affect retrieval, investigation, clarification and available proposals, never financial authorization.
10. **Notifications and voice:** actionable durable inbox, permission-aware push, opt-in spoken alerts, factual on-demand/scheduled-ready morning/evening briefs and follow-up conversation.
11. **Business Help Desk:** document vault, sourced local renewal checklist, notices/contract explanation and dispute evidence packet; maintained official-source RAG and explicit jurisdiction/date gaps.
12. **Additional operations:** selected customer message→order/picking draft; evidence-based close/shift handover; supplier promise/change impact; returnable crate/bottle/deposit records where relevant.

First useful experience is one supplier case, not mandatory full-business migration. Every workspace needs empty/loading/error/unknown/disconnected states, Bangla/English text and accessible phone layouts. A useful everyday deterministic feature does not need an LLM on every interaction.

## D. Confidence: required visual and behavioral contract

### D1. Meaning and UI

Initial displayed label: **“AI confidence — প্রমাণের সমর্থন: ৮৫/১০০”**, with a short explanation that it is a **versioned evidence-support index, not an 85% probability of correctness**. Do not append a percent sign, invent a number, derive it from token probabilities, or reuse `model_self_confidence` as public confidence. A future independently evaluated calibration may add a separate probability field; it cannot change this label silently.

Show an accessible badge and bar with text/icon, not color alone: strong (85–100), review (60–84), limited (0–59), unavailable (null). These are **initial policy thresholds**, not research-derived accuracy guarantees. Expand for supported claims, missing critical facts, conflicts, source versions, assessment method and why the next action was chosen. Show field-level state next to important amount, invoice, pack, payment applicability, prior inclusion and return-acceptance claims.

For “what is my cash balance?”, show canonical ledger source/as-of time and reconciliation freshness; do not imply exact arithmetic is a model prediction. For a scenario, show input assumptions separately from interpretation support and evaluated forecast uncertainty. For legal material, show source applicability/date status; a high score cannot certify legal correctness.

### D2. Versioned initial scoring policy, `evidence-support-v1`

The score service takes the **canonical required claim list for the decision type**, not a list chosen by the answering model. Required-but-missing facts remain in the denominator. Register criticality in code/config with reviewed tests; amounts, entity/document links, allocation applicability/inclusion and decision-changing offer/legal scope are critical. Claim weights: critical = 3, other = 1. These are explicit product policy choices, to tune using development evaluation and version with migrations/config history.

Registry coverage must include: evidence extraction (source/entity/reference/value/unit); supplier settlement (bill identity, payment/return applicability, acceptance and prior inclusion, allocation capacity); buying (SKU/pack, quantity/price, relevant bonus/payment/delivery scope); receiving/credit (order, actual count, disputed versus accepted remedy, exact bill application); compound voice events (party, event type, amount/unit, payment allocation); sourced business-help answers (authority, jurisdiction, activity, effective date and source-backed meaning). Optional conditional fields can be excluded only by a validated explicit applicability fact, not by the answering model omitting them. Unsupported question/intent types yield an unavailable assessment until a reviewed registry exists. Free-form answers cannot inflate confidence by selecting only easy claims; factual claims in the answer must also be checked against the required set and citations.

Each claim has state `supported`, `unknown`, `conflicted` or `unsupported`, original source locator(s), entity/scope/version checks, evaluator type (`deterministic`, `model_rubric`, `human`), method version and reasons. Supported means the assessed source supports **that specific claim and relationship**, not merely that a number occurs on the page. Model-rubric support remains fallible and must be identified as such. Hash/source availability alone cannot establish truth or authenticity. A copied summary cannot verify itself. Human review has provenance; it does not automatically make every other field supported.

For a nonempty assessable claim list:

`base = floor(100 * sum(weights of supported claims) / sum(weights of all required claims) + 0.5)`

If any required critical claim is unresolved/unsupported/conflicted, cap displayed score at **59** and set decision readiness to `needs_clarification`. A critical deterministic validation failure sets `score = null` and readiness to `blocked`. Critical cross-document contradictions remain blockers even if most other claims are supported. No averaging across agents may remove them.

No accessible evidence, unreadable necessary input, failed provider, empty required-claim definition or stale case version means `score = null`, an explicit reason/status, and no fabricated numeric fallback. A refreshed assessment must use the current case/source versions. Derive band and next-action policy in deterministic code; the LLM cannot assign or raise them. Keep raw retrieval similarities, ASR uncertainty and model self-ratings as separate diagnostic signals, never interchangeable probabilities.

Example contract: two critical and three ordinary required claims have total weight 9. If one critical plus all ordinary claims are supported, base is 67; unresolved other critical claim caps score at 59 and prevents a definitive recommendation. Supporting all five gives index 100, **not guaranteed correctness** and not authority to post/send. If the source is revoked, the old assessment becomes stale and the public score becomes null until reassessed.

### D3. Behavioral policy

| Assessment | Required behavior |
|---|---|
| Strong + no critical blocker | Cited answer or draft; any state/external action still uses explicit review, permission, version and idempotency checks |
| Review | Show provisional answer and missing facts; optionally make one bounded additional retrieval/verification pass before asking |
| Limited or critical unresolved | Present supported partial findings and one decision-changing question; withhold definitive ranking/payable/legal conclusion |
| Unavailable/stale/validation failure | Explain the exact unavailable or invalid state; retain manual review and permitted factual tools; no guessed answer or success |

Initial case budget: at most 8 model calls, 12 read-tool calls and 1 clarification question per synchronous round, plus an explicit configured monetary ceiling. Thresholds/caps must be tunable and logged. A user reply resumes a new round with a versioned cumulative budget; it does not grant infinite retries. Score-driven escalation may spend remaining budget, not recursively spawn agents until the number looks high.

Persist claim, retrieval, answer, plan and score versions. A correction invalidates dependent answers/drafts/notifications and triggers scoped reassessment. The UI explains the change (for example, “supplier reply resolved credit timing”) rather than claiming learning or increased model intelligence.

Canonical assessment response must include `assessment_id`, `tenant_id`, `case_id`, `case_version`, `answer_or_plan_version`, `policy_version`, `kind: evidence_support_index`, `base_score`, `score`, `band`, `readiness`, required-claim states/weights/source locators, evaluator/version, cap/null/blocker reasons, `assessed_at`, `next_action` and `calibrated_probability` (initially null). The service derives this response; model output cannot override its policy fields. Readiness values are `ready_for_review`, `needs_review`, `needs_clarification`, `blocked`, `unavailable`. No accessible evidence is different from assessed low support. Noncritical unknowns remain visibly unknown even when the overall index is strong.

The confidence panel must explain routing: for example, “একটি গুরুত্বপূর্ণ শর্ত অজানা, তাই supplier-কে প্রশ্ন প্রয়োজন।” The corresponding case actually enters `waiting_user` and its definitive recommendation remains withheld. A later supported reply changes the case version and can enable a reviewable draft. Test this complete transition; a changing colored bar without the state/action change does not satisfy the requirement.

### D4. Evaluation and calibration

Independently label claim support, critical omissions and actual answer correctness. Measure whether low/limited cases route to the right question and whether incorrect definitive answers remain in the strong band. Report coverage versus error, source alignment, false-high-confidence count and denominators. Do not change thresholds on held-out cases.

A true correctness probability needs a separately trained/validated calibration mapping with family-separated fit/evaluation data, reliability plots, bucket counts/uncertainty and appropriate proper scoring metrics. Insufficient data keeps `calibrated_probability = null` and UI wording unchanged. Brier/log-loss improvements alone do not establish universal calibration; see [official calibration guidance](https://scikit-learn.org/stable/modules/calibration.html). A new model/prompt/corpus/policy version may invalidate calibration. No claim of 95% reliability without applicable evidence.

## E. Shared architecture and data contracts

Use the modular monolith and existing transactional database as the source of truth. Add a bounded worker/outbox only as required; do not require a fleet of services. Reuse current accounts, parties, products, evidence and approval tools after checking actual contracts. New package/module names below are proposed: `services/cases`, `confidence`, `retrieval`, `agents`, `copilot`, `notifications`, `business_help`.

Proposed entities, to map into actual SQLAlchemy models/migrations rather than duplicate existing equivalents:

- Case and CaseVersion; typed EvidenceClaim and SourceLocator; ClaimRelation (`supports`, `contradicts`, `supersedes`, `applies_to`), ClaimAssessment and ConfidenceAssessment.
- DocumentChunk, IndexVersion/Job and embedding metadata; scoped SupplierTerm and reviewed ProductAlias. Preserve original source plus parsed/canonical values.
- AgentRun, AgentTask and append-only AgentEvent; Conversation, Message, ToolReceipt and ProposedAction references.
- Offer/OfferLine/Condition; order references, separate Receipt/ReceiptLine and Discrepancy/Claim/Resolution/CreditApplication references. Keep planned, delivered, damaged, accepted, promised and applied states separate.
- UnmetRequest, AvailabilityWindow and forecast evaluation record; return batch/date/condition records.
- Notification/EventDelivery/Preference and Brief/Snapshot references; customer order/picking/reservation references; handover note; returnable item/deposit movements.
- BusinessDocument, VerifiedChecklist, OfficialSourceVersion and applicability/review status.

Every row that contains shop data has tenant ownership; relevant records also need actor, timestamps, version, provenance, state and audit history. Define exact units/rounding policies and referential constraints. Vector rows, cache entries, events, audio and exported packets inherit access restrictions. Private file hashes are integrity aids, not proof of authenticity. Migrations are additive and tested on fresh and populated databases; do not infer “next migration number” without inspecting current Alembic heads.

### E1. Hybrid retrieval

Native PDF text first; real OCR/multimodal path for scans/images; real ASR/audio path for voice. Chunk by meaningful invoice/line/term boundaries and retain page/box/timestamp provenance. Preserve Bengali originals; normalize Bengali/ASCII digits and reviewed Banglish aliases for searching. Do not combine different invoice entities into a single authoritative fact.

Run exact/entity and keyword retrieval alongside dense multilingual retrieval. Filter tenant/role/scope **before** retrieval/reranking; check source versions/effective dates and invalidate deleted/revoked records/caches. Fuse ranked candidates with RRF; proposed initial `k=60`, tuned on development cases only. Optional cross-encoder reranker is an evaluated adapter, not a mandatory heavy dependency. The [pgvector documentation](https://github.com/pgvector/pgvector#hybrid-search) supports Postgres full-text + vector fusion. PostgreSQL `ts_rank` is not BM25. If choosing BM25, record an actual compatible implementation and verified Bengali behavior; no imaginary extension/API.

Use the existing PostgreSQL for pgvector if actually available. SQLite offline/test boundaries may use a clearly scoped lexical/injected embedding double; they do not prove deployed vector-index behavior. Verify actual PostgreSQL extension/permissions and multilingual embedding output dimensionality/model version. Keep official compliance corpus separately governed from untrusted shop content. Retrieval relevance is not truth or legal authority.

### E2. Agents and visible activity

Coordinator dynamically assigns relevant work to Terms/Evidence, Stock/Demand, Reconciliation and Skeptic specialists. A Clarifier may be coordinator functionality rather than another paid role. Give each an objective, bounded tools, context scope, structured output and stopping condition. Same-model roles are not independent truth guarantees. Deterministic cash/ledger/stock tools are not LLM agents.

Agent event schema: tenant, case/version, run/task ID, parent/dependencies, monotonically ordered event ID, role, business question, state, timestamps, safe tool/source references, concise finding and failure reason. States: queued/running/waiting_tool/waiting_user/succeeded/failed/cancelled/skipped. Use actual backend task state. No timer-driven success, fake percentage, prewritten conclusion or exposed private chain of thought.

Provide a real activity stream with authenticated reconnect/replay, cancellation, duplicate-event handling and current snapshot. Prefer an implementation compatible with current auth: native `EventSource` cannot be assumed to attach an arbitrary Authorization header; choose verified cookie/fetch-stream or another documented approach without leaking long-lived tokens into URLs. Background tasks survive appropriate worker restarts or fail visibly. Parallelize only independent reads; never race conflicting stock/ledger writes.

### E3. Copilot and proposed endpoints

Routes below are **planned contracts**. Inspect collisions and decide actual request/response schemas before implementing. Suggested UI routes: `/app/buying`, `/app/receiving`, `/app/cases/:id`, `/app/copilot`, `/app/notifications`, `/app/business-help`; integrate capture, briefs, return and demand views with existing pages.

Suggested API families under current `/api/v1`: `/cases`, `/cases/{id}/events`, `/cases/{id}/assessments`, `/search`, `/copilot/conversations`, `/offers`, `/receipts`, `/claims`, `/demand-requests`, `/notifications`, `/briefs`, `/business-help`. Reuse existing transactional endpoints through typed tools; do not expose unrestricted SQL/filesystem/network tools or let chat select its tenant/role.

Copilot routes intents to current ledger queries, retrieval, case investigation, scenarios or a reviewable action draft. Every material factual claim cites a source or current tool receipt/as-of time. Separate actual/pending/obligation/promise/forecast/scenario. Confirmed application posting occurs only through the existing reviewed executor, not an LLM tool with direct writes. Clarification resumes durable state; a new conversation cannot bypass limits or reuse another tenant's cache.

### E4. Notifications, voice and business help

Transactional outbox produces durable notification events with deduplication/version, recipient role, priority, resolution state and actions. Readiness/confidence changes can update a notification, but unsupported speculation cannot become an urgent financial fact. Provide in-app inbox first; actual permission-aware push after compatible service-worker/provider setup. Delivery accepted/read/spoken are distinct states. Quiet hours, grouping, mute, privacy-safe previews and revocation are required.

Voice brief uses an exact ledger/case snapshot and source cards. AI can prioritize/summarize evidence; code checks spoken amounts/dates and separates uncertainty. Use device TTS only when a suitable voice is observed; otherwise a verified provider or text-only mode. No guaranteed voice while the website is closed. No private customer names/balances on shared speakers or lock screens by default. See [notification permission](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API) and [device voice discovery](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices).

Business Help starts with vault/checklist/renewal and notice/contract explanation. Ask jurisdiction, activity and dates. Approved corpus tracks authority, publication/effective/access/review dates, amendments and supersession. Undated/outdated/conflicting material yields an explicit gap. Do not infer tax thresholds, legal liability, universal registrations or guaranteed return rights. Sources such as [NBR](https://nbr.gov.bd/faq/vat-faq) and local authority pages are candidates to reverify, not an already validated legal corpus. Packets/drafts are not official approvals; submissions, fees and complaints require their own authorized workflow.

## F. Ordered extension phases

There are **14 new phases, 13–26**. All tasks below are required for the defined scope; optional model calibration or provider choices must retain honest unavailable states when unverified. Preferred phase order follows the table; task-level independent allowances appear in J.

| Phase | Preferred prerequisites | Milestone |
|---|---|---|
| 13 | Existing repository | Evidence audit, repaired verification contracts and upgrade baseline |
| 14 | 13 | Genuine multimodal inference and original reconciliation repaired |
| 15 | 13; live checks use 14 | Shared cases, provenance and confidence policy |
| 16 | 15; real inference adapters from 14 | Tenant-safe hybrid RAG and scoped memory |
| 17 | 14–16 | Bounded agents and visible live teamwork |
| 18 | 14–17 | Cited copilot and compound voice review |
| 19 | 15–18 plus verified money/scenario tools | Buying Desk |
| 20 | 19 plus original reconciliation gates | Actual receiving, returns and credit recovery |
| 21 | 19–20 plus verified stock history | Demand Memory and honest future impact |
| 22 | 18, 20–21 | Actionable notifications and voice briefings |
| 23 | 18, 20–21 | Customer orders, handover and returnable deposits |
| 24 | 16, 18 plus reviewed official-source collection | Business Help Desk |
| 25 | Required implemented 14–24 paths | Fair AI/RAG/confidence/agent evaluation and real browser gates |
| 26 | 25; hosting access for deployed claims | Release validation, Git evidence and Antigravity handover |

Each phase section supplies task IDs, outputs and acceptance gates. Store results under `docs/evidence/phase-XX/`, with task/check IDs, real command, cwd, UTC timestamp, exit/outcome, mode, code/tree context, sanitized summary and artifact paths. A mocked run is labeled mock even if it passes.

### Phase 13 — establish the real upgrade baseline

- **P13-T01 — inventory and reconcile.** Inspect every original phase's claimed gate, related code/tests, integration evidence and remote receipt. Create `docs/BASELINE_AUDIT.md` with implemented / observed tested / simulated / blocked distinctions, actual endpoints/data contracts, and a legacy-to-extension repair map. Recheck all findings in B, not just this document's historical source state. Preserve data and contribution history. Audit identity/demo configuration before introducing privileged chatbot tools; client-supplied role/tenant must never confer authority.
- **P13-T02 — make verification honest.** Replace message-only AI/integration runners with structured per-check outcomes; separate configured, attempted, executed and correct. Implement strict release/evaluation modes where failed or required blocked gates return nonzero, while explicit local inventory mode may report blocked without claiming pass. Replace `test:e2e` with an actual browser launcher; keep source/CSS checks under a truthful separate name. Confirm all root command names from G.
- **P13-T03 — execute a relevant baseline.** Run actual existing domain/API/web/type/build checks with configured test database and documented runtime. Record real failures and targeted repairs; never weaken golden fixtures. Test current tenant isolation, role authority and approval/version boundaries. Record browser/provider gates as blocked if unavailable, not “all verified.” Establish database backup/test-copy and migration restore procedure before altering schema.
- **P13-T04 — correct records and publish baseline.** Reconcile `PROGRESS.md`, `progress.json`, `INTEGRATIONS.md`, `KNOWN_ISSUES.md`, decisions and historical report notices. Leave original completed states only where evidence supports them; reopened tasks link exact repair/evidence. Publish the verified Phase 13 checkpoint after its local audit/runner gates pass. An external integration can be explicitly blocked in the baseline without being a required baseline success claim.

**Gate:** reproducible observed baseline and truthful runners exist; no gold-derived model metric or CSS scan is presented as runtime/browser evidence; critical financial/auth violations found by the audit are fixed or explicitly block dependent implementation. Use `pnpm test:domain`, `pnpm test:api`, `pnpm test:web`, `pnpm typecheck`, `pnpm build` and targeted real database/security checks. A baseline report is not proof the repaired feature itself works live.

### Phase 14 — genuine evidence inference and original reconciliation

- **P14-T01 — explicit provider boundary.** Replace implicit fixture branches with injected test doubles confined to test/demo wiring. Add model/provider/version configuration, typed response validation, size/time/cost limits, request/usage receipts, cancellation and bounded retry. Implement an actual verified provider SDK/HTTP path. Check installed types/current official API docs before selecting model IDs, content parts or structured-output settings. No silent offline fallback for ordinary uploads.
- **P14-T02 — genuine media paths.** Forward actual image/PDF/audio content to the supported adapters; preserve page/box/timestamp source locators and original bytes privately. Native PDF text uses its native route; scans require real vision/OCR; audio requires actual transcription/understanding. Keep exact Bengali numerals/currency/unit normalization separate from interpretation. Unreadable/ambiguous fields remain null with reasons.
- **P14-T03 — review and failure integration.** Persist proposed claims, provenance and sanitized provider metadata; source review/correction can open originals and invalidate dependent drafts. Exercise no key, invalid key, quota, timeout, invalid JSON, poor media, unsupported format, malicious embedded instructions and oversized uploads. Ordinary missing-provider UI is unavailable, not extracted/success.
- **P14-T04 — repair original P04/P05 journey.** Run actual synthetic bill, unrelated/reused receipt, payment, accepted return and ambiguous Bangla/Banglish reply through genuine inference→review→original reconciliation→clarification→approved adjustment. Cover all original payable hypotheses, no reply, partial reply, contradiction, prior inclusion and stale approval. Preserve the independent domain engine and exact allocations.
- **P14-T05 — actual provider evidence.** Execute unseen synthetic text/image/audio cases with recorded model/version, response/usage, elapsed time and field correctness. Implement `pnpm eval:ai` as actual requests and scoring; missing access stays blocked. Reconcile repaired P04/P05 task states and publish new amendment evidence without rewriting their historical commits.

**Gate:** real media reaches configured inference; provider outputs differ appropriately on changed inputs; unknowns/failed calls stay explicit; original reconciliation works from actual interpreted evidence and exact tools. Unit/mock tests plus configured-key detection do not pass this phase's genuine-provider gate.

### Phase 15 — cases, provenance and confidence

- **P15-T01 — durable case/claim contracts.** Add additive migrations for case versions, source locators, typed required claims, support/conflict/supersession and assessments. Register canonical decision claim sets and field criticality for reconciliation, offers, receiving, chat and business help. Preserve existing evidence IDs and confirmed ledger facts. Test fresh/populated migrations and ownership checks.
- **P15-T02 — scoring and routing policy.** Implement D's exact `evidence-support-v1` formula/caps/null handling, assessment provenance and deterministic readiness/next-action rules. Persist raw self-ratings separately for diagnostics only. Version model/prompt/source/case/policy references; refuse stale approval/assessment. Conflicting agent verdicts cannot be counted as majority truth.
- **P15-T03 — accessible confidence UI.** Reusable confidence badge/bar/details and field-level chips across evidence review, case results and future copilot answers. Show score reasons, critical unknowns, source links, as-of time and a distinct verified-transactional-data state. Preserve text-only, reduced-motion and both languages. The public label must not imply calibrated probability.
- **P15-T04 — behavioral tests.** Assert the 67→59 cap example, score-null cases, no claims, all-supported-but-still-review-required, high average with critical blocker, source revocation, correction, stale version, failed validator, model self-rating 0.99 with unsupported facts and bounded escalation. Test actual new evidence changing readiness while unrelated facts remain unchanged.

**Gate:** score is derived, persisted and explained; confidence affects real retrieval/clarification/draft behavior; no score bypasses approval or safety. Local algorithm/UI tests can pass independently of model access; genuine inferred-claim assessment evidence is still required for overall phase completion.

### Phase 16 — hybrid merchant memory

- **P16-T01 — ingestion and indexing.** Source-preserving chunks for bills, offers, notes, return terms and audio transcripts; index/model version and idempotent jobs; backfill existing authorized evidence without duplicate semantic records. Add reviewable aliases/digit normalization. Handle delete/revoke/reindex and private-file access correctly.
- **P16-T02 — actual hybrid retriever.** Default architecture is existing PostgreSQL full-text/exact entity filters + pgvector dense retrieval + RRF. Record real extension availability, compatible versions, embedding model/dimensions and language evaluation. Verify query/result shapes; scope filters precede search. Keep a labeled SQLite/test adapter rather than pretending it validates PostgreSQL vector queries. Do not mislabel keyword rank as BM25.
- **P16-T03 — evidence pack and safe answer boundary.** Return source locators, effective scope, conflicts and sufficiency. A copied summary cannot replace an original source. Exact invoice identity beats semantically similar old invoices. Retrieval emits findings for the case/score service; it cannot authorize financial actions. Invalid citations, insufficient evidence and stale terms produce structured gaps.
- **P16-T04 — retrieval evaluation.** Create independently labeled exact-ID, Bengali numeral, Banglish, product-alias, paraphrase, scoped-term, wrong-version and cross-tenant cases. Compare keyword-only, dense-only and hybrid with identical filters; report Recall@k/ranking, exact-ID errors, wrong-scope results, deletion behavior and measured latency. Add reranking only if development evidence justifies it, with separate held-out reporting.

**Gate:** actual persistent retrieval retrieves the right source/entity/version in the configured database; no cross-tenant results; dense/keyword contribution is observed rather than declared. No claim that hybrid is universally superior without actual comparisons.

### Phase 17 — bounded collaboration and visible teamwork

- **P17-T01 — typed tools and role boundaries.** Catalog existing read/compute tools with schemas, permissions and invariants. Implement case coordinator, terms/evidence, stock/demand, reconciliation and skeptic roles with scoped contexts and stopping conditions. Use an application-owned durable state graph within the current Python service first; add a framework only with a justified decision and verified API. Ledger/stock/cash calculators remain code tools.
- **P17-T02 — real task execution.** Coordinator selects needed specialists, parallelizes independent reads and requests a decision-changing clarification. Skeptic receives original sources and structured candidate claims without persuasive proposer narrative. Persist tasks/events, safe tool receipts, retries, budget, cancellation and wait/resume state. Document model-correlated failure risk. One uncomplicated case must avoid unnecessary specialists.
- **P17-T03 — visible Agent Workspace.** Render coordinator's plan, agent cards, dependency edges, parallel work, live state, concise findings and source/tool drilldown. Implement authorized streaming/reconnect/replay with real persisted event IDs. Desktop has a graph/cards plus evidence/outcome; mobile has an ordered accessible timeline. Do not hardcode active agent counts, success, elapsed time or percentage.
- **P17-T04 — collaboration acceptance.** Observe one genuine parallel evidence investigation and one skipped-specialist simple path. Change a supplier reply, resume only affected tasks, re-evaluate score and invalidate stale drafts. Test stream disconnect, duplicate/out-of-order events, cancellation, worker/provider failure, budget exhaustion, malicious source instructions and cross-tenant subscriptions. Browser-test the actual activity/decision screen.

**Gate:** visible activity matches actual backend tools/tasks and durable case state; paused/failed work remains visibly paused/failed; collaboration can be compared with a single-agent baseline. A scripted graph preview is only a UI fixture, never live-agent evidence.

### Phase 18 — copilot and compound voice transaction review

- **P18-T01 — scoped conversations and intent router.** Add durable text/voice conversation context tied to shop and selected case/entity. Route questions to current ledger/stock queries, hybrid retrieval, investigation, scenarios or proposed action drafts. Context switching must not accidentally reuse another supplier/order. Allow users to inspect which records the answer used.
- **P18-T02 — sourced answers and confidence.** Present concise Bangla/English answers, inline citations/tool receipt as-of time, evidence-support badge and unknowns. “How much cash?” uses the current canonical query; “what did the supplier promise?” uses source retrieval. Confidence changes call routing per D. Invalid citation/no evidence results in correction or clarification, not a confident paragraph.
- **P18-T03 — reviewed actions.** Draft an order, proposed financial event, claim or follow-up through typed tools. Preview before/after values, actor/recipient, source, exact units, expiry and versions. Require actual permissions and approval before any posting. A user saying “yes” to one draft cannot approve a different amount/version; model text is never an authorization token.
- **P18-T04 — real voice input.** Record/upload audio with explicit user interaction, actual transcription timestamps and editable preview. Parse compound events, for example old debt collection versus new sale versus split payment. Ask about ambiguous allocation; retries must not create duplicate transactions. Test noisy/poor audio, denied microphone, unavailable provider and text fallback. A single keyword cannot map to a fixed answer.

**Gate:** persisted chat can answer from current facts and original evidence, route based on support and safely prepare actions. Real voice inputs yield reviewable distinct events; no direct chat/voice ledger writes or invented balances.

### Phase 19 — Buying Desk

- **P19-T01 — offer contracts and source scope.** Model supplier/lines, exact SKU/pack conversion, quantity/minimum, bonus goods/conditions, discounts, fees, method, credit period, delivery, batch/expiry and return terms. Preserve conflicting revisions and effective order/date scope. Unknown is not zero/no. Align reviewed product aliases; do not collapse different pack sizes into a fake match.
- **P19-T02 — semantic offer investigation.** Ingest two differently formatted offers, use RAG for relevant scoped history, assign needed agents and ask about decision-changing gaps. “Ten cartons gives one free” remains conditional until the bonus SKU/eligibility is supported. Draft negotiation questions without recording imagined supplier acceptance.
- **P19-T03 — deterministic comparison and impact.** Compute landed/effective unit costs with exact rounding and verified units; use actual account availability, due obligations and permitted payment routes. Compare explicitly labeled demand/credit scenarios. Preserve cash-only constraints, reserve, fees and settlement timing. If no feasible option exists, say so; never change the amount owed or invent credit approval.
- **P19-T04 — decision-to-order UI.** Side-by-side offer/source/score panels, unknowns, agent activity, cash effect and editable order draft using existing purchase tools. A changed condition refreshes only relevant comparisons and invalidates old drafts. Merchant approval creates the intended draft/order state; supplier confirmation remains separately recorded.

**Gate:** an unseen change in pack, bonus scope or cash-versus-credit changes the correct terms/readiness/scenario; arithmetic uses code; unaccepted negotiation is never treated as a deal. No automatic external order or payment.

### Phase 20 — Receiving, returns and credit recovery

- **P20-T01 — actual and partial receipts.** Add received quantities independently from purchase drafts; ordered/received/accepted/damaged/missing/free units and later installments have explicit events. Preserve atomic/idempotent stock/WAC behavior and existing returns. Validate race/replay cases and cumulative quantity bounds; oversupply requires explicit reviewed handling.
- **P20-T02 — evidence investigation.** Compare offer/order, challan, invoice, owner-confirmed counts and selected messages/audio. Agents find incorrect pack, bonus, shortage or inconsistent timing. Code calculates candidate discrepancies. Do not promise reliable hidden-carton counts from photos; source confidence and owner counts remain visible.
- **P20-T03 — resolution and credit lifecycle.** Separate suspected claim, merchant-reviewed claim, supplier reply, accepted remedy, credit note and applied-to-bill. “Adjust next invoice” creates a follow-up, not an immediate reduction. Link to original reconciliation's applicability/prior-inclusion/allocation rules and enforce exactly-once application. No-reply/rejected claims stay unresolved.
- **P20-T04 — return windows and evidence packet.** Interpret supplier-specific batch/invoice conditions and supported dates, calculate deadlines in code, and prepare a source-linked return/dispute packet. Returned physical stock, supplier acceptance and bill inclusion remain distinct. Track promised versus accepted versus applied credit without labeling potential claims as recovered money.
- **P20-T05 — complete operational journey.** Buying draft→partial receipt→discrepancy→clarification→supplier agreement→later statement→approved credit allocation. Test corrections, multiple deliveries, disputed damage, accepted return, reused credit, contradictory/no reply and stale approvals through API/database/browser.

**Gate:** stock and financial source of truth remain consistent under retries and concurrent receipt/credit application; agreed credits reach only the correct bill; evidence supports every accepted interpretation.

### Phase 21 — Demand Memory and supported future impact

- **P21-T01 — unmet requests.** Quick capture records requested product/pack/quantity, observed count type, date, availability/rejection reason and optional order/source linkage. AI proposes aliases/preferences; owner can correct. Deduplicate repeated mentions of the same event without merging separate legitimate visits. Never book these as revenue or guaranteed lost sales.
- **P21-T02 — availability-aware history.** Persist or derive stockout windows from verified movements/counts; distinguish observed sales, available hours, missed requests and genuinely unknown demand. Corrected movements invalidate relevant features. Do not treat an unavailable product's zero sales as ordinary zero demand by default.
- **P21-T03 — forecast and scenario honesty.** Repair the prior rolling-origin/interval claims. Implement actual time-ordered rolling evaluation without future leakage, compare naive/seasonal/moving baselines and only select justified forecasts. Minimum history is task/data-quality dependent, not proof that 14 days guarantees calibration. Public data experiments are separate from shop validation; insufficient data yields counts/scenarios, not fabricated prediction probabilities.
- **P21-T04 — buying impact UI.** Show recorded unmet demand, stock cover, small trial-order options and explicit assumptions beside actual constraints. Compare a present purchase/expense against future obligations and stock availability using existing scenario tools. Display evaluated uncertainty separately from evidence-support score. Explain a recommendation with linked customer-request/stock/term evidence.

**Gate:** no sales double-counting or promise-as-cash, deduplication preserves event meaning, unavailable observations are handled explicitly, and forecast labels match observed validation. Cold-start stores still receive useful factual counts and conditional planning.

### Phase 22 — notifications, voice alerts and briefs

- **P22-T01 — durable actionable inbox.** Emit actual events for unresolved receipt, agreed-but-unapplied credit, confirmed return cutoff, supported cash constraint and invalidated approval. Add outbox/deduplication, role routing, grouping, snooze/resolve, preferences and deep links to the exact case. Stale/resolved alerts must update rather than accumulate duplicate urgency.
- **P22-T02 — contextual priority and delivery.** Code creates factual triggers; AI can summarize the evidence and next question under D's readiness policy. Implement in-app delivery first; browser push requires actual permission/compatible setup and real delivery evidence. Delivery provider acceptance, user display, read and acted states are distinct. No new SMS/WhatsApp/debt-collection integration is assumed.
- **P22-T03 — voice brief.** Generate morning/evening snapshots with exact current figures, supported issues and a few next actions. Provide transcript/source cards and “why/open this case” follow-up through copilot. Validate all spoken numbers/dates against snapshot fields; unknown/recovery promises remain unknown/promised. Scheduled generation and actual playback are distinct; a missed job is not completed speech.
- **P22-T04 — voice privacy and accessibility.** Opt-in spoken alerts, quiet hours, mute, text fallback and privacy-safe shared-device/lock-screen previews. Discover actual Bangla voice availability or use a verified TTS adapter; no forced autoplay/permission request. Test unsupported voices, denied notification/microphone, background limitations, repeated event delivery and stale briefs.

**Gate:** inbox is driven by real business state; actionable links work; brief narration matches actual snapshot and uncertainty; no false background-voice guarantee or private financial announcement by default.

### Phase 23 — additional everyday operations

- **P23-T01 — customer message to order.** Turn uploaded/selected text/audio into product/pack/quantity draft, with availability-aware picking list and approved substitutions. Reservation/release/expiry/retry rules are deterministic; receiving a customer message is not a confirmed sale. Do not claim automatic access to private chat platforms.
- **P23-T02 — close and shift handover.** Reuse actual cash-close discrepancy and stock movement tools. Retrieve related receipts, returns, voids and notes to generate an evidence-linked handover and possible explanations; keep hypotheses distinct from established cause. No employee accusation or fraud label from a model guess. Owner-only financial details remain role restricted.
- **P23-T03 — supplier change watch.** A later delivery/payment/return-condition message proposes a scoped term change. Show affected orders, return tasks, cash scenarios and case confidence. Recompute dependency consequences in code; require review before changing agreed commitments. A message scoped to yesterday's order must not rewrite future orders globally.
- **P23-T04 — returnable items/deposits.** Track crate/bottle/bag movements, damage claims and refundable deposits separately from goods sales. Decide and test the appropriate posting/quantity policy in a dated domain decision using actual existing account contracts. AI parses mixed notes; code enforces exact quantities, refund capacity and idempotency. Enable this workflow only for stores that need it.

**Gate:** each workflow connects to existing stock/ledger/case records without duplicate sales, duplicate reservations/refunds, unauthorized access or invented state. Each has a complete happy and material failure path, not only a decorative card.

### Phase 24 — maintained Business Help Desk

- **P24-T01 — business document vault.** Reuse private evidence storage for business/lease/licence documents, classification/date extraction, reviewed expiry fields and missing-document checklist. Store correct role scope, source, reviewed dates and retention/delete behavior. Not every document or checklist item applies to every shop.
- **P24-T02 — official corpus governance.** Choose a deliberately limited jurisdiction/topic collection first and publish its exact coverage. Reverify authoritative primary sources and record effective/publication/review dates, amendments and applicability. Add a reviewed publication step for new corpus versions. An inaccessible/undated source is not silently treated as current; record the missing verification and keep affected advice blocked.
- **P24-T03 — sourced assistance.** Ask business location/type/relevant dates, explain uploaded notice/agreement clauses, show renewal checklist/official links and prepare factual dispute/administrative packets. Separate what the document says from applicability and suggested questions. Source conflicts, missing facts or insufficient authority trigger clarification/professional/official escalation, not confident tax/legal conclusions.
- **P24-T04 — legal/corpus acceptance.** Test wrong jurisdiction, old rule superseded, conflicting authority, missing document, changed date, malicious uploaded instruction, low support, and irrelevant high-similarity text. No fabricated section number, deadline, fee or registration requirement. Any actual filing/payment/complaint remains outside automatic chat execution and needs separately authorized verified integration.

**Gate:** the bounded coverage and corpus review state are visible, citations open correct source versions, and unsupported applicability is withheld. General legal accuracy is not claimed from a working RAG pipeline; source review is a real completion dependency.

### Phase 25 — fair evaluation, confidence validation and browser verification

- **P25-T01 — independent paired evaluation.** Keep original financial goldens. Correct the prior evaluation runner; add 30 new paired families/60 synthetic cases covering offers, partial receipt/credit, demand, voice, retrieval/confidence and source applicability. Split whole families into 18 development/12 held-out before tuning; disclose synthetic origin and any contaminated legacy cases. Gold answers are accessible only to the scorer, never model input or a tool exposed to agents.
- **P25-T02 — actual architecture/retrieval comparison.** Execute extraction+rules, strong single tool-using model, conditional multi-agent and a real domain engine with gold structured facts. Give equal source/tool access and disclose budgets; run matched-budget and intended-operating comparisons. Run keyword-only/dense-only/hybrid retrieval ablations. Measure actual tool/model output, latency including retry, usage and cost; no fixed injected error or perfect-score assignment. When budget permits, repeat stochastic tests and show variation.
- **P25-T03 — confidence and behavioral evaluation.** Independently review claim support/correctness, missing critical facts, citations, false-high cases, useful clarification, abstention and escalation/cost. Evaluate score bands and version drift on held-out data. Fit/evaluate a separate calibration only if data supports an honest probability claim; otherwise preserve the visible support index and null probability. Test overconfident wrong self-rating and high retrieval similarity with wrong applicability.
- **P25-T04 — real browser and operational tests.** Run complete Buying→Receiving→Reconciliation, chat/RAG, agent resume, notification/brief and bounded business-help journeys in a real browser at 360/768/1440px. Verify keyboard/focus, bilingual labels, reduced motion, scrolling and all loading/error/unknown states. Test two tenants, low privilege, stale approvals, concurrent credits, revoked sources, worker/provider failures and event reconnect. Source scans cannot satisfy this gate.
- **P25-T05 — observed report and release decision.** Report exact denominators/modes, model/index/prompt/score/corpus versions, supported completion, financial errors, citation/field accuracy, appropriate abstention, review effort, latency and real cost. Distinguish team usability trials from merchant outcomes; no invented customer adoption/savings. Prefer the least complex measured architecture meeting requirements; keep specialized path experimental if not justified, while retaining truthful visible teamwork for cases it genuinely executes.

**Gate:** no known invariant/security failure, no simulated metric called empirical, complete relevant observed tests and a changed-input live demonstration. If the live model or maintained legal corpus cannot be evaluated, those capabilities and the overall full-scope release remain incomplete.

### Phase 26 — release and resumable handover

- **P26-T01 — regression and package.** Run relevant full offline/domain/API/web/type/build/migration gates and strict integration/AI/browser gates for claimed capabilities. Audit secrets/private-data exclusions, dependency/runtime versions and actual release configuration. Every known gap is resolved or accurately blocks its claim; do not set overall verified when required live gates are missing.
- **P26-T02 — persistence and recovery.** Validate fresh and populated upgrade migrations, private evidence/index access, worker/outbox recovery, event resume and backup/restore against the actual chosen runtime. Document how to rebuild indexes without rewriting financial history and how to revoke a compromised source/provider.
- **P26-T03 — deployment scope and smoke.** Prepare deploy/runbook locally; publish/deploy only with applicable existing user authorization and actual hosting access. If deployed, execute authenticated end-to-end changed-input smoke with persistence/restart observations and permitted synthetic integrations. A local container is labeled local, not public production. Missing hosting leaves deployed verification blocked.
- **P26-T04 — final handover/checkpoint.** Update feature/status matrix, setup/config placeholder guide, confidence explanation, corpus coverage, provider/cost evidence, eval reports, known issues and the same auto-resume prompt. Reconcile all original and extension task gates with actual source and Git history. Publish Phase 26 milestone/receipt only after its defined gates pass; leave exact next tasks for anything blocked.

**Gate:** another developer can reproduce setup, identify actual capability/access and resume from trackers without invented state. The final summary names the published tip and remaining limitations; no feature is called complete solely because it appears in navigation or this plan.

## G. Commands and observable evidence

Run from repository root with its actual pinned dependencies/interpreter. Existing command names were found in `package.json`; they have **not been executed by this handoff authoring session**. Phase 13 verifies/repairs their actual scope. Do not report a runner as a test merely because it exits zero.

| Interface | Required contract |
|---|---|
| `pnpm typecheck`, `pnpm test:domain`, `pnpm test:api`, `pnpm test:web`, `pnpm build` | Actual current code checks; API discovery must include new tests and relevant existing security/concurrency tests, not a stale hardcoded file list |
| `pnpm db:migrate`, `pnpm db:check` | Actual test/development DB migrations and head verification; never migrate an unidentified real shop database |
| `pnpm verify:offline` | Honest deterministic/mock/type/build gate with exact included checks; no live/provider quality claim |
| `pnpm verify:integrations` | Actual configured sandbox/live behavior and amount/entity checks; an env var presence check is inventory only |
| `pnpm eval:ai` | Actual provider outputs compared with independent expected facts; model/version/usage recorded |
| `pnpm test:e2e` | Actual browser journey, not CSS/file-string assertions; record browser/runtime/viewports |

New **command contracts to create in Phase 13** (do not claim they already exist):

- `pnpm test:extension`: meaningful local extension service/API tests with explicit doubles, real DB tests where declared, and no synthetic inference claim.
- `pnpm test:confidence`: policy/gating/version/authorization tests, including independent handoff fixtures.
- `pnpm test:retrieval`: exact/keyword/vector ownership/version/language and delete tests; declare real Postgres versus injected test mode.
- `pnpm test:agents`: actual local orchestration/events/budgets/replay/cancellation tests with labeled doubles; genuine model runs remain separate.
- `pnpm test:workflows`: buying/partial receiving/credit/demand/voice-draft/order/notification/deposit failure and invariant tests.
- `pnpm test:business-help`: corpus scope/version/citation/insufficiency and unauthorized filing tests.
- `pnpm eval:rag`, `pnpm eval:agents`, `pnpm eval:confidence`: actual retrieval/model/score evaluations, explicit mode and exact denominators. Calibration unavailable is distinct from a passed probability claim.

Create launchers before use and test they discover the relevant cases. Until a suite is implemented, its runner reports `not_run`/blocked rather than empty success. Strict gates use nonzero status for required failed/blocked checks; a useful convention is 0=all required checks passed, 1=failed, 2=blocked. Test these runner failure semantics too. Provider receipts are sanitized: never retain keys, auth headers or private raw records in Git.

Each implementation task runs its relevant new suite plus regressions for changed existing behavior. Run typecheck/build for UI/contract changes and actual database/migration checks for schema changes. Run real-browser checks for interactive claims; screenshots/string scans alone do not pass workflows. After relevant checks pass, broaden only where a change/failure/concern justifies it. Phase 25/26 aggregate required release checks.

## H. Independent examples and acceptance traps

### H1. Confidence fixture contract

[Confidence policy fixtures](tests/fixtures/extension-handoff/confidence-policy-v1.json) are synthetic **input/expected contracts**, not implemented scoring or AI evaluation. Implement against them and add service/UI/permission tests. Keep expectation derivations; do not alter them to match code without a documented genuine correction. Tests must exercise assessment and routing, not just compare decorative badge text.

Required cases include: all supported but approval still required; missing critical→cap; ordinary unknown without false certainty; critical contradiction; no required claims; no source; unavailable provider; stale case; failed deterministic validator; high model self-rating that changes nothing. Responses with no supported answer can be useful abstentions; measure abstention separately from answer-confidence correctness.

### H2. One integrated synthetic buying/recovery story

Use **invented fixtures**, labeled as such, with owner-confirmed units and terms:

- Actual available cash BDT 5,000; wallet BDT 2,000; tomorrow's BDT 3,000 rent requires cash. Do not assume wallet conversion or credit collection is available.
- A offers ten cartons at BDT 500 each plus one identical free carton, cash today. B offers ten at BDT 510 each, seven days credit. Same pack/quality and no extra fees are explicit in this fixture, not assumed for real offers.
- A's immediate total BDT 5,000 leaves zero cash; B creates BDT 5,100 due on day seven and does not spend current cash. Show that later affordability is unresolved without supported assumptions. Effective unit display follows exact rational/rounding policy; account balances never use float approximations.
- Ask whether a supported alternative payment/order size is possible; do not invent supplier agreement. In a **separate selected branch** where A's order was actually approved, owner receives nine paid cartons plus one free while bill charges ten paid cartons. Flag BDT 500 as a candidate discrepancy, not a confirmed recovered sum.
- Supplier says “পরের চালানে adjust করব”; this supports a future follow-up only. Later statement/payment/return evidence must resolve acceptance, bill applicability and inclusion separately. One accepted credit must not be applied twice.
- Add an unmet-request note; it affects demand evidence, never booked revenue. Alter one term/reference/reply unseen in development during a real demo and observe the changed evidence, score, agent activity and supported action.

### H3. Non-negotiable failure paths

| Area | Must demonstrate |
|---|---|
| Financial | Exact paisa/units, original four balances, reused receipt, partial/concurrent allocations, no double credit, no promise as actual money |
| Interpretation | Wrong invoice, bonus SKU unknown, scope-limited old offer, acknowledged payment with inclusion unknown, no/partial/contradictory reply |
| Confidence | No copied self-rating, null when unavailable, critical cap, stale invalidation, reasons/citations, escalation bounded, no permission bypass |
| Retrieval | Bengali/Banglish/IDs, dense look-alike versus exact match, tenant filters, old/revoked source, corpus conflict and bad citation |
| Agents/chat | Real task→event correspondence, partial failure, resume/replay, no unauthorized tool/write, prompt injection and budget exhaustion |
| Operations | Actual partial receipt, accepted vs applied return, stockout data, duplicate missed request/order/reservation, cancelled draft and deposit refund retry |
| Notifications/voice | Duplicate event, resolved alert, quiet hours/privacy, denied permission, unavailable Bangla voice, exact spoken figures and text fallback |
| Business help | Wrong jurisdiction/date, amended/undated rule, missing source, unsupported legal certainty and unauthorized submission |
| Upgrade/release | Populated DB migration, tenant/role isolation, worker restart, real browser layouts and actually configured/deployed capability |

## I. UI contract and feature ownership

- **Landing:** explain the existing merchant workflow plus buying/recovery, cite evidence-backed outcomes only; do not advertise “100% accurate,” autonomous money control or unverified legal coverage.
- **Today:** current canonical facts, next actionable cases, capture button, brief playback and unresolved confidence states. Keep existing money/stock/report navigation usable.
- **Buying:** comparable offer cards/table, source/term drilldown, score/critical unknowns, cash impact, visible agent plan and reviewed draft action.
- **Receiving & Claims:** ordered/actually received/invoiced lines, discrepancy review, return/credit timeline and exact bill application. A one-click receive-all path cannot be the only option.
- **Case / Agent Workspace:** desktop task graph plus evidence/outcome; mobile ordered timeline, expandable source cards and reviewable next action. Show real status with accessible text, timestamps and failure/resume state.
- **Copilot:** global drawer plus full-page route, context chip, text/voice input, cited answer, confidence details, clarification and safe action preview. Persist user intent/case scope across navigation without granting extra access.
- **Stock/Demand:** integrate captured requests/availability/return deadlines into current stock views; distinguish counts, assumptions and evaluated predictions.
- **Notifications / briefs:** bell/inbox, actionable deep links, resolve/snooze/preferences, readable transcript and user-controlled audio. Voice is a communication channel, not proof of intelligence.
- **Business Help:** private vault, topic/jurisdiction coverage, reviewed official-source dates, missing-document tasks and bounded cited answers/packets.
- **Settings/Connections:** actual configured/blocked/degraded/revoked states for AI, embeddings, DB vector capability, speech/push and optional providers. No invented connected badge.

Use current component/i18n conventions with a coherent spacing/type/color system. Test 360/768/1440px, keyboard/focus, meaningful headings/labels, screen-reader status updates and reduced motion. Confidence and agent activity cannot be color-only or motion-only. Explain the business outcome first; debugging/tool details can expand.

## J. Dependencies, blockers and progress

`docs/progress.json` keeps original 00–12 and new 13–26 task IDs. Phase dependencies describe **full-completion prerequisites**. Phases with required blocked live tasks remain incomplete. The following are the only explicit allowances for useful local task work while an external predecessor gate remains blocked:

| Allowed local work | Actual prerequisite to verify | What it cannot establish |
|---|---|---|
| P15-T01..T04 schema, score policy and UI | Published Phase 13 baseline plus verified existing identity/financial contracts | Genuine inferred-claim support or full Phase 15 completion without its live gate |
| P16-T01 indexing design and P16-T02/T03 lexical/injected-vector boundary | P15-T01 ownership/source contracts implemented and tested | Real embedding/pgvector access, retrieval quality or full Phase 16 completion |
| P17-T01 tool contracts and P17-T03 event-view UI with explicit doubles | P15 case/event contracts and permission tests; actual local event persistence | Live multi-agent collaboration or model-performance comparison |
| P18-T01 router/persistence, P18-T03 approval and P18-T04 voice recorder/text fallback | Verified tenant/action/case contracts | Genuine voice understanding or live cited answers |
| P19-T01/T03 verified-fact offer math; P20-T01/T03 receipt/credit invariants | Existing money/stock/approval contracts and relevant source/receipt migrations verified | Real offer interpretation or complete agent-driven workflow |
| P21-T01/T02 captured-request/availability records and deterministic scenario tests | Verified stock/event ownership/units | Validated demand model or real merchant demand capture |
| P22-T01 factual inbox and P22-T04 preferences/text fallback | Tested local case/business events and recipient permissions | Live push/TTS delivery or genuine generated brief |
| P23 local reservation/handover/deposit contracts | Relevant tested ledger/stock ownership and event contracts | Genuine semantic input parsing or verified operational pilot |
| P24-T01 vault and P24-T02 corpus governance tools | Tested private evidence access and versioned corpus schema | Current authoritative applicability, live legal advice or completed corpus review |
| P25 runner/scorer setup; P26 runbook/package preparation | Published Phase 13 command contracts and actual implemented interfaces | Evaluated model superiority, calibrated probability or deployed production |

Record such work by task, mode, passed prerequisite and remaining live gate. If needed publish an honest partial checkpoint first; never jump past verified-but-unpublished work. Do not call a later phase complete while required dependencies remain incomplete. Critical correctness/security failures block their dependent tasks, even locally. These allowances do not excuse skipping a required genuine-provider/browser/corpus/deployment test.

At session end, provide task IDs completed, checks/modes actually run, new failures/unknowns, milestone/receipt publication state, blocker details and one next executable task. The starting prompt must work unchanged for both first run and resume. If the current tracker is stale, repair it before resuming rather than hardcoding Phase 13 forever.

## K. Handoff validation and limitations

The accompanying handoff validator checks task/phase IDs, dependency acyclicity, document links, confidence-fixture arithmetic, tracker consistency and placeholders/status honesty. It is a **documentation/fixture validation**, not an application, model, browser, retrieval or financial integration test. Execute it and record actual results before calling the handoff ready.

No API keys, actual merchant records, verified embeddings, maintained legal corpus or deployment authorization are supplied by this file. Those boundaries must stay visible. The complete scope is a substantial product expansion; event deadlines do not waive acceptance gates. Preserve current organizer rules and original repository history; the live event schedule/rules were inaccessible in the prior research, so do not invent updated rules or guarantee a competition outcome.
