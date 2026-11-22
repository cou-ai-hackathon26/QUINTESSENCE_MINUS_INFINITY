# BakiProof — Full Project Context & Proposal Modification Guide
**Target Event:** CoU TechNova AI Hackathon 2026 (Finance & Inclusion / FinTech)  
**Document Target:** `e:\mu idea\output\pdf\bakiproof-overleaf\main.tex` (Compiles to `main.pdf`)  
**Status Date:** 17 November 2026

---

## 1. Executive Summary & Purpose of this File
This document contains the entire background, competition constraints, core problem formulation, strategic synthesis, technical architecture, and document layout for **BakiProof**. 

Use this document as the prompt/context for any AI modifying `main.tex` or iterating on the proposal PDF. It provides all domain knowledge, design choices, competitor facts, and structural rules needed to make edits without breaking the 4-page layout or violating hackathon regulations.

---

## 2. Competition & Submission Parameters
* **Event:** CoU TechNova AI Hackathon 2026 (`https://coutechnova.xyz/`)
* **Category:** **Finance & Inclusion** (also referred to as *FinTech & Financial Intelligence*).
* **Submission Deadline:** **18 November 2026 at 23:59 BST**.
* **Phase 1 Outcome:** Top **30 teams** will be shortlisted for the on-site hackathon (not direct final winners).
* **Code Freeze Rule:** **No project code may be written before 21 November 2026**. Phase 1 allows research, proposal writing, system diagrams, UX wireframes, and synthetic dataset preparation.
* **Phase 2 Timeline:**
  * 21–23 Nov 2026: Pre-build in a brand new public repository.
  * 24 Nov 2026: 5-hour on-site final build, live demonstration, and evaluation.
* **Official Submission Deliverables on `coutechnova.xyz/register`:**
  1. **Four Narrative Form Fields (50 to 2,000 characters each):**
     * *Problem Statement*
     * *Proposed Solution*
     * *AI Component / Technologies*
     * *Expected Impact*
  2. **Proposal File Attachment:** PDF or DOCX, maximum **10 MB**.

---

## 3. Origin & Strategy: Merging BakiProof, DokanPulse & UNDERWRITE
The user initially had two proposals plus a previous repository:
1. **Original BakiProof (`BakiProof_CoU (1).pdf`):** Focused on supplier bill reconciliation using multi-agent reasoning to read informal Bangla/Banglish slips and chat logs.
   * *Strengths:* Distinctive AI reasoning core, tackles accounts payable reconciliation.
   * *Weaknesses:* Assumed suppliers will answer itemized requests cleanly; lacked an immediate intuitive financial consequence for the shopkeeper.
2. **DokanPulse (`DokanPulse_Concept_Proposal.pdf`):** Focused on overall store health, ledger tracking, and cash-flow monitoring.
   * *Strengths:* Clear financial framing ("will I have money to buy goods tomorrow?").
   * *Weaknesses:* Broad and generic scope; overlaps heavily with incumbents like TallyKhata.
3. **UNDERWRITE (`github.com/sakibul-shovon/UNDERWRITE`):** An earlier FinTech project.
   * *Contribution borrowed:* The architectural principle of **evidence-bounded authority** and **deterministic audit guards** (LLMs do not post ledger changes; deterministic code enforces limits and balances). Old blockchain/smart-contract code was discarded to comply with hackathon rules.

### Strategic Synthesis Decision:
* **Core Base:** Keep **BakiProof** as the core because "reconciling disputed supplier bills" is a genuine, unsolved problem in Bangladesh MSMEs.
* **Borrowed from DokanPulse:** The **Restocking / Working Capital Reserve** decision layer:
  > *"Before paying the supplier bill, know what cash will be left for tomorrow's inventory."*
* **Competitor Differentiation (vs TallyKhata / Dokan Khata):**
  * TallyKhata already does daily sales recording, customer credit (baki) tracking, automated SMS reminders, and QR code payments.
  * Attempting to build another "AI Khata" will lose. BakiProof focuses solely on **Accounts Payable Reconciliation** when bills, challans, returns, and partial receipts contradict each other.

---

## 4. The Core Problem & The Dual-Outcome Narrative
In Bangladeshi grocery/retail shops (mudir dokan), suppliers deliver goods on informal credit. When the delivery representative arrives for collection:
* The bill demands an amount (e.g., **BDT 25,000**).
* The shopkeeper has scraps of evidence: a partial bKash transaction screenshot (BDT 4,000) and a handwritten goods-return slip (BDT 3,000).
* **The Crucial Ambiguity:** Were those credits *already deducted* from the BDT 25,000 bill, or were they *omitted*?

