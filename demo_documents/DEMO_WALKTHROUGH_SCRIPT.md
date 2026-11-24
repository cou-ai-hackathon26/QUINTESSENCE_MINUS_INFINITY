# Shongoti — Live Judge Demonstration Walkthrough Script
**Hackathon Task #45: Quintessence Minus Infinity**
*Bilingual AI-Assisted Supplier Settlement Review for Bangladeshi MSMEs*

---

## 📂 The Generated Demo Files in `demo_documents/`

All demo documents have been generated and are ready for you to use or show:

| File Name | Format | Purpose & Scenario |
|---|---|---|
| [`01_Supplier_Invoice_INV-8891.pdf`](file:///d:/bbb/sonngoti/demo_documents/01_Supplier_Invoice_INV-8891.pdf) / [`.png`](file:///d:/bbb/sonngoti/demo_documents/01_Supplier_Invoice_INV-8891.png) | PDF / Image | **Demand Document**: Wholesale Bill from *মেসার্স কালাম ট্রেডার্স* for **৳45,000** (oil, rice, biscuits) to *রহিম স্টোর*. |
| [`02_Payment_Receipt_bKash_20k.png`](file:///d:/bbb/sonngoti/demo_documents/02_Payment_Receipt_bKash_20k.png) / [`.pdf`](file:///d:/bbb/sonngoti/demo_documents/02_Payment_Receipt_bKash_20k.pdf) | Image / PDF | **Payment Slip**: bKash Merchant Payment of **৳20,000** (TrxID: `9K72JFL18A`, Ref: `INV-8891`). |
| [`03_Return_Damage_Challan_5k.pdf`](file:///d:/bbb/sonngoti/demo_documents/03_Return_Damage_Challan_5k.pdf) / [`.png`](file:///d:/bbb/sonngoti/demo_documents/03_Return_Damage_Challan_5k.png) | PDF / Image | **Goods Return Voucher**: 4 Cartons damaged mustard oil returned to delivery rep Kalam for **৳5,000**. |
| [`04_Bangla_Supplier_Clarification.txt`](file:///d:/bbb/sonngoti/demo_documents/04_Bangla_Supplier_Clarification.txt) / [`04_Supplier_Audio_Voice_Note.mp3`](file:///d:/bbb/sonngoti/demo_documents/04_Supplier_Audio_Voice_Note.mp3) | Text / Audio | **Bangla Supplier Message**: Supplier clarifies: *"২০,০০০ টাকার বিকাশ পাইছি, কিন্তু ৫,০০০ টাকার ফেরত মাল এখনও হিসেবে বাদ দেই নাই।"* |
| [`05_Challenge2_Cropped_Unreadable_Receipt.png`](file:///d:/bbb/sonngoti/demo_documents/05_Challenge2_Cropped_Unreadable_Receipt.png) | Image | **Challenge 2 (Honesty)**: Degraded/cropped voucher where amount is torn off. Proves Shongoti never hallucinates missing numbers. |
| [`06_Challenge2_Contradictory_Supplier_SMS.txt`](file:///d:/bbb/sonngoti/demo_documents/06_Challenge2_Contradictory_Supplier_SMS.txt) / [`06_Challenge2_Contradictory_Voice.mp3`](file:///d:/bbb/sonngoti/demo_documents/06_Challenge2_Contradictory_Voice.mp3) | Text / Audio | **Challenge 2 (Contradiction)**: First message confirms payment; second message denies receiving it. Proves conflict detection. |
| [`07_Challenge1_Multi_Invoice_LumpSum_Batch.pdf`](file:///d:/bbb/sonngoti/demo_documents/07_Challenge1_Multi_Invoice_LumpSum_Batch.pdf) / [`.png`](file:///d:/bbb/sonngoti/demo_documents/07_Challenge1_Multi_Invoice_LumpSum_Batch.png) | PDF / Image | **Challenge 1 & Direction**: Statement with 3 open invoices (৳15k, ৳25k, ৳10k) and Shongoti's proposed split of a ৳30,000 lump sum. |

---

## ⏱️ Step-by-Step 3-Minute Live Judge Demo Flow

### 1. The Context (30 seconds)
> *"Judges, Bangladeshi retail grocers deal with scattered wholesale bills, bKash slips, damage return slips, and Bangla voice notes from suppliers. Neither the shopkeeper nor the supplier knows what was actually deducted from the bill. Shongoti solves this by turning scattered evidence into an honest, audit-ready settlement brief."*

### 2. The Core Idea Demo (90 seconds)
1. **Show the 3 scattered sources:**
   - Bill `INV-8891`: **৳45,000**
   - bKash Payment Slip: **৳20,000**
   - Damaged Oil Return Slip: **৳5,000**
2. **The Problem:**
   Without clarification, 4 mathematical hypotheses exist:
   - $H_1$: Both included $\rightarrow$ Due: ৳45,000
   - $H_2$: Return excluded $\rightarrow$ Due: ৳40,000
   - $H_3$: Payment excluded $\rightarrow$ Due: ৳25,000
   - $H_4$: Neither included $\rightarrow$ Due: ৳20,000
3. **Play or show Document 04 (`04_Supplier_Audio_Voice_Note.mp3` or `.txt`):**
   *"রহিম ভাই, ২০,০০০ টাকার বিকাশ পাইছি, কিন্তু ৫,০০০ টাকার ফেরত মাল এখনও বাদ দেই নাই।"*
4. **Result in Shongoti:**
   - Shongoti parses the natural Bangla statement:
     - `payment_included = True`
     - `return_included = False`
   - Shongoti automatically isolates **Hypothesis 2 (REC-003)**:
     $$\text{Net Payable} = 45,000 - 5,000 = \mathbf{৳40,000}$$
   - Generates a **reviewable settlement draft action** for the store owner to approve with one click.

### 3. Challenge 2: System Honesty & Cropped Receipts (30 seconds)
1. **Show Document 05 (`05_Challenge2_Cropped_Unreadable_Receipt.png`):**
   - The receipt amount is torn or cropped off.
2. **Point out to judges:**
   - *"Typical LLM apps hallucinate a random number. Shongoti has an evidence-support policy: confidence is immediately capped at 59%, status flags `needs_review`, and the brief explicitly states: 'Unreadable amount — manual owner verification required'."*

### 4. Challenge 1 & Direction: Splitting One Payment Across Invoices (30 seconds)
1. **Show Document 07 (`07_Challenge1_Multi_Invoice_LumpSum_Batch.pdf`):**
   - 3 open invoices from Kalam Traders totaling ৳50,000:
     - `INV-101`: ৳15,000 (Due Nov 01)
     - `INV-102`: ৳25,000 (Due Nov 10)
     - `INV-103`: ৳10,000 (Due Nov 20)
   - Merchant makes **one lump-sum payment of ৳30,000**.
2. **Show the proposed split:**
   - **Oldest-First Strategy:**
     - `INV-101`: ৳15,000 (100% cleared, ৳0 due)
     - `INV-102`: ৳15,000 (partially cleared, ৳10,000 remaining)
     - `INV-103`: ৳0 (৳10,000 remaining)
   - Guaranteed exact integer paisa arithmetic (no floating-point rounding errors or phantom balances).
