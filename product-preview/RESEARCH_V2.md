# Research behind the revised workbench

Checked23November2026. This is a design decision record, not a competitive benchmark or a claim of matching these products' capabilities. Existing approved Shongoti landing identity is retained.

The initial preview placed a large balance panel and decorative role sequence above ordinary task detail. Feedback correctly identified that it did not make the agent's work sufficiently useful or visible. The revision uses business exceptions and reviewable outcomes as its organizing structure.

## Product references

| Official source | Finding used | Shongoti change |
|---|---|---|
| [QuickBooks Business Feed](https://quickbooks.intuit.com/global/resources/product-update/quickbooks-business-feed/) | Agent work needing review/action appears in a central feed; an empty feed can be legitimate. | Prioritized work queue; no permanent fabricated stream to make AI look busy. |
| [Ramp Accounting Agent: daily use](https://support.ramp.com/ramp-accounting-agent-enablement-daily-use-admin-guide/) | Suggested actions, grouped review and distinctions between AI coding and human/rule values. | Source-linked proposals and separate unknown/review/blocked states in actual task rows. We do not copy Ramp's automatic posting policy. |
| [Digits: how AI works](https://help.digits.com/business-agentic-general-ledger/digits-ai) | Places AI within ledger, checklist, reconciliation, document capture and questions; uncertain work is surfaced for attention. | Evidence review beside source document, with contextual agent contribution. No claim of implementing Digits' learning/autonomy. |
| [Pennylane supplier invoices](https://data-sharing.pennylane.com/docs/en/pennylane/models/supplier_invoices.html) | OCR-extracted invoices can lack data or contain errors before user validation. | Source extraction, established facts and owner review remain separate. A document-looking panel is explicitly synthetic, not proof OCR ran. |

Official product documentation supports these workflow principles. Some documentation contains product images; no asset/composition was copied into Shongoti. Gallery awards and visual novelty alone do not establish financial software quality. Real merchants have not tested this design yet.

## Chosen interface structure

- Compact navigation, small financial summary and a queue of specific business decisions.
- Contextual agent panel visible alongside that queue, with per-task source/receipt references and a next needed answer.
- Invoice/source canvas, established/unknown findings and owner review arranged together, rather than separate ornamental agent avatars.
- Procurement table with selectable quotes and an adjacent decision panel; uncertain bonus excluded from normalized totals.
- A scenario lens with explicit assumptions and conditional funds; no promise added to actual balance.
- Distinct sign-in/registration and judge entry; seeded examples do not become a new customer's financial data.

These are Shongoti design recommendations, not usability findings. The owner is reviewing four core screens before approving rollout. Motion explains a state change and can be reduced/paused; it is not evidence of intelligence.

## Implementation references

- [Chrome headless](https://developer.chrome.com/docs/automation-and-testing/headless), [DevTools Page](https://chromedevtools.github.io/devtools-protocol/tot/Page/), [Emulation](https://chromedevtools.github.io/devtools-protocol/tot/Emulation/): real rendered checks in an isolated local test profile.
- [Node crypto](https://nodejs.org/api/crypto.html), [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): salted scrypt for local account verification; chosen parameters are one listed CPU/memory trade-off.
- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): server-side session material and cookie flags. Loopback HTTP preview is not deployed TLS or production identity readiness.
- [W3C status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html), [pause/stop/hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html): user-control and meaningful status, with no constant assertive announcements.

The local prototype has genuine server-verified account/session behavior and deterministic exact-money interactions. Specialist activity and Copilot remain explicitly predefined examples. A production “AI-powered” claim still requires wiring and verifying real inference/retrieval/tool receipts in the main application.
