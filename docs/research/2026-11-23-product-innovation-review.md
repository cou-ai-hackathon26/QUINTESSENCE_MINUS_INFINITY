# Shongoti: product innovation and real AI review

Research date: **23 November 2026, Asia/Dhaka**. Source revision inspected: `8d4c122d712edbca4adad998090727779bef1dd0` on local `main`.

**Status: research and proposed extension, not implemented functionality or a replacement for `plan.md`.** Existing application code was inspected; application tests, real inference, payment calls and deployed workflows were not executed in this research session. The recommendations below do not certify previously reported phase results.

## 1. Product decision

Keep the connected merchant platform and the original evidence-backed supplier reconciliation. Make the next differentiator a **merchant-side buying and recovery assistant**: understand supplier offers before buying, verify what actually arrived, and follow an agreed correction until it is applied to the right bill. Add a low-effort memory of customer requests that did not turn into sales.

Bangla positioning: **“কেনার আগে শর্ত বুঝুন, মাল এলে মিলিয়ে নিন, পাওনা credit ভুলে যাবেন না—দোকানের টাকা কোথায় আটকে আছে দেখুন।”**

Initial customer hypothesis: an owner-operated grocery/general store with repeat suppliers, mixed cash/digital collections and informal Bangla/Banglish documents/messages. Do not target every type of business at once. The user cannot currently reach merchants; this remains a research-supported hypothesis, not customer validation.

The product should answer four concrete questions:

1. Which available offer fits my actual cash, demand and supplier terms?
2. Did I receive what was promised, including the free goods and correct pack size?
3. Which agreed credits, returns or payments have not yet reached the supplier's current balance?
4. What did customers ask for that my sales records never captured?

The differentiation hypothesis is the connected Bangla evidence-to-action workflow across these questions. OCR, three-way matching, voice commands, forecasting and multiple agents are existing categories; none alone establishes novelty.

## 2. Actual gaps before adding features

These findings come from source inspection at the revision above. They are narrower than a complete application/security audit.

| Finding | Source | Consequence |
|---|---|---|
| Configured AI path unconditionally raises `ProviderUnavailableError`; there is no provider request in that path | `apps/api/app/ingestion/adapters.py:95–96` | Adding a key alone cannot activate genuine inference. Implement the adapter and its failure contract first. |
| Unconfigured adapter returns fixed party/amount/date/snippet when fixture keywords match | `apps/api/app/ingestion/adapters.py:61–82` | Keep test doubles explicitly injected into tests/demo; ordinary user uploads must not receive canned extraction. |
| Upload passes PDF-native text or UTF-8 text to the adapter; image/audio content is not forwarded | `apps/api/app/api/v1/evidence.py:58–68` | Upload support is not proof of functioning image OCR or audio understanding. |
| AI evaluation script prints a message and exits; configured branch runs no evaluation | `scripts/eval-ai.js` | A successful process exit is not evidence of real AI quality. |
| Benchmark reads `gold_expected`, assigns correct fields directly and adds fixed model latency/cost and hypothetical errors | `scripts/run-benchmark.js:52–143` | Existing generated comparisons are simulations. Do not use their accuracy, financial error, cost or latency as measured architecture results. |
| Report presents those outputs as evaluation results | `docs/evidence/phase-11/evaluation-benchmark-report.md` | Preserve history, clearly supersede the empirical interpretation, and replace it with an actual evaluation before pitching results. |
| Forecast holds out the final seven observations once, then emits `rolling_origin_evaluated: true`; bounds are prediction ± MAE | `apps/api/app/adapters/forecast.py:54–110` | This is a single holdout comparison, not rolling-origin evaluation. The interval has no demonstrated probability coverage. |
| Progress says Phase 04 blocked and Phase 05 incomplete, but also says all delivery phases published and key configuration is the only remaining AI task | `docs/PROGRESS.md`, `docs/progress.json` | Reconcile claims before another agent resumes. Published commits do not establish acceptance gates. |

Useful existing foundations to extend: exact-money domain code, merchant transactions, evidence storage/review, stock and purchase drafts, scenarios, actions and portal UI. Their existence is visible in source; their full correctness was not re-certified here. In particular, current purchase receiving uses the draft quantity as received quantity; a discrepancy workflow needs separately recorded actual receipts and partial deliveries.

The original submission already proposed Reader, Reconciler, Skeptic and Clarifier roles. The extension is to implement genuine, conditional tool-using investigation across the buying lifecycle, rather than claim that multi-agent is a newly invented idea.

## 3. Current research and what it permits us to conclude