### The Worked Example (Dual Outcome):
* **Available Cash:** BDT 26,000
* **Next-Day Restocking Reserve Required:** BDT 8,000
* **Outcome A (Credits Omitted):** Correct payable is BDT 18,000. Cash left is **BDT 8,000** (Restocking safe).
* **Outcome B (Credits Already Included):** Payable is BDT 25,000. Cash left is **BDT 1,000** (**BDT 7,000 shortfall** — cannot restock goods tomorrow).

*Key insight:* BakiProof must not naively deduct every receipt it sees; it must maintain competing interpretations until verified, preventing both overpayment and accidental underpayment.

---

## 5. System Architecture & Technical Workflow
The system consists of 4 workflow steps and 5 architectural layers:

### Merchant Workflow:
1. **Add:** Merchant captures bill photo, receipts, or chat logs.
2. **Review:** System highlights candidate mismatches, prior allocations, and unresolved items.
3. **Clarify:** Merchant approves or edits a short, polite Bangla question to send to the supplier (e.g., *`"এই বিলের টাকায় আগের পেমেন্ট আর ফেরত ধরা আছে?"`*).
4. **Decide:** Final decision card shows supported payable options and remaining working capital.

### Technical Architecture Layers:
1. **Evidence Store:** Relational store holding images, OCR crops, Banglish text, timestamps, and prior allocation history.
2. **Interpretation Layer (Multimodal LLM - Gemini API):** Extracts claims, dates, amounts, and candidate invoice links without asserting final truth.
3. **Challenge / Adversarial Layer:** A separate LLM prompt context inspects the raw sources looking specifically for contradictions, duplicate receipts, or conflicting dates.
4. **Deterministic Accounting Engine:** Pure code rules that cannot be overridden by AI:
   * A single transaction cannot be allocated beyond its actual value.
   * Unacknowledged returns cannot reduce confirmed payables.
   * Ambiguous or missing evidence remains flagged as unresolved.
5. **Restocking What-If Engine:** Evaluates remaining cash against merchant-set restocking minimums. Treats physical cash and MFS (bKash/Nagad) wallets separately due to withdrawal fees and supplier acceptance limits.

---

## 6. Document Architecture (`main.tex` / `main.pdf`)
* **File Location:** `E:\mu idea\output\pdf\bakiproof-overleaf\main.tex`
* **Compiled PDF:** `E:\mu idea\output\pdf\bakiproof-overleaf\main.pdf`
* **Compiler Target:** **XeLaTeX** (Overleaf-ready). Uses `fontspec` with local fonts (`fonts/NotoSerifBengali-Regular.ttf`) and TeX Gyre Pagella / Heros.
* **Page Budget:** **Strictly 4 A4 Content Pages** (No separate blank cover; page 1 opens immediately with the hook and problem).

### Page-by-Page Breakdown:
* **Page 1: The Financial Decision**
  * Header & Title: BakiProof — AI supplier reconciliation for small-shop working capital.
  * Hook: *"Before paying the bill, know what will be left."*
  * Worked Example Box: BDT 25,000 invoice with dual outcomes (preserving reserve vs BDT 7,000 shortfall).
  * Sample Bangla Clarification Card (rendered with Bengali typography).
  * Target User Segment: Grocery retailers with repeat credit suppliers (citing LightCastle 2026 MSME study).
  * Editable Header Variables (`\TeamName`, `\MemberNames`, `\ProposalDate`).
* **Page 2: Method & Architecture**
  * Merchant Workflow: 4-node TikZ flowchart (`Add` $\to$ `Review` $\to$ `Clarify` $\to$ `Decide`).
  * System Architecture: TikZ diagram showing Evidence Store, Multimodal Interpreter, Challenge Step, Accounting Engine, Decision Card, and Clarification Loop.
  * Short technical expositions: *"Why a matcher is not enough"* & *"Why a second model is not proof"*.
  * Three non-negotiable accounting rules.
* **Page 3: Product & Market Fit**
  * 4 Planned Modules: Bill Evidence Capture, Allocation Review, Bangla Clarification Card, Restocking What-If.
  * Documented Competitor Comparison Table: TallyKhata, Dext, Xero JAX vs BakiProof.
  * Mobile First Design: Low-bandwidth offline capture queue, camera crop.
  * Cash vs Wallet Liquidity distinction (referencing World Bank CPSD 2025).
  * Boundary Box: Defining the MVP limits (No live banking APIs needed during demo).
* **Page 4: Delivery, Evaluation & References**
  * Adversarial Behavior Matrix: 5 specific tricky cases (duplicate invoice allocations, partial receipts, unacknowledged returns, etc.).
  * Evaluation Methodology: **24 synthetic case pairs** with held-out splits to test robustness.
  * Correctness vs Usefulness metrics.
  * 4-Day Build Timeline (21 Nov: Setup & schema $\to$ 22 Nov: Ambiguity engine $\to$ 23 Nov: Restocking UI $\to$ 24 Nov: 5-hour final demo).
  * Merchant interview validation plan (5–8 retailers, 2–3 suppliers).
  * Six primary academic & industry citations (LightCastle, World Bank, TallyKhata, Dext, Xero, Gemini API).

