# Shongoti — Developer Handover & Production Runbook

**Project:** Shongoti (সংগতি) — Bilingual (Bangla/English) Financial Workspace for MSMEs  
**Target Repository:** `sakibul-shovon/Shongoti` (branch `main`)  
**Handoff Date:** 23 November 2026  
**Implementation Team:** Quintessence Minus Infinity (Sakibul Hassan Shovon, Sabbir Ahmed, Sanjid Talukder)

---

## 1. Verified Runtime Environment & System Requirements

- **Node.js:** v20.x or v24.x (Tested on Node v24.20.0)
- **pnpm:** v9.x (Tested on pnpm v9.1.0)
- **Python:** 3.12.x (Tested on Python 3.12.15 with virtualenv at `apps/api/.venv`)
- **Database:** PostgreSQL 16.8 (Live local instance on `127.0.0.1:5432/shongoti`) or SQLite 3 (Memory / file for offline tests)
- **Operating System:** Windows, Linux, or macOS

---

## 2. Quick Start & Setup for Secondary Developer

### A. Clone & Install Dependencies
```bash
git clone https://github.com/sakibul-shovon/Shongoti.git
cd Shongoti

# Install JavaScript workspace dependencies
pnpm install

# Setup Python API virtual environment
cd apps/api
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary alembic pydantic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" python-multipart pypdf httpx pytest anyio
cd ../..
```

### B. Database Migrations
```bash
# Run all 6 Alembic migrations to head
pnpm db:migrate

# Check current revision status
pnpm db:check
```

### C. Run the Comprehensive Offline Verification Gate
The entire project is governed by a unified offline verification gate:
```bash
pnpm verify:offline
```
This single command executes and validates:
1. **Frontend Typecheck:** `tsc --noEmit` across React components and i18n dictionaries.
2. **Domain Golden Contracts:** 34 golden contract tests enforcing integer paisa arithmetic, capacity allocation, 4 supplier reconciliation hypotheses, and 7-day spending impact scenarios.
3. **API, Persistence & Security Tests:** 45 pytest tests verifying tenant isolation, JWT auth, merchant sales, wallet transfers with 1.85% cashout fee, action approvals, SSLCommerz callback tamper rejection, stock WAC calculation, operating reports, prompt injection defense, and upload path sanitization.
4. **Web Unit & Workflow Tests:** 8 vitest tests verifying bilingual switching and complete navigation across all MSME modules.
5. **Web Production Build:** Production Vite compilation emitting optimized bundle (`dist/index.html`).
6. **Evaluation Benchmark:** 24 paired story families / 48 cases comparing rules reasoning vs single model vs conditional multi-role vs gold-fact engine.
7. **Secrets & Credentials Scan:** 172 tracked repository files scanned for private keys or live API tokens (0 leaks).
8. **E2E & UI Workflow Gate:** Checking 14 application pages, responsive CSS rules (360px mobile, 768px tablet, 1440px desktop), and `prefers-reduced-motion` accessibility.

---

## 3. Demo Accounts & Credentials

The database includes predefined test accounts for local verification:
- **Demo Owner:**
  - Phone: `01700000001`
  - OTP: `123456`
  - Role: `owner` (Full administrative, financial, and withdrawal permissions)
- **Demo Cashier:**
  - Phone: `01700000002`
  - OTP: `123456`
  - Role: `cashier` (Sales and debt collection allowed; owner withdrawal, CSV export, and full profit views strictly denied with HTTP 403)

---

## 4. Containerized Local Deployment

To run Shongoti via Docker containers:
```bash
# Copy production environment variables
cp .env.production.example .env

# Build and start services (PostgreSQL db, FastAPI api, Nginx static web)
docker compose up -d --build

# Run deployment smoke test
node scripts/smoke-test.js
```
The application will be accessible at:
- Frontend Web App: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`
- Readiness Endpoint: `http://localhost:8000/ready`

---