| Evidence, date and source type | Observation | Product implication and limit |
|---|---|---|
| [MSC Bangladesh field-research article, 14 May 2026](https://www.microsave.net/2026/05/14/why-bangladeshs-supply-chains-still-run-on-cash-despite-digitization/) | Describes a Manikganj retailer handling sales, records and cash alone, with supplier cash requirements, withdrawal fees and reconciliation barriers. | Usable money depends on payment method and timing. Our existing liquidity planner matters; an LLM cannot create missing payment rails or remove provider restrictions. This is not evidence that merchants will adopt our proposed app. |
| [UNCDF Bangladesh FMCG report, 12 August 2021](https://www.uncdf.org/article/7065), [report](https://www.uncdf.org/Download/AdminFileWithFilename?cultureId=127&filename=12082021-uncdffmc-supply-chain-and-payment-digitization-reportfinal-enpdf&id=15234) | Describes supply-chain coordination, returns/dues information and promotional schemes, including product-with-product and price discounts. | Offers, delivery, returns and account reconciliation are connected processes. Historical Bangladesh context, not a fresh 2026 prevalence estimate. The report download timed out during this session; detailed passages were available through indexed report results. |
| [Unilever Bangladesh's 2026 smart-retail page](https://www.unilever.com.bd/news/2026/from-mudir-dokan-to-smart-retail/) | Describes Lever Bazar/UCart ordering and offers, and IQ Nexus sales-based stocking/assortment intelligence. | Ordering plus AI stock recommendations already exists locally. Focus on merchant-controlled, cross-supplier evidence and unresolved exceptions. Page has a 2026 URL but no exact publication day visible; accessed 23 November. Vendor impact claims were not independently validated. |
| [TallyKhata feature page](https://www.tallykhata.com/en/khata-features/), current page accessed 23 November | Customer/supplier balances, reminders, reports and backups are advertised. | These are expected operational features, not the innovation claim. Absence of a feature on a page is not proof that the competitor cannot do it. |
| [Zoho Billing AI feature page](https://www.zoho.com/uk/billing/features/ai-features/), current page accessed 23 November | Advertises conversational queries, English voice instructions, transaction drafting, forecasting and review controls. | A chat assistant, voice input or a generated invoice does not by itself distinguish Shongoti. |
| [Tipalti invoice-processing guide](https://tipalti.com/resources/learn/automated-invoice-processing/), current page accessed 23 November | Describes invoice/PO/receiving matching and exception handling. | Do not pitch ordinary three-way matching as an invention. Our hypothesis is low-entry-effort investigation of informal, changing Bangla terms connected to actual shop actions. |
| [FreshRetailNet-50K, version 6, revised 20 November 2026](https://arxiv.org/abs/2505.16319v6), primary research | Stockouts censor observed sales; dataset includes hourly availability annotations for latent-demand research. | Zero sales during unavailable stock must not automatically mean zero demand. Add missed-request capture and availability history. Data is fresh retail from a different setting; its published performance cannot be transferred to Bangladeshi shops. |
| [Towards a Science of Scaling Agent Systems, version 3, revised 8 April 2026](https://arxiv.org/abs/2512.08296v3), primary research | Controlled comparisons show that task decomposition, coordination and verification affect whether multi-agent helps; tool-heavy/sequential work can suffer overhead. | Use specialists conditionally and compare against a strong single agent with equal access. No blanket claim that more agents improve quality. |
| [Anthropic multi-agent research engineering, 13 June 2025](https://www.anthropic.com/research/multi-agent-research-system) | Explains orchestrator/worker systems, separate contexts and the cost of coordination. | Independent evidence investigations can fit this pattern. Results on research tasks are not Shongoti accuracy or cost estimates. |

Research supports problem categories and design hypotheses. It does not establish frequency of free-goods disputes, local willingness to pay, adoption, time saved, or money recovered by this product.

## 4. Proposed features and the AI necessity test

### A. Buying Desk: understand the real offer before spending

**Daily trigger:** supplier sends a price-list photo and a Bangla voice note. Another supplier offers a lower headline price but different pack size, cash terms or delivery time.

Capture price, SKU, pack size, minimum order, free units, delivery fees, credit period, payment method, expiry/batch limits, return conditions and offer validity. Every field needs a source reference and a state: proposed, confirmed, disputed or unknown. Preserve both old and changed terms with their effective scope.

**Real AI work:** resolve local product aliases, parse conditional speech, align differently structured offers, detect conflicts and ask a decision-changing question. For example, “১০ কার্টনে একটা ফ্রি” does not tell us whether mixed SKUs qualify or which item is free. Do not infer these missing conditions.

**Code work:** normalize verified units, compute landed cost, enumerate feasible orders against actual funds, upcoming obligations and supplied demand scenarios. No model-authored balance or invented supplier price.

**Result:** comparable offers, unavailable facts, cash effect today/next week and an editable clarification/counteroffer draft. Only already offered terms are available options; a drafted negotiation is not an accepted discount or credit extension.

**Acceptance:** changing “cash today” to “seven days credit” must change the parsed terms and permitted scenario without changing price or fabricating supplier acceptance. An ambiguous bonus SKU keeps effective cost conditional.

### B. Receiving Desk: promised, delivered, billed and credited

**Daily trigger:** delivery arrives while the owner is serving customers. The challan says one quantity; an owner voice note says fewer arrived and some were damaged.

Compare the approved order and offer with actual receipt, invoice and later acknowledgments. Capture separate ordered, received, damaged, accepted and disputed quantities. Support partial delivery rather than treating a purchase draft as fully received.

**Real AI work:** connect informal delivery notes to the correct order, distinguish a shortage from a later installment, identify changed or contradictory explanations, and find missing evidence. Source-backed questioning matters more than a confident summary.

**Code work:** quantity conservation, pack conversion, stock movements, exact discrepancy amount and independent allocation checks. A photograph cannot reliably count hidden cartons; ask for owner-confirmed counts or barcode/count capture.

**Result:** an evidence packet with the disputed line, source excerpts and a specific question. Track `suspected discrepancy → merchant reviewed → supplier response → agreed resolution → credit note → applied to bill`. Rejected/no-reply cases remain open.

Do not reduce payables simply because a claim was drafted or because the supplier said goods were returned. Acceptance and inclusion in the current demand are separate facts, preserving the original Shongoti problem.

**Acceptance:** a supplier's “we will adjust next invoice” creates a future adjustment follow-up, not an immediate deduction from today's demand. A corrected invoice must not double-apply an already used credit.

### C. Demand Memory: remember customers who left without buying

**Daily trigger:** owner records, “আজ তিনজন ছোট ডিটারজেন্ট চেয়েছে, বড়টা নেয়নি।” No sale appears in the POS.

**Real AI work:** map local product descriptions to candidate SKUs, distinguish out-of-stock requests from price rejection or pack preference, and propose a compact structured event. Ask whether “three” means three visits, people or units when material.

**Code/statistical work:** deduplicate linked events, count captured requests, retain stockout windows and compare availability-aware forecasts against naive sales-only forecasts. A repeated mention must not become another customer request automatically.

**Result:** “recorded unmet requests” beside sales and stock history, with a suggested small trial purchase for merchant review. Captured requests are a lower bound on observed requests, not complete market demand. Requested units are not guaranteed sales or lost profit.

Start with extraction and honest counts. Train/evaluate a statistical demand model only with sufficient relevant history. Public datasets can test a method, not validate local adoption or store-specific accuracy.

**Acceptance:** one stockout day with zero sales is labeled unavailable/censored; the model must not silently treat it as an ordinary zero-demand observation. Show unknown demand if recovery is unsupported.

### D. Return Window and Credit Recovery: finish the follow-up

**Daily trigger:** items are approaching a supplier's agreed return cutoff, or a credit was promised but the following statement still contains the full amount.

**Real AI work:** find the correct batch/invoice and interpret supplier-specific return wording, exceptions and subsequent messages. Identify whether “মেয়াদের এক মাস আগে” is a return condition and which stock it covers; an unclear date remains unclear.

**Code work:** calculate deadlines from confirmed dates/terms, prevent duplicate claims, account for returned physical stock and allocate an accepted credit exactly once.

**Result:** evidence-backed return task and the next specific action, with separate potential claim, supplier-accepted credit and applied credit. Do not present the total potential claim as savings or spendable money. A simple expiry alarm alone is a rules feature.

**Acceptance:** shipping a return, supplier accepting it and supplier deducting its value must remain separate events. A later exception scoped to one batch cannot rewrite every earlier purchase.

### E. Voice Transaction Review: the input method supporting all four

Example: “রহিম পুরনো বাকি থেকে পাঁচশ দিল, আজ তিনশ টাকার মাল নিল, দুশ নগদ দিল, বাকি খাতায়।”

AI proposes distinct events and asks where unclear amounts belong. Show a concise before/after preview with original audio timestamps/transcript; post only merchant-approved events through exact-money code. Preserve old-debt collection separately from today's revenue. Speech-to-text alone is a convenience, while event linking and ambiguity resolution are the semantic task.

This supports daily use but should not be the headline novelty. No hard-coded name/phrase path may substitute for real inference.

## 5. One synthetic demo that connects the product

The following numbers are **invented test inputs, not observed merchant impact**.

1. Owner has BDT 5,000 cash and BDT 2,000 in a wallet. Tomorrow's BDT 3,000 rent requires cash. No conversion route is assumed available; credit promises are excluded from usable funds.
2. Supplier A offers ten cartons at BDT 500 each, one identical carton free, cash today. Supplier B offers ten at BDT 510 each with seven days' credit. Same pack/quality/fees are explicitly confirmed in this synthetic case.
3. Code calculates A's BDT 5,000 total and effective price `5000/11` per carton, with an explicit display rounding policy. A leaves zero cash before rent; B leaves cash unchanged today but creates BDT 5,100 due on day seven. Its later affordability remains a scenario, not guaranteed.
4. Before suggesting B, the system must clarify whether A accepts a smaller order or confirmed wallet payment and whether B's credit terms are actually applicable. It cannot autonomously negotiate a successful new deal.
5. In a separate, clearly selected synthetic purchase branch where A is approved, delivery contains nine paid cartons and one free carton. The invoice charges ten paid cartons. Code flags one paid carton, BDT 500, as a candidate discrepancy.
6. Supplier says, “পরের চালানে পাঁচশ সমন্বয় করব।” AI links the promise to this discrepancy; the next action is to verify the later credit, not deduct BDT 500 from the current demand immediately.
7. Add the later statement, payment receipt and return slip. Reuse the original reconciliation workflow to establish whether each accepted adjustment was already included. Duplicate receipts and partial replies must keep their original financial invariants.
8. A missed-customer request can separately update the next buying recommendation without being counted as revenue.

During judging, alter one term, invoice reference or supplier reply not used in fixture development. Show the real provider/tool activity and the changed decision. If service fails, show the actual error and available manual review; do not replay a canned answer as live.

## 6. Multi-agent design with a specific reason to exist

Use a **case coordinator with conditional specialist investigations**, not a fixed procession of personas on every click. An agent is an actual model/tool loop that can select relevant records, seek missing information and stop within a budget. A prompt label or dashboard avatar is not proof of an agent.

| Role | Responsibility and tools | Boundary |
|---|---|---|
| Coordinator / Clarifier | Select the current decision, delegate only needed investigations, compare missing facts, request a focused answer and resume the affected case version | Does not generate favorable facts or bypass an unresolved supplier condition |
| Terms and Evidence Agent | Read offer/bill/audio sources, retrieve scoped supplier terms and propose source-linked claims | No stock/ledger writes; extracted amounts remain proposals |
| Stock and Demand Agent | Retrieve SKU aliases, received quantities, availability and recorded unmet requests; identify tradeoffs relevant to the proposed purchase | Numerical demand estimates come from evaluated tools or labeled assumptions |
| Reconciliation Agent | Retrieve payment/credit allocations and current statement; propose alternative inclusion/applicability interpretations | Does not determine truth by arithmetic alone or consume the same credit twice |
| Skeptic | Re-read original source locations and structured candidate claims without the proposer's persuasive narrative; return unsupported facts, conflicting scope and missing evidence | Agreement is not an independent truth guarantee; unresolved disagreement remains visible |

Start with the coordinator, evidence/terms specialist and skeptic for an offer case; add stock/demand or reconciliation roles only when their investigation can change the decision. Source extraction may also be a bounded non-agent model call where a loop adds no value.

The cash planner, unit normalizer, ledger and forecast evaluator are **deterministic/statistical tools**, not LLM agents. A financial executor revalidates permission, ledger/case versions, allocations and idempotency after merchant approval.

Shared durable state should include tenant, case/version, decision type, source IDs and locators, typed claims, contradicting/superseding links, missing facts, tool results and pending approvals. SQL tables and typed edges are sufficient initially; a graph database is not required. Preserve source-backed memory of approved aliases and scoped terms; a correction does not authorize global rules or model self-training.

Example dynamic behavior: the terms agent finds “free goods only on cash settlement”; coordinator requests payment constraints; stock agent finds the offered pack is not the requested size; skeptic discovers a later supplier exception scoped to yesterday's order. The coordinator asks about scope before ranking offers. After the answer, it resumes only affected work. This is a defensible investigation; summing balances with three agents is not.

Proposed initial engineering caps, to tune from observed evaluation: no more than eight model calls, twelve read-tool calls and one clarification round per synchronous case. Exhaustion returns a resumable case with unknowns. Set an explicit per-case monetary ceiling using the selected provider's verified pricing; no unsupported cheapness claim.

Capture actual model/version, elapsed time, retries, tool arguments/results, usage and status. Display an activity summary, cited findings and decisions, not private model chain of thought. Model roles on the same model can share failure modes. Uploaded instructions such as “ignore the ledger” remain document content, never authority.

## 7. Product flow without an oversized menu

Keep existing navigation. Add **Buying** and **Receiving & Claims** as connected workspaces; keep evidence and demand notes accessible through a global capture button.

| Moment | Owner action | Product response |
|---|---|---|
| Morning / Today | Review the next actionable decisions | Show confirmed payment constraints, receipt discrepancies, due credit follow-ups and return cutoffs; each opens the underlying case |
| Before ordering / Buying | Upload/record two offers or select previous terms | Compare confirmed terms and conditional costs; show missing facts, cash scenarios and reviewable purchase draft |
| When goods arrive / Receiving | Open order, record actual counts and attach challan/audio | Preview received stock, shortages and disputed lines; no blind “receive all” as the only path |
| After supplier reply / Claims | Add reply or corrected statement | Update only supported facts; show accepted versus applied credit and a precise next task |
| During a customer visit / Quick capture | Record a missed request or mixed transaction | Review proposed SKU/event links; save without requiring a full catalog migration |
| Before paying / Reconciliation | Open supplier account and review evidence | Original supported payable alternatives and clarification flow remain available |

The user sees business decisions, evidence and approval, with a compact **visible agent teamwork panel** on active cases. Show real task assignment, parallel work, findings, handoffs and waiting states; expand a task for its source/tool activity. Keep agent configuration out of routine shop work. Source locators open the relevant page/box/audio segment. This visible panel is an explicit user requirement added in the follow-up discussion; its events must come from actual backend work rather than timed animation.

First-use target: one supplier case from an uploaded bill/offer, with optional manual actual funds and stock context. Do not demand a complete historical ledger before providing any value. Missing context limits the recommendation explicitly. Offline capture can queue uploads/drafts later; do not claim offline inference or offline payment execution.

## 8. Credible evaluation and business validation

Replace simulation-derived claims with observed outputs from four real paths:

1. Native/OCR/ASR extraction plus serious deterministic matching/rules; disclose any ML used by OCR/ASR.
2. One capable tool-using model with the same documents, history, permissions and numerical tools.
3. Conditional multi-agent with those same sources/tools. Compare at matched budgets and also disclose extra compute at its intended operating setting.
4. A domain-engine oracle given reviewed structured facts, to isolate interpretation from arithmetic. Execute the engine; do not award it correctness by copying the answer.

Keep the existing 48-story material, but correct the runner. Add a proposed 30 paired families/60 cases across offer-scope changes, pack mismatches, partial receipts, promised versus applied credits, stockout demand and compound voice entries. Split whole families before prompt tuning; reserve 12 families/24 cases for held-out evaluation. Pair members and paraphrases cannot cross splits. Use independently checked arithmetic and source labels; replace any discovered leaked test family.

Required adversarial cases: ambiguous bonus SKU; old offer mistakenly applied to a new order; unit mismatch; one invoice split into deliveries; unreadable date; “credit next bill”; payment acknowledged but inclusion unknown; reused receipt; conflicting audio/text; duplicate missed request; prompt injection; timeout; stale approval; cross-tenant record access.

Measure exact financial-field accuracy, unsupported term/inclusion rate, source-locator correctness, justified completion, correct abstention, clarification usefulness, unauthorized state changes, merchant corrections, elapsed time including retries, actual billed usage and cost. Report denominators separately by mode/modality and difficulty. Run stochastic comparisons repeatedly when budget permits and show variation. Do not assert statistical superiority from a tiny suite.

Zero unauthorized writes and zero double allocations are required invariants in the tested cases, not a universal zero-error guarantee. Decide whether multi-agent earns its additional cost from observed reduction in material errors or review effort. If it does not, keep a single-agent default and the specialist path as an explicitly experimental option.

No merchant access: synthetic evaluation, team usability trials and public-data experiments must retain those labels. Team completion times are not merchant time savings. Once access is possible, test a few consenting shops on specific recent purchase/return cases and compare manual vs assisted review. Track real accepted/applied recoveries separately from possible claims. Start with a small operational pilot; do not manufacture a market-size, retention, savings or willingness-to-pay figure.

Pricing hypothesis only: test a transparent per-shop subscription with a bounded AI allowance. Log real cost per useful case. Supplier-funded ranking creates a conflict with merchant-neutral advice; disclose sponsorship and keep commercial ranking independent. No numerical subscription recommendation is validated yet.

## 9. Extension sequence and acceptance gates

These are proposed work packages, **not newly completed numbered phases**. Preserve existing phase IDs/checkpoints. If adopted, add explicit tasks/dependencies to the canonical plan rather than treating this report as implementation instructions that override it.

| Package | Scope | Gate |
|---|---|---|
| R0 — repair the evidence base | Truthful AI status, real provider adapter and modality routing, real evaluation runner, corrected benchmark/forecast descriptions and progress | Unseen synthetic text/image/audio reach the configured service; usage/error evidence is captured; unavailable mode never emits fixture output; no simulated metric is called observed |
| R1 — one source-backed case engine | Typed claims/provenance, scoped terms, case versions, coordinator/reader/skeptic and clarification resume | A contradictory reply changes only supported claims; unknowns persist; injected instructions cannot authorize state changes |
| R2 — Buying Desk | Two offers, units/conditions, deterministic cash impact, clarification and reviewable order | Unseen term changes alter the correct comparison; missing terms stay conditional; no order/payment is sent automatically |
| R3 — Receiving and credit follow-up | Actual/partial receipt, offer/PO/invoice comparison, claims, supplier response and applied credit | One discrepancy survives upload→clarification→accepted credit→exactly-once allocation with a source trail |
| R4 — Demand Memory and return windows | Compound voice capture, missed requests/availability, scoped return conditions | Duplicate notes do not inflate demand; no-history state is honest; promised credit never becomes money |
| R5 — fair comparison and demonstrable product | Live changed-input demo, held-out paired evaluation, failure paths and browser workflow validation | Publish actual outputs/metrics and their limits; preserve golden financial contracts; checkpoint each adopted phase per AGENTS.md |

**Prioritize R0, one case engine and a narrow Buying→Receiving→Reconciliation slice.** Demand Memory and advanced demand modeling are later additions if the core slice is reliable. Existing day-to-day transactions remain useful while these workflows develop.

Saved event references put the final on 24 November 2026, five continuous hours. On 23 November, committing to all proposed features before that event would be an unsupported delivery promise. The live event rules/challenges/schedule pages could not be accessed in this session. Confirm current organizer instructions; distinguish preparation allowed before the final from work required during it.

Historical saved rubric: relevance 20, innovation 25, AI application 25, feasibility 15, impact 15. Treat these as saved-reference values, not re-verified live rules. The convincing evidence for judging is a real changing-input workflow, justified unknowns, exact financial tools, bounded agent collaboration and an honest comparison—not a predicted judge score or a guaranteed win.

## 10. Experience to reuse as design knowledge

The preserved [prior-project README collection](../context/prior-project-readmes.md) suggests relevant experience: GridWise's interpreter/optimizer/independent replay split, Support Triage's tool routing and escalation, PSL Document Intelligence's source locations and correction memory, VERITAS-600's cross-document checks, and Pathwarden's multi-hop data lineage. These are README descriptions, not independently verified Shongoti capabilities.

Apply the architectural lessons with new project code and new measurements. Do not copy old implementation or inherit performance, legal-grounding or zero-error claims. Preserve hackathon history and original financial invariants. No new public release, external customer communication, order or payment is authorized merely by this research proposal.

**Next concrete implementation task:** repair P04-T04's genuine inference path and evaluation boundary before adding agent interfaces. Then implement one offer/receipt case using the existing ledger, stock and scenario tools; add broader modules only after its observed acceptance gates pass.

## 11. Follow-up requirements: visible teamwork, copilot, hybrid RAG and briefings

Added 23 November 2026 after user feedback. **Explicit product requirements:** visible agent collaboration, a chatbot, normal notifications, voice notifications and voice briefings. **Proposed supporting design:** hybrid RAG. **Exploratory extensions:** bounded compliance assistance and additional operational workflows. None is implemented by this document update.

### 11.1 Visible agent collaboration

In the Buying/Receiving case workspace, show the owner’s request above the coordinator’s task plan. Agent cards show their assigned business question and real states: queued, working, waiting for a tool, waiting for the owner, completed, failed or skipped. Parallel tasks appear side by side; dependency edges show which result another agent needs.

Example cards: Terms Agent checks the free-carton condition; Stock Agent checks product/pack and captured demand; Reconciler checks open obligations; Skeptic flags that the current offer applies only to cash settlement. Coordinator then asks the owner to resolve the payment-method question.

Persist events with case/version, task ID, agent role, parent/dependency, event ID, timestamp, status, source/tool references and a concise result. Stream actual events with reconnect/replay support; do not display fake percentages or completed work before a result exists. A timeout is a timeout, not a successful handoff. Show findings and tool activity rather than private chain of thought. Keep a simplified outcome view for users who do not want the full teamwork panel.

### 11.2 Shongoti Copilot: one conversational entry point

Use a persistent text/voice copilot drawer, with a full-page conversation when needed. It should understand the currently selected supplier, purchase or claim while preserving explicit scope.

Useful questions/actions:

- “রহিম ট্রেডার্সের পাঁচশ টাকার credit কোন বিলে adjust হওয়ার কথা?” → retrieve original agreement and current application state.
- “আগামীকাল cash-এ কোন খরচগুলো দিতে হবে?” → query ledger/obligations and verified payment constraints.
- “এই দুই offer-এর কোন শর্তটা আগে জিজ্ঞেস করব?” → invoke the active buying case.
- “এই notice-এ কী চেয়েছে, আমার কোন কাগজগুলো নেই?” → retrieve a verified source and review the uploaded notice/checklist.
- “রহিমের নতুন order-এর draft বানাও” → prepare a reviewable draft, then require the existing permission/version/approval gate.

Answer types must be distinguished: ledger fact, quoted document claim, proposed interpretation, scenario or unresolved question. Answers link directly to source locations and relevant screens. RAG answers cannot silently modify accounts, send messages, place orders or promise a discount. Keep context tenant- and role-scoped; cashier access does not expand through chat.

### 11.3 Hybrid RAG: the shop’s source-backed memory

Index consented shop documents and messages: bills, supplier offers, return terms, selected communications, audio transcripts and reviewed corrections. Store official compliance material in a separately governed collection. Keep original files and locators; a generated summary must not replace the source as evidence.

Pipeline:

`parse/OCR/ASR → source-preserving chunks → metadata and index → exact/entity + keyword + dense retrieval → rank fusion → optional reranking → scoped evidence pack → cited answer or clarification`

**Keyword/exact retrieval** is important for invoice IDs, transaction references, SKU/brand, dates and quoted phrases. **Dense retrieval** is useful for paraphrases such as “মাল ফেরতের টাকা” versus “return credit adjustment.” Normalize Bengali/ASCII digits and maintain reviewed Bangla/Banglish product/name aliases without corrupting original text. Entity equality and allocation validity remain deterministic checks.

Existing PostgreSQL can support full-text search alongside pgvector, combining rankings with reciprocal rank fusion; [pgvector’s official documentation](https://github.com/pgvector/pgvector#hybrid-search) describes this pattern. Do not call PostgreSQL’s built-in `ts_rank` BM25. If BM25 is an explicit requirement, choose and verify a genuine BM25 implementation and benchmark its Bengali tokenization. A multilingual embedding model and any reranker must be selected through local fixture evaluation, not an assumed language-quality claim.

Filter candidate records by tenant/role before scoring and reranking. Keep document version, source date, effective interval, supplier/order scope, page/box/audio timestamp and review state. Deleted/revoked records must disappear from retrieval and related caches. Never let a similar old invoice override the exact current invoice. Contradicting documents are returned as a conflict; high relevance is not proof of authority or truth.

**RAG is for finding and interpreting records.** Cash balance, dues, stock availability, allocation capacity and current permissions come from canonical transactional queries/tools. Chat combines these two paths and states their provenance. No embedding search is allowed to invent a financial total.

For retrieval evaluation, compare keyword-only, dense-only and hybrid on the same labeled questions. Measure Recall@k and ranking relevance alongside exact-ID mistakes, wrong-version retrieval, citations and unsupported answers. Include Banglish aliases, Bengali numerals, ambiguous people names, stale offers and cross-tenant traps. Adopt a reranker only if its observed gain warrants latency/cost.

### 11.4 Normal notifications, voice notifications and voice briefs

Build a durable notification inbox tied to actual case/business events. Examples: partial delivery unresolved; agreed credit absent from the next statement; approved return cutoff approaching; cash-only obligation with a supported shortfall; a pending approval invalidated by changed records. Notifications open the exact case and offer review, snooze, assign or dismiss actions.

Separate `rule trigger → contextual explanation → proposed action`. Rules detect dates, thresholds and state transitions. AI may summarize the evidence or choose a useful clarification; the notification channel itself is not an AI innovation claim. Deduplicate by event/version, group repeated alerts, respect quiet hours and role visibility, and expire resolved alerts.

Voice notification: an opt-in short spoken alert while the app is available, followed by a tap to inspect the evidence. Default lock-screen/shared-speaker content should not expose balances, customer names or dues. Offer mute and text-only modes.

Voice brief: a user-started morning/evening briefing assembled from an exact snapshot. It summarizes actual funds, due obligations, unresolved credits/receipts and the next few actions; distinguish promises and scenarios explicitly. Show the transcript and source cards, and allow “কেন?”/“এই কাজটা খোলো” follow-ups. Do not convert uncertain recovery or predicted sales into cash in the narration.

Browser notifications require user permission and compatible delivery setup; background push is not a guarantee of arbitrary background speech. See [Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API). Browser speech voices depend on the device, so Bangla availability must be checked at runtime; [getVoices](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices) returns the available set. Verify a suitable TTS provider if device voices are inadequate, and retain a readable transcript. Do not advertise reliable website-closed voice announcements without actual platform testing.

### 11.5 Business Help Desk: bounded document and compliance assistance

Start with administrative help: a business document vault, confirmed expiry/renewal reminders, jurisdiction-specific checklists, official application links and an explanation of uploaded notices or agreement clauses. For a supplier/rental dispute, prepare a factual chronology and an editable document packet; legal conclusions and contested obligations require appropriate professional review.

Ask the business location, activity and relevant dates before applying any checklist. Use reviewed official sources, with authority, publication/effective dates, jurisdiction, retrieved date, amendments and supersession links. A current crawl of an undated FAQ does not establish that every rule is current. If governing rules conflict or applicable facts are missing, show the gap and official/professional escalation path. Do not automatically file a form, pay a fee or submit a complaint.

Examples of primary sources researched on 23 November: [DNCC trade-license issue/renewal process](https://dncc.gov.bd/pages/static-pages/6922e06d933eb65569e27049), [NBR VAT FAQ](https://nbr.gov.bd/faq/vat-faq), [BIDA FAQ](https://boi.gov.bd/faq). NBR's page was retrieved; DNCC/BIDA content was available in indexed search results, but direct page retrieval timed out. These establish candidate source collections and services, not a universal checklist, a verified 2026 tax threshold or advice that every shop needs the same registrations. Legal help should begin after merchant-memory retrieval is reliable and its official corpus can be maintained.

### 11.6 More daily workflows worth testing

The following are product hypotheses, not claimed findings about their prevalence:

| Workflow | Useful outcome | Meaningful AI task / code boundary |
|---|---|---|
| Customer message to order | Convert an uploaded/selected voice or text order into a stock-checked draft and picking list; ask about unavailable pack/substitution | Interpret product aliases, quantities and preferences; code checks/reserves stock and prevents duplicate orders. Ask approval for substitution; no assumed chat-platform access. |
| Closing and shift handover | Explain an observed cash/stock discrepancy with linked events and a concise handover note | Retrieve and organize receipts, returns, voids and staff notes into hypotheses; code recomputes balances. Never accuse an employee based on a model guess. |
| Supplier promise/change watch | A changed delivery date or payment condition highlights affected purchase, cash scenario and follow-up | Interpret scope and link the change to active commitments; deterministic dependency tools calculate affected dates/amounts. Do not rewrite agreed terms from an ambiguous message. |
| Returnable crates/bottles/deposits | Track items sent/received, damage disputes and a refundable deposit separately from product revenue | Parse mixed item/return notes and find terms; exact quantity/deposit ledger remains code. Include only for stores that use this workflow. |
| Renewal-ready document packet | Collect the shop’s relevant reviewed documents and flag missing items against a sourced checklist | Extract identity/date/type and explain mismatch; code enforces access, expiry and checklist state. An assembled packet is not government approval. |

### 11.7 Implementation priority for these additions

Extend the existing proposal in this order: genuine inference and truthful evaluation → source-backed merchant-memory retrieval → copilot and real task/event view on one buying/receiving case → actionable inbox and on-demand voice brief → extra operational workflows → maintained compliance corpus. Basic in-app alerts and factual brief templates can be built independently while model access is blocked.

Acceptance checks must include: real parallel task events and reconnect replay; no fake agent completion; exact invoice versus semantic look-alike retrieval; no cross-tenant/cashier privilege leak; changed balance queried from ledger; insufficient evidence refusal; unapproved chat action rejected; duplicate/stale notification handling; voice disabled/unsupported mode; spoken amounts matching the exact snapshot; and jurisdiction/version conflict in a compliance answer.

This update changes the research proposal only. It neither completes a build phase nor repairs the previously identified AI/evaluation implementation gaps.
