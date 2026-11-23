# Graph Report - sonngoti  (2026-11-23)

## Corpus Check
- Large corpus: 535 files · ~739,399 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 2059 nodes · 5663 edges · 130 communities (85 shown, 45 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 519 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Supplier Offers & Copilot Engine
- Web UI Router & Agent Console
- Stock Reporting & Demand Forecasting
- Multi-tenant Auth & Database Persistence
- Evidence Verification & Document Search
- Groq Provider & AI Extraction Schemas
- Multimodal AI & Reconciliation Adapters
- Operations & Container Logistics
- Double-Entry Financial Ledger
- Frontend Commerce & Currency Helpers
- Goods Receiving & Credit Notes
- Case Triage & Confidence Assessment
- React Workbench UI Root
- Statement Reconciliation & Disputes
- Web Application Manifest & Build Config
- Package Concurrently Description
- Portal And Actions
- Agents Orchestrator Run
- And Stock Reports
- Reportspage Stockpage Navbar
- Scenarios Scenario Domain
- Merchant Create Summary
- Money Bdt Decimal
- Planning Operations Evidence
- Auth Supportpages Layout
- Helpdesk Engine Document
- Notifications Engine Notification
- Actionableinbox Businesshelpdesk Languagecontext
- Workbench Auth Models
- Router Demo Session
- Merchant Record Cash
- Badge Button Card
- Home Inferencedetails Charts
- Auth Store Server
- Domain Contracts Eval
- Liquidity Domain Golden
- Confidence And Cases
- Agents Cases Events
- Browser Check Commerce
- Landing Runtime Domain
- Tsconfig Compileroptions Allowimportingtsextensions
- Agents Tenant Verifies
- Business Help Verifies
- Workflow Merchant Sale
- And Phase11 Security
- Buyingdesk Confidencebadge Copilotchat
- Buying Desk Bonus
- Copilot And Tenant
- Notifications Tenant Voice
- Operations Tenant Verifies
- Retrieval Tenant Ensure
- Checkpoint Real Mjs
- Demand Unmet Engine
- Demand Memory Tenant
- Buying Supplier Order
- And Portal Actions
- Scenarios Workflow And
- Validate Study Validate-study
- Preview Mjs Dir
- Validate Extension Handoff
- Main Package React-dom
- Voicecopilot Choose Ensuresession
- Benchmark Run Run-benchmark
- Run Python Run-python
- Agenttimeline Agenteventview Agenttaskview
- Operationshub Customerreservationview Operationshubprops
- Tsconfig Node Compileroptions
- Scan Secrets Scan-secrets
- Smoke Checkport Http
- Check Css Check-css
- Verify Redesign Verify-ui-redesign
- 008 Hybrid Memory
- Engine Evidencepack Retrievalresult
- Demandtracker Bengali Digits
- Receivingtracker Bengali Digits
- Http Check Http-check
- Package Name Private
- Browser Check Accessibility
- Eval Rag Eval-rag
- Verify Offline Verify-offline
- Eval Eval-ai Path
- Browser Check Core
- Browser Check Final
- Browser Check Groq
- Browser Check Judge
- Browser Check Operations
- Browser Check Planning
- Browser Check Recording
- Browser Check Support
- Browser Check Voice
- Browser Check Workbench
- Storage Evidencestorage Sanitize
- Main Info Health
- Domain Golden Setup
- Sslcommerz Payment Gateway
- Workbench Data Capabilities
- Evidence Ingestion Auth
- 001 Initial Schema
- 002 Evidence Schema
- 003 Merchant Workflow
- 004 Scenarios Schema
- 005 Actions And
- 006 Stock Reports
- 007 Cases And
- 009 Agent Workspace
- 010 Copilot Workspace
- 011 Buying Desk
- 012 Receiving And
- 013 Demand Memory
- 014 Notifications Inbox
- 016 Business Help
- 017 Workbench Credentials
- 018 Provider Receipts
- Config Settings Cors
- Persistence And Auth
- Stock And Reports
- Emptystate Emptystateprops
- Landing Component
- Verify Integrations Verify-integrations
- Assets Html?raw
- Eval Agents Eval-agents
- Eval Confidence Eval-confidence
- Eval Workflows Eval-workflows
- Pyproject Shongoti-api

## God Nodes (most connected - your core abstractions)
1. `UserModel` - 136 edges
2. `Money` - 91 edges
3. `useLanguage()` - 68 edges
4. `useCopy()` - 58 edges
5. `react` - 48 edges
6. `now_utc()` - 45 edges
7. `post()` - 45 edges
8. `Badge()` - 43 edges
9. `get_db()` - 40 edges
10. `lucide-react` - 40 edges

## Surprising Connections (you probably didn't know these)
- `run_eval()` --uses--> `AIModelAdapter`  [INFERRED]
  scripts/eval_ai.py → apps/api/app/ingestion/adapters.py
- `test_judge_isolation_balanced_seed_and_cookie_csrf()` --uses--> `PostingModel`  [INFERRED]
  apps/api/tests/test_workbench_auth.py → apps/api/app/persistence/models.py
- `test_public_invoice_is_scoped_and_unverified_payments_cannot_post()` --uses--> `CustomerPortalTokenModel`  [INFERRED]
  apps/api/tests/test_workbench_auth.py → apps/api/app/persistence/models.py
- `AgentOrchestrator` --uses--> `HybridRetriever`  [INFERRED]
  apps/api/app/agents/orchestrator.py → apps/api/app/retrieval/engine.py
- `CopilotEngine` --uses--> `AgentOrchestrator`  [INFERRED]
  apps/api/app/copilot/engine.py → apps/api/app/agents/orchestrator.py

## Import Cycles
- 1-file cycle: `apps/web/src/workbench/Landing.tsx -> apps/web/src/workbench/Landing.tsx`

## Communities (130 total, 45 thin omitted)

### Community 0 - "Supplier Offers & Copilot Engine"
Cohesion: 0.06
Nodes (23): list_supplier_offers(), create_session(), CreateSessionDTO, get_session_detail(), list_sessions(), MessageResponseDTO, send_copilot_message(), send_copilot_voice() (+15 more)

### Community 1 - "Web UI Router & Agent Console"
Cohesion: 0.11
Nodes (64): accountHome(), agentConsole(), agentFlow(), authPage(), authRequest(), badge(), bootstrap(), briefText() (+56 more)

### Community 2 - "Stock Reporting & Demand Forecasting"
Cohesion: 0.05
Nodes (32): HistoryForecastAdapter, create_product(), create_purchase_draft(), create_recurring_commitment(), CSVImportRequest, CSVImportResponse, delete_recurring_commitment(), export_dues_csv() (+24 more)

### Community 3 - "Multi-tenant Auth & Database Persistence"
Cohesion: 0.08
Nodes (9): decode_access_token(), get_current_user(), TokenData, check_db_connection(), get_db(), verify_tenant_ownership(), readiness_check(), BusinessDocumentModel (+1 more)

### Community 4 - "Evidence Verification & Document Search"
Cohesion: 0.07
Nodes (22): ClaimCorrectionRequest, correct_claim(), download_evidence(), get_evidence_details(), upload_evidence(), hybrid_search(), index_chunk(), IndexChunkDTO (+14 more)

### Community 5 - "Groq Provider & AI Extraction Schemas"
Cohesion: 0.07
Nodes (23): CommercialExtraction, ExtractedLine, GroundedAnswer, ProposedOperation, StrictOutput, extract_document(), GroqProvider, InferenceUnavailable (+15 more)

### Community 6 - "Multimodal AI & Reconciliation Adapters"
Cohesion: 0.05
Nodes (15): AIModelAdapter, ProviderUnavailableError, StructuredClaimExtraction, isolate_external_inference(), test_ai_boundary_missing_key_behavior(), test_evidence_file_size_limit(), test_postgresql_live_connection_and_schema(), client() (+7 more)

### Community 7 - "Operations & Container Logistics"
Cohesion: 0.09
Nodes (17): check_supplier_change(), ContainerMovementIn, create_handover(), create_reservation(), CreateReservationIn, list_containers(), list_handovers(), list_reservations() (+9 more)

### Community 8 - "Double-Entry Financial Ledger"
Cohesion: 0.08
Nodes (8): AccountType, JournalEntry, Posting, PostingDirection, PostingEngine, StandardAccount, TestFinancialInvariants, TestPostingContracts

### Community 9 - "Frontend Commerce & Currency Helpers"
Cohesion: 0.20
Nodes (36): money(), parsePaisa(), workspaceFetch(), AssistantNote(), ErrorLine(), Field(), Receipt(), Row (+28 more)

### Community 10 - "Goods Receiving & Credit Notes"
Cohesion: 0.07
Nodes (16): apply_credit_note(), ApplyCreditDTO, list_credit_notes(), list_goods_receipts(), record_goods_receipt(), RecordReceiptDTO, CreditNoteModel, GoodsReceiptModel (+8 more)

### Community 11 - "Case Triage & Confidence Assessment"
Cohesion: 0.10
Nodes (26): assess_case_confidence(), AssessCaseRequest, CaseCreateDTO, ClaimRegisterDTO, create_case(), get_case_details(), list_cases(), ReconciliationInputsDTO (+18 more)

### Community 12 - "React Workbench UI Root"
Cohesion: 0.10
Nodes (32): Actions, AgentPage, App(), AuthPage, Buying, CaseDetail, Cases, Connections (+24 more)

### Community 13 - "Statement Reconciliation & Disputes"
Cohesion: 0.13
Nodes (13): ClarificationReplyRequest, clarify_and_draft_action(), evaluate_reconciliation(), EvaluateReconciliationRequest, FactDTO, parse_clarification_reply(), AllocatedCreditFact, DemandFact (+5 more)

### Community 14 - "Web Application Manifest & Build Config"
Cohesion: 0.05
Nodes (35): dependencies, clsx, lucide-react, react, react-dom, react-router-dom, tailwind-merge, devDependencies (+27 more)

### Community 15 - "Package Concurrently Description"
Cohesion: 0.05
Nodes (36): description, devDependencies, concurrently, name, private, scripts, build, check:css (+28 more)

### Community 16 - "Portal And Actions"
Cohesion: 0.13
Nodes (19): SSLCommerzAdapter, SSLCommerzValidationResult, ActionCreateDTO, approve_action(), cancel_action(), create_action_draft(), DisputeDTO, execute_action() (+11 more)

### Community 17 - "Agents Orchestrator Run"
Cohesion: 0.12
Nodes (13): AgentEventDTO, AgentOrchestrator, AgentEventResponseDTO, AgentRunResponseDTO, AgentTaskResponseDTO, cancel_agent_run(), get_agent_events(), get_agent_run() (+5 more)

### Community 18 - "And Stock Reports"
Cohesion: 0.10
Nodes (16): DemandEngine, AllocationModel, AuditLogModel, ProductItemModel, StockMovementModel, StockoutPeriodModel, TenantModel, UnmetDemandModel (+8 more)

### Community 19 - "Reportspage Stockpage Navbar"
Cohesion: 0.19
Nodes (22): Navbar(), NavbarProps, Sidebar(), useLanguage(), ConnectionsPage(), DemoPage(), LandingPage(), MoneyPage() (+14 more)

### Community 20 - "Scenarios Scenario Domain"
Cohesion: 0.13
Nodes (13): get_tenant_baseline(), list_scenarios(), save_scenario(), SaveScenarioDTO, simulate_scenario(), SimulateRequestDTO, SimulateResponseDTO, ConditionalPromise (+5 more)

### Community 21 - "Merchant Create Summary"
Cohesion: 0.18
Nodes (23): CashCloseDTO, close_cash(), collect_due(), create_expense(), create_party(), create_product(), create_sale(), create_withdrawal() (+15 more)

### Community 23 - "Planning Operations Evidence"
Cohesion: 0.10
Nodes (23): Actions(), act(), post(), create(), Evidence(), correct(), search(), compare() (+15 more)

### Community 24 - "Auth Supportpages Layout"
Cohesion: 0.13
Nodes (22): Row, Session, Auth, enter(), logout(), Context, Protected(), useAuth() (+14 more)

### Community 25 - "Helpdesk Engine Document"
Cohesion: 0.11
Nodes (8): get_compliance_checklist(), list_corpus(), list_documents(), query_guidance(), SourcedGuidanceIn, upload_document(), UploadDocumentIn, BusinessHelpDeskEngine

### Community 26 - "Notifications Engine Notification"
Cohesion: 0.13
Nodes (10): emit_notification(), EmitNotificationDTO, get_daily_brief(), list_notifications(), mark_read(), resolve_notification(), snooze_notification(), SnoozeDTO (+2 more)

### Community 27 - "Actionableinbox Businesshelpdesk Languagecontext"
Cohesion: 0.16
Nodes (16): ActionableInbox(), ActionableInboxProps, DailyBriefView, InboxItemView, BusinessHelpDesk(), BusinessHelpDeskProps, ComplianceChecklistItem, SourcedGuidanceResult (+8 more)

### Community 28 - "Workbench Auth Models"
Cohesion: 0.20
Nodes (13): judge(), login(), logout(), me(), password_hash(), PasswordLogin, phone_number(), register() (+5 more)

### Community 29 - "Router Demo Session"
Cohesion: 0.14
Nodes (11): AuthResponse, get_demo_session(), JournalPostRequest, list_accounts(), login(), LoginRequest, post_journal_entry(), PostingDTO (+3 more)

### Community 30 - "Merchant Record Cash"
Cohesion: 0.22
Nodes (6): MerchantService, DailySnapshotModel, generate_uuid(), JournalEntryModel, PostingModel, test_cashflow_uses_tenant_owned_postings_and_excludes_internal_transfer_gross()

### Community 31 - "Badge Button Card"
Cohesion: 0.23
Nodes (15): Badge(), BadgeProps, Button(), ButtonProps, Card(), CardProps, CustomerPortalPage(), InvoiceData (+7 more)

### Community 32 - "Home Inferencedetails Charts"
Cohesion: 0.24
Nodes (15): AccountMix(), LineChart(), Row, AgentRail(), Home(), judgeScenarios, Row, Scenarios() (+7 more)

### Community 33 - "Auth Store Server"
Cohesion: 0.12
Nodes (14): createAuthStore(), checkRate(), issue(), failure(), normalizePhone(), passwordParams, scrypt, fixture (+6 more)

### Community 34 - "Domain Contracts Eval"
Cohesion: 0.12
Nodes (6): load_fixture(), test_cash_scenarios_contract_fixture(), test_liquidity_contract_fixture(), test_posting_contract_fixture(), test_reconciliation_contract_fixture(), run_eval()

### Community 35 - "Liquidity Domain Golden"
Cohesion: 0.18
Nodes (6): AccountBalances, LiquidityEngine, LiquidityEvaluation, Obligation, Promise, TestLiquidityContracts

### Community 36 - "Confidence And Cases"
Cohesion: 0.12
Nodes (9): ClaimInput, ConfidenceResult, evaluate_confidence(), client(), tenant_a_headers(), tenant_b_headers(), test_case_lifecycle_and_confidence_assessment(), test_confidence_fixture_exact_compliance() (+1 more)

### Community 37 - "Agents Cases Events"
Cohesion: 0.17
Nodes (15): AgentPage(), roleIcon(), Row, RunWorkspace(), load(), start(), request(), CaseDetail() (+7 more)

### Community 38 - "Browser Check Commerce"
Cohesion: 0.11
Nodes (12): browser, dir, profile, report, browser, dir, profile, report (+4 more)

### Community 39 - "Landing Runtime Domain"
Cohesion: 0.16
Nodes (11): facts, mountLanding(), answerFor(), refreshAgent(), refreshCase(), refreshChat(), refreshMotion(), refreshWorkflow() (+3 more)

### Community 40 - "Tsconfig Compileroptions Allowimportingtsextensions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 41 - "Agents Tenant Verifies"
Cohesion: 0.13
Nodes (8): client(), tenant_a(), tenant_b(), test_budget_exhaustion_halts_execution(), test_compound_case_multi_specialist_collaboration(), test_cross_tenant_isolation(), test_run_cancellation(), test_simple_query_optimization_skips_unnecessary_specialists()

### Community 42 - "Business Help Verifies"
Cohesion: 0.15
Nodes (9): client(), client_and_session(), db_session(), tenant_a(), tenant_b(), test_compliance_checklist_and_document_vault(), test_cross_tenant_document_vault_isolation(), test_sourced_guidance_with_statutory_citation() (+1 more)

### Community 44 - "And Phase11 Security"
Cohesion: 0.17
Nodes (6): client(), tenant_a_headers(), tenant_b_headers(), test_registration_prevents_role_escalation_on_existing_tenant(), test_stale_and_duplicate_action_execution_prevention(), test_tenant_isolation_prevents_cross_tenant_reads_and_writes()

### Community 45 - "Buyingdesk Confidencebadge Copilotchat"
Cohesion: 0.17
Nodes (13): BENGALI_DIGITS, BuyingDesk(), BuyingDeskProps, OfferEvaluationView, toBengaliNumber(), BENGALI_DIGITS, ClaimItem, ConfidenceBadge() (+5 more)

### Community 46 - "Buying Desk Bonus"
Cohesion: 0.15
Nodes (7): client(), tenant_a(), tenant_b(), test_compare_offers_landed_cost_and_bonus_calculation(), test_create_order_draft_does_not_execute_payment(), test_cross_tenant_isolation(), test_offer_ingestion_and_bonus_confidence_capping()

### Community 47 - "Copilot And Tenant"
Cohesion: 0.15
Nodes (7): client(), tenant_a(), tenant_b(), test_action_draft_does_not_mutate_ledger(), test_canonical_query_cash_balance(), test_copilot_session_creation_and_cross_tenant_isolation(), test_hybrid_retrieval_and_confidence_capping()

### Community 48 - "Notifications Tenant Voice"
Cohesion: 0.15
Nodes (7): client(), tenant_a(), tenant_b(), test_cross_tenant_isolation(), test_daily_executive_brief(), test_idempotent_notification_emission(), test_snooze_and_resolve_lifecycle()

### Community 49 - "Operations Tenant Verifies"
Cohesion: 0.17
Nodes (8): client(), client_and_session(), db_session(), tenant_a(), tenant_b(), test_cross_tenant_isolation_operations(), test_returnable_containers_deposit_tracking(), test_supplier_change_proposal_scope()

### Community 50 - "Retrieval Tenant Ensure"
Cohesion: 0.15
Nodes (7): client(), tenant_a(), tenant_b(), test_alias_and_bengali_digit_normalization(), test_cross_tenant_isolation_prevents_chunk_leakage(), test_exact_invoice_id_outranks_semantic_lookalike(), test_revocation_removes_chunk_from_retrieval()

### Community 51 - "Checkpoint Real Mjs"
Cohesion: 0.13
Nodes (10): entry, milestone, [phase,...files], progress, root, entry, milestone, [phase,...files] (+2 more)

### Community 52 - "Demand Unmet Engine"
Cohesion: 0.15
Nodes (4): analyze_demand_impact(), list_unmet_demands(), record_unmet_demand(), RecordUnmetDemandDTO

### Community 53 - "Demand Memory Tenant"
Cohesion: 0.18
Nodes (6): client(), tenant_a(), tenant_b(), test_cross_tenant_isolation(), test_demand_analysis_incorporates_unmet_requests_honestly(), test_record_unmet_demand_does_not_mutate_revenue()

### Community 54 - "Buying Supplier Order"
Cohesion: 0.23
Nodes (6): compare_supplier_offers(), CompareOffersDTO, create_order_draft(), CreateOrderDraftDTO, ingest_supplier_offer(), IngestOfferDTO

### Community 55 - "And Portal Actions"
Cohesion: 0.20
Nodes (3): auth_headers(), cashier_headers(), client()

### Community 57 - "Validate Study Validate-study"
Cohesion: 0.18
Nodes (6): cp, crypto, fs, path, root, vm

### Community 58 - "Preview Mjs Dir"
Cohesion: 0.18
Nodes (7): dir, { JSDOM }, repo, require, resolvePaths, script, skeleton

### Community 59 - "Validate Extension Handoff"
Cohesion: 0.22
Nodes (8): check(), checks, crypto, { execFileSync }, fs, path, root, visit()

### Community 61 - "Voicecopilot Choose Ensuresession"
Cohesion: 0.31
Nodes (7): VoiceCopilot(), ensureSession(), refresh(), send(), speak(), start(), stop()

### Community 62 - "Benchmark Run Run-benchmark"
Cohesion: 0.22
Nodes (7): benchmark, benchmarkPath, fs, outputPath, path, results, systems

### Community 63 - "Run Python Run-python"
Cohesion: 0.22
Nodes (8): args, fs, path, result, rootDir, { spawnSync }, venvUnix, venvWindows

### Community 64 - "Agenttimeline Agenteventview Agenttaskview"
Cohesion: 0.29
Nodes (7): AgentEventView, AgentTaskView, AgentTimeline(), AgentTimelineProps, BENGALI_DIGITS, ROLE_META, toBengaliNumber()

### Community 65 - "Operationshub Customerreservationview Operationshubprops"
Cohesion: 0.39
Nodes (6): CustomerReservationView, OperationsHub(), OperationsHubProps, ReservationItem, ReturnableContainerView, ShiftHandoverView

### Community 66 - "Tsconfig Node Compileroptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 67 - "Scan Secrets Scan-secrets"
Cohesion: 0.25
Nodes (6): { execSync }, fs, path, rootDir, secretRules, trackedFiles

### Community 68 - "Smoke Checkport Http"
Cohesion: 0.29
Nodes (6): checkPort(), http, path, rootDir, run(), { spawnSync }

### Community 69 - "Check Css Check-css"
Cohesion: 0.25
Nodes (7): checks, cssContent, cssPath, fs, path, rootDir, webDir

### Community 70 - "Verify Redesign Verify-ui-redesign"
Cohesion: 0.25
Nodes (7): checks, dir, env, results, root, sources, walk()

### Community 73 - "Demandtracker Bengali Digits"
Cohesion: 0.33
Nodes (6): BENGALI_DIGITS, DemandAnalysisView, DemandTracker(), DemandTrackerProps, toBengaliNumber(), UnmetDemandView

### Community 74 - "Receivingtracker Bengali Digits"
Cohesion: 0.33
Nodes (6): BENGALI_DIGITS, CreditNoteView, GoodsReceiptView, ReceivingTracker(), ReceivingTrackerProps, toBengaliNumber()

### Community 75 - "Http Check Http-check"
Cohesion: 0.29
Nodes (3): checks, cookie, report

### Community 76 - "Package Name Private"
Cohesion: 0.29
Nodes (6): name, private, scripts, start, test, type

### Community 77 - "Browser Check Accessibility"
Cohesion: 0.29
Nodes (4): browser, dir, profile, report

### Community 78 - "Eval Rag Eval-rag"
Cohesion: 0.29
Nodes (4): modes, { performance }, results, testCases

### Community 79 - "Verify Offline Verify-offline"
Cohesion: 0.33
Nodes (4): { execSync }, path, rootDir, steps

### Community 80 - "Eval Eval-ai Path"
Cohesion: 0.33
Nodes (4): path, res, rootDir, { spawnSync }

### Community 81 - "Browser Check Core"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 82 - "Browser Check Final"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 83 - "Browser Check Groq"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 84 - "Browser Check Judge"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 85 - "Browser Check Operations"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 86 - "Browser Check Planning"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 87 - "Browser Check Recording"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 88 - "Browser Check Support"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 89 - "Browser Check Voice"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

### Community 90 - "Browser Check Workbench"
Cohesion: 0.33
Nodes (4): browser, dir, profile, report

## Knowledge Gaps
- **8 isolated node(s):** `shongoti-api`, `clsx`, `tailwind-merge`, `@types/react`, `@types/react-dom` (+3 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 814 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserModel` connect `Merchant Create Summary` to `Supplier Offers & Copilot Engine`, `Stock Reporting & Demand Forecasting`, `Multi-tenant Auth & Database Persistence`, `Evidence Verification & Document Search`, `Operations & Container Logistics`, `Goods Receiving & Credit Notes`, `Case Triage & Confidence Assessment`, `Statement Reconciliation & Disputes`, `Portal And Actions`, `Agents Orchestrator Run`, `And Stock Reports`, `Scenarios Scenario Domain`, `Helpdesk Engine Document`, `Notifications Engine Notification`, `Workbench Auth Models`, `Router Demo Session`, `Buying Desk Bonus`, `Copilot And Tenant`, `Notifications Tenant Voice`, `Demand Unmet Engine`, `Demand Memory Tenant`, `Buying Supplier Order`, `Workbench Data Capabilities`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Are the 103 inferred relationships involving `UserModel` (e.g. with `approve_action()` and `cancel_action()`) actually correct?**
  _`UserModel` has 103 INFERRED edges - model-reasoned connections that need verification._
- **What connects `shongoti-api`, `clsx`, `tailwind-merge` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Supplier Offers & Copilot Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.06335403726708075 - nodes in this community are weakly interconnected._
- **Why does `Money` connect `Money Bdt Decimal` to `Supplier Offers & Copilot Engine`, `Liquidity Domain Golden`, `Double-Entry Financial Ledger`, `Statement Reconciliation & Disputes`, `Portal And Actions`, `Scenarios Scenario Domain`, `Domain Golden Setup`, `Merchant Record Cash`, `Sslcommerz Payment Gateway`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Money` (e.g. with `clarify_and_draft_action()` and `evaluate_reconciliation()`) actually correct?**
  _`Money` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Should `Web UI Router & Agent Console` be split into smaller, more focused modules?**
  _Cohesion score 0.11381074168797954 - nodes in this community are weakly interconnected._