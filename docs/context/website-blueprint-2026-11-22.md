**Shongoti: website, financial workflow and prediction blueprint**

22 November 2026, Asia/Dhaka. This document extends the earlier research into a customer-facing product specification. The accompanying interactive preview uses synthetic, screen-specific examples and local calculations. It is not an authenticated application, trained forecasting service, payment integration or deployed website.

**The product to build.**

Shongoti is a Bangla-first workspace where a small-business owner records transactions, understands the current financial position, tests a decision's future consequences, and completes the associated work. The original evidence-backed supplier reconciliation remains the first verification step before accepting a disputed obligation.

Customer promise: **“হিসাব রাখুন। সামনে কী আসছে দেখুন। সিদ্ধান্তের প্রভাব বুঝে কাজ শেষ করুন।”**

One shared financial event model must connect sales, receipts, receivables, purchasing, inventory, payables, cash/wallet positions and planning. Separate screens are different views of this model. A collection cannot be recorded once in a customer ledger and again as new sales revenue; a payment cannot be counted twice because it arrived through two connectors.

Full product scope and hackathon scope are different delivery milestones. Define the broad platform now; implement and verify one complete path before expanding it.

**Customer journey and website structure.**

| Stage / route | What the customer sees | What the customer can finish |
|---|---|---|
| Landing `/` | A concrete spending-impact example, Bangla product story, capture/reconciliation/planning previews, demo CTA, account CTA, real integration capabilities and privacy/data explanation | Explore a sample shop or begin setup; no fabricated customer counts, testimonials, accuracy or savings |
| Authentication `/login` | Mobile OTP and, if implemented, Google sign-in; explicit demo entry | Authenticate through the real configured provider; demo is visibly separate |
| Setup `/onboarding` | Shop type/name, opening money snapshot, essential reserve, optional dues/import and optional service connection | Start with minimal data; review an import before it affects the ledger |
| Today `/app/today` | Available funds by method, due commitments, data freshness, important corrections and three actionable priorities | Capture a transaction, inspect a shortfall or open the next task |
| Future `/app/future` | Seven/thirty/ninety-day outlook, source categories, assumptions, supported uncertainty and scenario comparison | Inspect when/why a shortfall appears; distinguish recorded obligations from anticipated receipts |
| Decision lab `/app/scenarios/:id` | Baseline versus a proposed purchase, expense, withdrawal, sale on credit or changed collection date | Save a scenario, compare alternatives and propose an action without changing actual books |
| Money `/app/money` | Cash, bank and wallet positions; receipts/payments/transfers; balances and settlement timing | Reconcile a snapshot, record a verified movement, review fees and account-to-account transfers |
| Sales `/app/sales` | Touch-friendly sale entry, products/units, customer, split payment and invoice | Finish a sale, allocate a receipt, issue a receipt/invoice and update stock correctly |
| Customers `/app/customers/:id` | Bills, receipts, returns, outstanding amount, statements, messages and promises in one timeline | Prepare an eligible payment request, record a dispute, inspect allocation and review new evidence |
| Suppliers `/app/suppliers/:id` | Bills, deliveries, accepted credits, allocations, collection dates and payment methods | Review a demand, prepare a purchase and reconcile a supplier statement |
| Bill check `/app/reconcile/:id` | Source beside proposed facts; reused receipts; received/included/accepted states; payable alternatives | Correct interpretation, ask one useful question, review the answer and approve a supported adjustment |
| Stock/purchasing `/app/stock` | Stock count, cost, cover, lead times, returns and draft purchase orders | Compare reorder options with cash consequences and approve an actual order when an integration exists |
| Evidence `/app/inbox` | Images/PDF/audio/text; extraction status and review queue | Capture, inspect the original, correct proposed facts and post a reviewed event |
| Actions `/app/actions` | Drafts, approval requests, schedules, provider execution status and exceptions | Edit/approve a permitted action, see delivery/payment status, retry safely or cancel pending work |
| Connections `/app/connections` | Exact capability, permissions, account, live/sandbox mode, last sync and errors | Connect/revoke a supported service, inspect sync failures and choose import fallback |
| Reports `/app/reports` | Cash movement, sales, expense categories, margins where supported, dues aging and inventory value | Export actual reviewed reports and inspect the sources behind a number |
| Team/settings `/app/settings` | Owner/cashier/accountant roles, approval limits, business time zone, export/delete, audit and backups | Delegate safely, correct settings and inspect who changed what |
| Customer invoice portal `/pay/:token` | Only that customer's invoice/request, current status, receipts and dispute/reply action | Start an approved checkout or submit information without needing a full merchant account |

