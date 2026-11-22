# Shongoti - Submission Answers

**Team:** Quintessence Minus Infinity  
**Members:** Sakibul Hassan Shovon, Sabbir Ahmed, Sanjid Talukder  
**Category:** Finance & Inclusion

Each narrative field allows **2,000 characters**, including spaces and line breaks. Copy only the answer beneath each field heading.

| Field | Characters | Words | Allowed characters |
|---|---:|---:|---:|
| Project / idea title | 53 | 9 | Up to 120 |
| Problem statement | 1,815 | 288 | 50-2,000 |
| Proposed solution | 1,812 | 281 | 50-2,000 |
| AI component / technologies | 1,900 | 265 | 50-2,000 |
| Expected impact | 1,782 | 269 | 50-2,000 |

## Project / idea title

Shongoti - Check What You Owe Before Paying Suppliers

## Problem statement

A shopkeeper has paid part of a supplier's bill. The supplier now asks for the balance. Has the earlier payment already been deducted?

Consider a Bangladeshi grocery shop facing a BDT 25,000 supplier demand. Its records show a BDT 4,000 payment and an agreed BDT 3,000 credit for returned goods, both against this bill.

● If neither amount is reflected in the demand, BDT 18,000 remains due.
● If both were already deducted before the demand was issued, BDT 25,000 is still due.

Both calculations are valid under different facts. The arithmetic is simple; the missing detail is what the supplier has already counted. Deducting every receipt risks underpaying. Accepting the demand without checking risks paying twice.

Our first users are small grocery shops buying stock on credit from regular suppliers. Their relevant records may be spread across paper bills, transfer receipts, return slips and Bangla/Banglish messages. Similar amounts can belong to different bills. A supplier saying "payment received" may still leave the deduction unclear.

A receipt records an event; establishing the current balance requires checking which bill it belongs to, how much has already been used and whether it is reflected in the demand. Incomplete history or a vague reply can leave more than one defensible amount.

During a collection, the shopkeeper must reconstruct these facts while keeping cash for the next stock purchase. Entering the supplier's stated balance in a ledger preserves the number but does not resolve the disagreement behind it.

The financial consequence runs both ways: an overlooked payment or return can consume restocking money, while a repeated deduction leaves the supplier short. The shop needs a way to trace the amount back to its records and identify the exact missing fact before paying.

## Proposed solution

We will build a mobile-friendly web prototype that helps a shopkeeper check a supplier demand before paying. The first screen shows an amount supported by the records, or the specific question still blocking a decision.

The shopkeeper will:

1. Add one bill, relevant payment receipts, return slips and selected messages. Reuse reviewed history rather than re-entering the whole account.
2. Check proposed links between records and the bill. Open the source behind any amount, correct a misread value and see payments already used on other bills.
3. Review the remaining payable scenarios. Shongoti separately checks whether a payment or return belongs to this bill and whether the supplier has already deducted it.
4. Share a focused Bangla question, add the reply and review the updated settlement brief. The supplier needs no account; the merchant shares the question in an existing conversation.

For example, if the return is confirmed as not deducted but the payment remains unclear, ask: "Was the BDT 4,000 payment already deducted from today's BDT 25,000 demand?" The answer separates BDT 22,000 from BDT 18,000. A partial reply leaves that difference open.

The shopkeeper can enter usable cash and a restocking reserve to see what each supported payment would leave. The reserve explains the consequence; it does not change the amount owed. Every account adjustment requires merchant approval.

Our demonstration will follow one complete collection: one shop, one supplier, one bill, a payment, a return and a misleading receipt already used on another bill. We will show capture, source review, clarification and an approved adjustment with a settlement brief, plus a no-reply path. Uploaded demo records and a small, manually supplied history avoid dependency on live banking integrations.

## AI component / technologies

We will use a Gemini multimodal model to interpret bill images and informal Bangla/Banglish messages. TypeScript will coordinate calls, structured JSON will carry claims with source references and unknown fields, and a relational store will hold records and allocations.

The key reasoning task: "payment received" acknowledges an event; it does not establish "payment already deducted from today's balance." The model must link language to the right bill and retain alternatives when the evidence leaves a fact open.

A conditional multi-agent workflow uses four roles, with separate contexts on the same model:

● Evidence Reader extracts candidate amounts, events and source references.
● Reconciler proposes links between bills, payments and returns, keeping alternative interpretations of what is already deducted.
● Skeptic rechecks original evidence and allocation history without the Reconciler's explanatory narrative, looking for unsupported deductions and contradictions.
● Clarifier selects a missing fact whose answer changes the payable amount, then drafts a supplier-ready Bangla question.

Once the return is established as not deducted, asking about the payment separates BDT 22,000 from BDT 18,000; asking about the return again adds nothing.

Inputs are uploaded bills, receipts, return slips, selected messages and merchant-provided history. Deterministic tools validate source references, enforce payment-allocation limits, calculate balances and reject approvals based on outdated records.

Agents cannot write confirmed balances; changes require merchant approval. Missing evidence, disagreement or a failed call leaves the affected decision open. Explicit, reviewed matches follow a rules-only path; extra calls are reserved for ambiguity.

We will compare it with one tool-using model using the same records and accounting tools, measuring errors, response time and API cost.

## Expected impact

A shopkeeper should be able to explain a supplier payment by pointing to the records behind it. Shongoti aims to make that possible with the bill, receipts and messages already at hand.

For merchants, the intended benefit is fewer overlooked payments or returns and less time reconstructing what happened. For suppliers, it is protection against the same amount being deducted twice and a clear explanation of any disputed balance.

The working-capital consequence is concrete. In our illustrative case, a shop has BDT 26,000 available and needs BDT 8,000 for stock. Paying BDT 25,000 leaves BDT 1,000; paying BDT 18,000 leaves BDT 8,000. The evidence determines which amount is justified. Shongoti must show the correct obligation even when it leaves a cash shortfall.

Access starts with one bill and familiar Bangla records. The merchant need not migrate the entire shop ledger, and the supplier can reply through an existing conversation. Without a reply, the merchant still receives a discrepancy note and a specific unresolved question.

We will measure:

● Financial correctness: final amounts and payment links against reviewed case answers, including duplicate deductions and unsupported conclusions.
● Merchant effort: time and corrections needed to review the same records manually and with Shongoti.
● Clarification value: whether the first question separates possible amounts, and whether partial replies update only what they establish.
● Useful completion: the share of cases reaching a supported amount, alongside cases correctly left unresolved. Refusing every case would not count as success.

We will count a financial correction only when the records establish a valid, previously uncounted payment or return. Amounts still disputed will be reported separately.

## Idea document

Upload the six-page [Shongoti_Clear_Proposal.pdf](proposal-reference.pdf). The existing PDF is 59,973 bytes, within the 10 MB upload limit.
