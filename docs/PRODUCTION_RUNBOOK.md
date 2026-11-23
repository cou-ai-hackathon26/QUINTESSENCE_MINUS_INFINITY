# Shongoti (সংগতি) — Production & Operational Runbook

**Date:** 2026-11-23  
**Version:** 1.0.0-rc.1  
**Target Environment:** Local Docker / Cloud Linux (Ubuntu 22.04 LTS / Debian 12)  
**Primary Database:** PostgreSQL 16+ (with SQLite static pool test double for offline CI)  

---

## 1. System Architecture Overview

Shongoti is a Bangla-first MSME financial workspace built on deterministic financial integrity and verifiable AI boundaries:
```
+-------------------------------------------------------------+
|                      React + Vite UI                        |
|  - Bangla default + English toggle (Bilingual)              |
|  - Responsive: 360px mobile / 768px tablet / 1440px desktop  |
|  - Accessible components: ConfidenceBadge, ActionableInbox, |
|    AgentTimeline, BuyingDesk, OperationsHub, BusinessHelp   |
+------------------------------+------------------------------+
                               | REST / JSON
+------------------------------v------------------------------+
|                     FastAPI API Server                      |
|  - Multi-tenant isolation (TenantModel, UserModel, RBAC)     |
|  - Integer paisa arithmetic (0 floating point)              |
|  - Balanced double-entry ledger (Debits == Credits)         |
|  - Canonical ledger separation from future projections       |
+------------------------------+------------------------------+
                               |
      +------------------------+------------------------+
      |                                                 |
+-----v----------------------+            +-------------v-------------+
|    PostgreSQL 16 Engine    |            |   Bounded AI Boundaries   |
|  - 16 Alembic migrations   |            |  - Google Gemini adapter  |
|  - Strict Foreign Keys     |            |  - evidence-support-v1    |
|  - Zero financial mutation |            |    index (0-100, cap 59)  |
|    on drafts/unmet demands |            |  - Deterministic fallback |
+----------------------------+            +---------------------------+
```

---

## 2. Invariant & Governance Guarantees

1. **Integer Paisa Currency Storage:**
   - Every monetary transaction, landed cost, fee, credit note, and reservation deposit is stored and calculated in integer paisa (১ টাকা = ১০০ পয়সা).
   - Floating-point arithmetic on currency is strictly forbidden and rejected at the domain contract layer.
2. **Balanced Double-Entry Books:**
   - Every journal entry posting requires `sum(debits) == sum(credits)`.
   - Single-sided or unbalanced postings raise invariant errors.
3. **Canonical Cash Separation:**
   - Physical spendable cash (Cash in Till, bKash, Nagad) is strictly separated from expected future receivables, customer promises, or unmet customer demand logs.
   - Recording an unmet customer demand or a customer order reservation NEVER increases revenue or accounts receivable.
4. **Exactly-Once Credit Recovery:**
   - Supplier credit notes cannot be applied more than once (`applied_to_bill` rejects duplicate reuse with HTTP 400).
5. **Evidence-Support Confidence (`evidence-support-v1`):**
   - Visible confidence index (০-১০০).
   - Missing critical facts (missing SKU, unknown return cutoff, unverified bonus condition) strictly cap confidence at 59, enforcing human review.
   - No calibrated probability claims or false certainty.

---

## 3. Configuration & Secrets Management

Store configuration in environment variables or `.env` files. Secrets are never committed to Git:
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/shongoti

# Security
JWT_SECRET=your_super_secret_hmac_sha256_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Provider Boundary (Optional / Sandboxed)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Payment Sandboxes
SSLCOMMERZ_STORE_ID=sandbox_shongoti
SSLCOMMERZ_STORE_PASS=sandbox_pass
SSLCOMMERZ_IS_SANDBOX=true

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
```

---

## 4. Database Lifecycle & Migrations

All 16 schema versions are versioned in `apps/api/alembic/versions/`:
- `001_initial_schema`: Tenants, Users, Accounts, Journals, Postings.
- `002_evidence_schema`: Evidence documents and extracted claims.
- `003_merchant_workflow`: Daily snapshots, parties, products, stock movements.
- `004_scenarios_schema`: 7-day cash liquidity scenarios.
- `005_actions_and_portal`: Customer invoice portal, SSLCOMMERZ gateway payments.
- `006_stock_reports_commitments`: WAC recalculation, reorder alerts, commitments.
- `007_cases_provenance`: Discrepancy cases, audit log, confidence scores.
- `008_hybrid_memory`: Semantic chunking, document embeddings, RRF indices.
- `009_agent_workspace`: Multi-agent runs, tasks, timeline events.
- `010_copilot_workspace`: Scoped copilot sessions, voice draft reviews.
- `011_buying_desk`: Supplier offers, landed unit costs, buying comparisons.
- `012_receiving_and_returns`: Goods receipts, shortage deductions, credit notes.
- `013_demand_memory`: Unmet customer requests, availability stockout windows.
- `014_notifications_inbox`: Actionable inbox alerts, daily voice briefs.
- `015_everyday_operations`: Reservations, returnable crates, shift handovers.
- `016_business_help_desk`: Compliance document vault, regulatory corpus.

To execute migrations:
```bash
pnpm db:migrate
pnpm db:check
```

---

## 5. Backup, Restore & Rebuilding Indexes

### PostgreSQL Database Dump:
```bash
pg_dump -U postgres -d shongoti -F c -b -v -f /backups/shongoti_$(date +%Y%m%d_%H%M%S).dump
```

### PostgreSQL Database Restore:
```bash
pg_restore -U postgres -d shongoti -v -c /backups/shongoti_backup.dump
```

### Rebuilding Hybrid Retrieval Indexes:
If embedding models change or documents require re-indexing:
1. Re-index scripts only read `evidence_documents` and recreate `document_chunks`.
2. Financial ledger tables (`journal_entries`, `postings`) are NEVER mutated during re-indexing.

---

## 6. Verification & Health Monitoring

### Health & Readiness Probes:
- `GET /health`: Liveness probe (HTTP 200 `{"status": "ok"}`).
- `GET /ready`: Readiness probe verifying live database connectivity (HTTP 200 `{"status": "ready"}`).

### Full Offline Verification Suite:
```bash
node scripts/verify-offline.js
```
Runs 8 strict verification gates:
1. Frontend Typecheck (`tsc --noEmit`)
2. Domain Golden Contracts (34 tests)
3. API, Persistence & Security Tests (128 tests)
4. Web Unit & Workflow Tests (27 tests)
5. Web Production Build (`vite build`)
6. CSS & Mobile Accessibility Scan (360px viewport, focus rings, reduced motion)
7. Security & Secrets Scan (299 tracked files verified clean)
8. Architecture & Invariant Benchmark (48 paired test cases)