Keep primary navigation small: Today, Future, Money, Sales, People, Stock, Inbox and Actions. Put connections/reports/team under a secondary group if the merchant finds the full menu too dense. On mobile, expose Today, Add, Tasks and More; on desktop use a sidebar and persistent “Add record” action. A business-wide jump/search control is useful only after real searchable records exist.

**Landing page content and hierarchy.**

Open with a recognizable decision, not a list of AI technologies: **“আজ ৬,০০০ টাকা খরচ করলে, পরের সপ্তাহে মালের টাকা থাকবে?”** A small baseline/scenario preview leads directly into the sample shop. Primary CTA: “আমার দোকান শুরু করি”; secondary: “নমুনা দোকান দেখি”.

Follow with three connected jobs: add evidence simply, verify the obligation, and see the next financial consequence. Show a supplier-demand example, the spending-impact example and a completed invoice/payment-status example. Explain where the merchant reviews facts. Explain integrations by capability rather than showing every provider logo as if connected. Add clear account/data practices and a realistic support/contact path. Do not advertise guaranteed savings, guaranteed forecasts, one-click bank control, or real users that do not exist.

Authentication must use a configured provider. A production mobile OTP flow needs delivery status, expiry, retry limits and recovery. Demo mode must not ask for a real OTP or appear to authenticate an arbitrary phone number.

**Onboarding must produce a first useful result.**

First collect a shop identity and opening cash/wallet snapshot with an as-of time. Ask for the next known supplier obligation and an essential reserve. Let customers choose “check one bill” or “plan this week” as the first job. Offer optional CSV/Sheets or selected-document import after the first result.

Do not require every historical transaction, a complete SKU catalogue or a live bank connection. Surface “data incomplete” next to affected outputs. An opening snapshot is not revenue and historical payments must not be subtracted again from today's opening cash. A plan based on a stale snapshot is visibly stale.

**The daily workflow should connect the whole business.**

| Real event | Immediate effect | Downstream effect |
|---|---|---|
| Cash sale | Cash increases; sale is recorded; inventory quantity decreases | Cost of goods sold updates where the inventory-cost model supports it; forecast is refreshed |
| Credit sale | Receivable increases; revenue/stock effects are recorded | Expected collection is planned separately; no immediate cash increase |
| Partial collection of old dues | Cash/wallet increases, receivable decreases, receipt is allocated | Remaining balance and conditional collections update; no duplicate new sales |
| Inventory purchase for cash | Cash decreases, inventory increases | Later sales consume inventory cost; the full purchase is not automatically immediate profit loss |
| Inventory bought on credit | Inventory and payable increase | Due date creates a future obligation; cash is unchanged until payment |
| Supplier payment | Available funds decrease; payable allocation increases | Future obligation is reduced only once; source and settlement status remain inspectable |
| Accepted goods return | Quantity/value and accepted credit update according to the event | Payable reduction depends on acceptance, correct linkage and prior inclusion |
| Wallet transfer/cash-out | One account decreases; another increases at availability time; fee is separate | Total funds decrease by the fee, not by the transfer principal |
| Owner withdrawal | Funds decrease and owner account updates | Future cash changes; it is not automatically an operating expense |
| Equipment purchase | Funds decrease; asset treatment is separate | Depreciation/expense treatment is distinct from immediate cash impact |
| Planned purchase or simulated withdrawal | Scenario changes only | Actual money, inventory and financial statements stay unchanged |

The implementation can start with the transactions needed for the demo, but must preserve these distinctions. Taxes and formal financial statements should only be offered when the relevant accounting and jurisdiction rules are actually implemented and verified.

**Prediction and simulation are complementary features.**