## 5. Architectural & Financial Invariants Enforced

- **D001 — Money Primitive:** Strict integer paisa (৳1.00 = 100 paisa). Floating-point arithmetic is prohibited and rejected by domain validation.
- **D002 — Balanced Postings:** Double-entry ledger requires balanced debits and credits for all posted journal entries.
- **D003 — Actual vs Scenario Funds:** Projected future customer debt collections or conditional promises are strictly excluded from current liquid spendable cash.
- **D004 — Supplier Reconciliation:** All 4 original hypotheses preserved (REC 001 - 004); funds allocated to one invoice cannot be reused on another.
- **D007 — Forecast Cold Start:** Statistical forecasting is withheld if fewer than 14 daily sales records exist. When >= 14 records exist, rolling-origin backtest evaluates Naive vs Moving Average with calibrated MAE bounds.
- **D009 — WhatsApp Gating:** Debt-collection automation via WhatsApp is flagged with regulatory policy restrictions; manual and scoped portal links provided.
- **D011 — WAC Costing & Profit Suppression:** Inventory is valued using Weighted Average Costing (WAC). When purchase cost data is incomplete, profit reporting is suppressed rather than reporting unsupported profit based on ৳0 cost.
- **Bilingual Interface:** Every UI screen supports both Bengali (বাংলা) as the default first-class experience and instant toggle to English with localStorage persistence.

---

## 6. Scope & Truthful Status Matrix

| Phase | Description | Status | Evidence Checkpoint |
|---|---|---|---|
| **00** | Repository & verified handoff | Complete | `docs/evidence/phase-00/git-checkpoint.json` (`6c6d389`) |
| **01** | Executable foundation & contracts | Complete | `docs/evidence/phase-01/git-checkpoint.json` (`3808c0e`) |
| **02** | Exact financial domain (34 golden tests) | Complete | `docs/evidence/phase-02/git-checkpoint.json` (`8b34a32`) |
| **03** | Database, auth & tenant isolation | Complete | `docs/evidence/phase-03/git-checkpoint.json` (`0c9cada`) |
| **04** | Evidence ingestion & AI boundary | Blocked (Live AI) | P04-T01..T03 verified (`8e15789`); P04-T04 blocked pending `GEMINI_API_KEY` |
| **05** | Supplier reconciliation & AI clarification | Blocked (Live AI) | Blocked on live AI key; local deterministic reconciliation verified |
| **06** | Connected daily merchant workflow | Complete | `docs/evidence/phase-06/git-checkpoint.json` (`af708cb`) |
| **07** | Liquidity outlook & Decision Lab scenarios | Complete | `docs/evidence/phase-07/git-checkpoint.json` (`e4265e9`) |
| **08** | Action center, portal & SSLCommerz | Complete | `docs/evidence/phase-08/git-checkpoint.json` (`ba38e5f`) |
| **09** | Stock, evaluated forecasts & reports | Complete | `docs/evidence/phase-09/git-checkpoint.json` (`332851e`) |
| **10** | Complete product UI & accessibility | Complete | `docs/evidence/phase-10/git-checkpoint.json` (`0548800`) |
| **11** | Evaluation benchmark & security gates | Complete | `docs/evidence/phase-11/git-checkpoint.json` (`fa6131e`) |
| **12** | Deployment runbook & handover | Complete | `docs/evidence/phase-12/git-checkpoint.json` |

### Open Dependencies & Production External Unknowns:
1. `GEMINI_API_KEY`: Real live multimodal parsing requires approved API quota. Offline boundary, native PDF parsing, and deterministic rules matching are fully verified.
2. `SSLCOMMERZ_STORE_ID / STORE_PASS`: Configured sandbox lifecycle and callback tampering defenses are verified; production merchant credentials require merchant onboarding.
3. External Cloud Hosting: Local Docker container deployment verified. Cloud hosting (AWS / GCP / VPS) deferred pending team infrastructure provisioning.