---

## 7. Registration Form Answers (Ready to Use)
These are already drafted to fit the 50–2,000 character limit on `coutechnova.xyz/register`:

### 1. Project Title:
`BakiProof - AI Supplier Reconciliation for Small-Shop Working Capital`

### 2. Problem Statement:
> A grocery retailer needs to pay a supplier today and buy fresh stock tomorrow. The bill says BDT 25,000, but a payment record and a goods-return slip suggest credits may be missing. If those credits were already included, deducting them again would underpay the supplier. If they were omitted, paying the full demand could consume the next day's stock money. The records are scattered across paper, photos and ambiguous Bangla/Banglish messages. Our initial users are retailers buying on credit from repeat suppliers, with partial payments or returns and some supporting records. We will investigate their last actual mismatch to establish how often this happens, how much work it creates and whether the records are sufficient to help.

### 3. Proposed Solution:
> BakiProof is a mobile-first assistant for checking a supplier bill before settlement. The merchant adds the bill and selected records. The app links claims to their sources, flags reused receipts and keeps alternative balances when the evidence is ambiguous. It prepares a short Bangla clarification for the merchant to review and share. A new reply updates the case; a vague or missing reply leaves the unresolved facts visible. The final card shows the supported payable and what settling it would leave for the merchant's chosen restocking reserve. Cash and wallet funds are kept separate where acceptance or timing matters. During the three-day pre-build we will implement one merchant's capture-to-review workflow, followed by testing and a paired-case demonstration in the five-hour final. Live payment-provider integration is not required.

### 4. AI Component / Technologies:
> We plan to use the Gemini multimodal API to interpret receipt images and Bangla/Banglish messages into structured claims with source references. Retrieval supplies relevant invoices and recorded payment allocations. For ambiguous matches, a separate model context examines the original evidence for contradictions. A clarification step proposes an answerable question that could change the settlement decision, accounting for incomplete replies. Deterministic code enforces allocation limits and calculates balances; the model cannot silently post adjustments. The planned stack is TypeScript, a mobile web interface and a relational evidence/ledger store. We will fix the model version after Bangla-case trials and compare the workflow with date/amount rules and a strong single tool-using model at comparable budgets. Offline capture is in scope; full offline AI is a later experiment.

### 5. Expected Impact:
> The intended benefit is less work reconstructing supplier bills and fewer unsupported settlements that either drain a shop's restocking money or leave suppliers underpaid. We will prepare 24 synthetic case pairs where one changed fact must change the financial conclusion, keeping related variants in the same development or test split. Measures include wrong allocations, unsupported final balances, duplicate-allocation violations, resolved-case coverage, useful first clarifications, review time and model cost. We plan interviews with 5-8 retailers and 2-3 suppliers, using consented, redacted examples where available. These are proposed activities, not completed validation. The demo's amounts will be labelled illustrative, and controlled test results will not be presented as real-world savings. Repeat use, capture effort and willingness to pay will determine whether the product merits a pilot.

---

## 8. Instructions & Rules for the Next AI Modifying `main.tex`
When instructing an AI to modify `main.tex`, pass the following constraints:

1. **Keep the 4-Page Budget Exact:**
   * Every page has a dedicated role: Page 1 (Hook & Worked Example), Page 2 (Architecture & Rules), Page 3 (Product & Competitors), Page 4 (Evaluation & Roadmap).
   * Do not let content spill onto a 5th page. Keep `\newpage` at line boundaries 104, 155, and 204.
2. **XeLaTeX & Font Compatibility:**
   * Uses `\setmainfont{texgyrepagella}` and `\setsansfont{texgyreheros}`.
   * Any Bengali text must be wrapped inside `{\bengali ...}` to utilize `fonts/NotoSerifBengali-Regular.ttf`.
3. **No External Image Files in LaTeX:**
   * All diagrams are drawn inline using native **TikZ** code (`\begin{tikzpicture}`). Never introduce `\includegraphics` pointing to local PNG/JPG files that might break on Overleaf.
4. **Tone and Voice (Anti-AI-Detector & Credibility Guidelines):**
   * Avoid buzzwords like "revolutionizing", "synergy", "game-changing", or "seamless".
   * Never claim that interviews or merchant savings have *already* occurred. Clearly label them as planned validation or synthetic controlled trials.
   * Frame AI as a specialized claim extractor and ambiguity challenger, while deterministic code retains full ledger control.
5. **Team Configuration:**
   * Team and member names should be edited only via `\newcommand{\TeamName}{...}` and `\newcommand{\MemberNames}{...}` at lines 4–5 of `main.tex`.