1. **Payment-capacity outlook.** Forecast available money per account/method and cutoff. Show a cash-only supplier shortfall even if another wallet has a positive balance.
2. **Spend-before-you-commit.** Show how a proposed expense, owner withdrawal, equipment purchase or credit sale changes later obligations and reserves.
3. **Restock readiness.** Combine supported stock cover, supplier lead time and cash feasibility. Suggest a smaller order or different date when supported, rather than simply raising a low-stock alert.
4. **Collection outlook.** Separate known dues, recorded promises and statistically estimated payment delays. Do not turn a due date or model score into a guaranteed receipt.
5. **Margin squeeze.** Compare a new supplier unit price with the current selling price and cost basis. Calculate the margin effect; any assumed change in customer demand after a price change is a separate scenario.
6. **Recurring-cost outlook.** Include rent, utilities, wages and known periodic payments. A repeated entry suggestion remains a reviewed projection until accepted.
7. **Cash concentration and exposure.** Show how much working capital is in stock, owed by a few customers or committed to suppliers. It is a measured position, not a moral score of a customer.

Do not present all of these as trained AI predictions. Due-date arithmetic, margin calculations, stock-cover arithmetic and cash constraints are deterministic. Statistical models estimate uncertain inflows/outflows or demand when sufficient relevant history exists. Language/multimodal models interpret records and explain supported results.

**Define the forecast inputs explicitly.**

- Recorded actual events and verified account snapshots.
- Reviewed outstanding obligations and accepted recurring commitments.
- Promises with amount, timing, method, conditions and retraction status.
- Estimated operating flows with an identifiable model or manual assumption.
- Proposed scenario interventions, which never become actual events by simulation alone.

A forecasted collection must be removed or reconciled when the actual linked receipt arrives. Avoid double-counting an open invoice, a promise, a predicted payment and its gateway notification as four inflows. Similar rules apply to recurring expense suggestions and actual bills.

For cold start, show known obligations plus merchant-entered receipt assumptions and scenarios. For shops with useful history, begin with simple weekday/seasonal baselines and compare appropriate time-series models. Test on rolling historical cutoffs so no future information leaks into training. Use interval coverage and absolute monetary error as well as average point error; avoid percentage-error metrics that become misleading around zero. Only show probability/uncertainty claims that have been evaluated for the relevant task. [Forecast evaluation reference](https://otexts.com/fpptr/tscv.html).

A larger language model is not a substitute for training data or forecast calibration. QuickBooks already offers history-based projection suggestions and separates planning from actual accounting. This feature category is established; Shongoti must demonstrate its local evidence-to-action advantage. [Current QuickBooks projections documentation](https://quickbooks.intuit.com/learn-support/en-us/help-article/budget-and-planning/create-manage-cash-flow-projections-quickbooks-online/L5H72vJ7D_US_en_US).

**A concrete decision-lab example.**

The preview has a synthetic seven-day cash plan for 22–28 November. Opening cash is BDT 12,000. Assumed cash sales are BDT 1,000 each day. Planned outflows are BDT 2,000 on day one, BDT 6,000 on day three, BDT 4,000 on day five and BDT 3,000 on day seven. A BDT 3,000 cash reserve is the chosen target.

The baseline closing balances are 11,000; 12,000; 7,000; 8,000; 5,000; 6,000; 4,000. An extra BDT 6,000 cash expense today changes them to 5,000; 6,000; 1,000; 2,000; -1,000; 0; -2,000. Therefore reserve first falls short on 24 November, while the first direct inability to fund the plan appears on 26 November. A positive number below the reserve and a negative fund balance are different problems.

Under those assumptions, reducing the extra expense to BDT 1,000 keeps the minimum closing balance at BDT 3,000. This is a conditional result over the seven-day horizon, not a general claim that BDT 1,000 is always safe to spend. A BDT 3,000 promised receipt on day two is an optional scenario, not actual cash. Lower sales assumptions also change the answer. The calculation is performed locally in the preview; no forecasting model or real account is called.

In the full product, selecting the first shortage opens the contributing events and source records. The owner can compare a reduced purchase, accepted digital payment, permitted cash-out or agreed timing change. The selected alternative becomes an approval request. Executing it creates a real event only after the relevant confirmation.

**The original supplier feature is central to future planning.**

A current supplier demand is not necessarily a verified obligation. Preserve payment applicability, prior inclusion, return acceptance and allocation capacity as separate facts. Keep the original BDT 25,000 / BDT 4,000 payment / BDT 3,000 return example and its BDT 18,000–25,000 hypotheses.

An incorrect obligation corrupts every later projection. The product should therefore ask the question that changes the downstream decision most. If receipt versus inclusion changes whether a future stock purchase is affordable, show that connection. A plan can branch over disputed-payable scenarios, but must not quietly choose the cheapest one as the confirmed liability.

The preview keeps this proposal example separate from the seven-day planning fixture and explicitly labels that it is not posted into the simulation ledger. The production system should link reviewed reconciliations directly to the obligation/event records used by the planner.

**Action center: finish work, preserve status.**

Every proposed external action should contain the intended recipient, amount, document/message, reason, source links, expected effect and relevant permission. The owner can edit, approve, schedule or cancel it. Suggested states:

`proposed → reviewed → approved → queued → provider accepted → delivered/paid/failed → reconciled`

Message sent, message delivered, customer promised, checkout completed, provider verified and spendable settlement are distinct states. A callback alone must not produce an unrestricted available-money increase. If a prerequisite record changes, invalidate or re-review the affected action. Store outbox/idempotency keys and provider IDs to avoid repeats; verify callback signatures or provider validation as appropriate.

Use deterministic automation for known deadlines and repeating conditions. Use AI to interpret evidence, propose a relevant action and draft wording. Do not label a fixed cron schedule as autonomous reasoning. A bounded agent may inspect sources, retrieve reviewed records, request clarification or prepare an action; it must not directly change money, recipients or permissions from document instructions.

**Real integrations and the limits they impose.**

| Integration | Website capability | Access and execution requirements | Initial milestone |
|---|---|---|---|
| SSLCOMMERZ | Merchant-linked customer checkout; transaction status; matched payment receipt | Merchant account, sandbox/live credentials, server session creation, IPN, provider validation, amount/currency/merchant matching and deduplication | A real sandbox payment lifecycle, if credentials are available |
| Direct bKash / approved MFS gateway | Specific approved checkout/status capabilities | Provider onboarding and the exact API permissions; payment collection does not imply reading all wallet history or outbound transfers | Capability assessment; do not pretend universal live access |
| Google Sheets | User-selected import/export and later reviewed updates | OAuth, least-privilege file access, selected spreadsheet, field mapping and conflict/deduplication handling | One actual OAuth import/export if available; CSV fallback |
| Customer invoice portal | Show a scoped invoice; accept customer replies/disputes; start configured checkout | Unguessable/revocable scoped links, minimal exposed data, real backend and gateway confirmation | Implement before broad messaging automation |
| Email or SMS provider | Permitted invoice/order notices and status callbacks | Verified sender, approved use case where required, consent/recipient handling, fees and stop/retry logic | One approved provider or explicit manual delivery |
| WhatsApp Business Platform | Eligible transactional conversations and incoming-message/status webhooks | Business setup, recipient opt-in, approved templates when required and specific use-case eligibility | Do not assume automated debt collection is eligible |
| Statements/CSV/files | Import selected financial evidence and reconcile balances | User review, original preservation, parsing checks and deduplication | Directly feasible without broad account access |
| Browser/PWA | Camera capture, supported voice recording, local draft queue and printed receipts | User browser permission, offline state and later conflict-safe synchronization | Local drafts must not appear as server-posted records |

SSLCOMMERZ explicitly documents session creation, notification handling and Order Validation. A success redirect is insufficient proof of a valid payment. Checkout normally includes a gateway or provider authorization screen; “start from Shongoti” does not mean bypassing the provider's payment authorization. [Official developer documentation](https://developer.sslcommerz.com/).

Google recommends narrowly focused authorization, including per-file `drive.file` where applicable. A Google sign-in by itself does not authorize reading a shop's spreadsheets. [Sheets authorization documentation](https://developers.google.com/workspace/sheets/api/scopes).

**Important correction to the earlier communications assumption:** WhatsApp's policy, last updated 23 September 2026, lists debt collection among prohibited uses. It also requires opt-in and approved templates for initiated conversations/outside the applicable service window. Do not build or market an unrestricted WhatsApp debt-collection autopilot, and do not assume merchant approval overrides provider policy. Whether a particular ordinary invoice/order notification is eligible must be established with the provider. In-app owner tasks and a scoped customer invoice portal can still be designed without claiming a WhatsApp capability. This is not a suggestion to route prohibited activity around the rules. [Current WhatsApp Business Messaging Policy](https://business.whatsapp.com/policy), [official platform/webhook capabilities](https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform).

No live MFS/bank, SMS, email, Sheets or WhatsApp credentials were requested or used for this design. Integration viability is based on documentation; it is not an end-to-end tested integration result.

**Features that make the larger platform valuable.**

- Cash/credit/split sales and printable/shareable receipts.
- Customer and supplier statements with partial allocations, returns and disputes.
- Multi-account money management, fees, settlement timing and snapshot reconciliation.
- Repeating operating commitments, owner withdrawals and approval budgets.
- Inventory quantity, units, supported cost basis, purchase drafts and supplier lead time.
- Stock/cash-aware reorder comparison and supplier price/margin-change detection.
- OCR/PDF/audio evidence capture and a financially critical review queue.
- Searchable party timelines and source-grounded answers to business questions.
- Future cash scenarios and versioned, reviewable decision histories.
- Action queue, connector execution status, exceptions and audit.
- Cash-flow, dues-aging, sales and inventory reports; profit only where costing supports it.
- Owner/cashier/accountant permissions, safe corrections, backups and data export/delete.

Each feature should answer a merchant question and complete a task. Do not add a chart, agent name or technical security score merely to increase the feature count.

**Engineering depth that supports the experience.**

Keep one transactional ledger with append-only corrections, source-linked claims, obligations, payment allocations, inventory movements and scenario snapshots. Separate raw documents, proposed facts, reviewed facts and committed events. Compute balances exactly; enforce allocation capacity, posting idempotency and version checks in database transactions. Use account-specific availability timestamps.

Represent the dependency links from source → claim → obligation/event → forecast → action. A changed supplier credit, receipt date or stock assumption should show which plans/actions are affected. PostgreSQL relationships and explicit dependency records are sufficient at first; a separate graph service is a later scaling decision.

Give the forecast engine a deterministic snapshot and keep it independent of model prompts. First implement bounded scenario enumeration or a constrained optimizer, then independently replay money/stock constraints. Parse documents using the cheapest adequate route: native PDF extraction, bounded visual reading for scans/images, audio transcription with contextual extraction, and critical-field review. Do not allow an LLM to invent exact timestamps, document boxes or calibrated confidence.

A production forecasting pipeline needs reproducible data windows, training/evaluation splits, feature definitions, model/version tracking and drift/error monitoring. A synthetic dataset can demonstrate code execution and controlled failure cases; it cannot establish merchant forecasting accuracy.

**Delivery stages that preserve the ambition.**

| Stage | Working outcome | Evidence needed |
|---|---|---|
| Hackathon vertical slice | Landing/demo entry, minimal setup, today screen, original bill check, one spending-impact scenario, evidence review, action draft and one integration lifecycle where available | Genuine inference, changed-input results, independent accounting checks, real sandbox status if used |
| First merchant pilot | Actual daily capture, customer/supplier balances, cash close, usable-money planning, scoped portal and reviewed provider actions | Consented records, input burden, retention, correction rate, feasible actions and confirmed benefit |
| Predictive operating platform | History-based cash/demand forecasts, stock-aware purchasing, recurring commitments, reports and team workflows | Rolling-origin accuracy/interval evaluation, cold-start fallback, reliable integrations and supported accounting |
| Expanded operations | Multiple shops, richer procurement integrations and additional banking/payment capabilities | Verified provider access, branch/role controls, scale/reliability and customer demand |

The first delivery should still look and behave like one coherent product: an action begins at the dashboard, a decision is tested, evidence is reviewed, the owner approves, a provider executes where configured, and verified status updates the relevant records. Do not substitute a large set of static navigation pages for that complete loop.

**A winning-quality demonstration to aim for.**

Start with a shop owner considering a purchase or withdrawal. Let the judge change the amount or move a customer's promised date. Show the first future shortfall and the relevant supplier/stock obligation. Open the source, discover the supplier amount is ambiguous, resolve only what a new answer establishes, and recompute the alternatives. Choose a feasible action and demonstrate its actual configured execution/status path. Explain the result using source-linked facts, exact calculations and clearly labeled assumptions. Report measured errors, latency and cost rather than promising a ranking or real-world accuracy that has not been established.
