**Integration capability and access register**

Initial state: **no real application integration has been configured or tested**. Provider documentation was researched; this does not establish credentials, quotas or sandbox/live behavior.

| Capability | Current state | Required setup | Completion evidence |
|---|---|---|---|
| Model inference | not_configured | Approved model account/key, quota and data treatment; explicit configured model/version | Genuine synthetic bill/message/audio requests, output comparison, usage and failure behavior |
| Identity / OTP | undecided | Supported session/identity provider; verified OTP sender if that method is used | Valid/invalid/expired session, recovery and tenant isolation tests |
| SSLCOMMERZ | not_configured | Sandbox merchant credentials, session, IPN and Order Validation | Real sandbox success/failure/cancel, amount/currency/merchant match and deduplication |
| Direct bKash/Nagad/bank | capability_unverified | Actual approved provider account and exact granted APIs | Documented capability plus observed authorized calls; no universal wallet access assumed |
| Google Sheets | not_configured | OAuth client, selected-file permission and mapping | Real selected-file import/export with duplicates/conflicts tested |
| Email/SMS | not_configured | Verified sender, allowed transactional use case, recipient permission and budget | Actual provider outcome and failure/delivery state mapping |
| WhatsApp | restricted_use_case_unverified | Policy eligibility and approved setup | No unrestricted debt-collection capability; verify any specific eligible notification separately |
| Hosting/private storage | undecided | Persistent DB, private files, runtime, secrets, migrations and backup plan | Actual deploy, readiness, persistence and workflow smoke tests |

Reference documents: [SSLCOMMERZ](https://developer.sslcommerz.com/), [Sheets scopes](https://developers.google.com/workspace/sheets/api/scopes), [WhatsApp policy](https://business.whatsapp.com/policy), [Gemini model documentation](https://aistudio.google.com/docs/models/gemini-3.8-flash).

For every configured connector, record its mode (`mock`, `sandbox`, `live`), exact allowed operations, account ownership, secret variable names (never values), last verified date, provider/API version and evidence. Keep disconnected/revoked/degraded UI states truthful. Gateway checkout/status is separate from reading a personal wallet balance or sending supplier funds.

A missing key is not a reason to abandon independent local development. It is also not permission to mark the real integration task complete. Use explicit adapter doubles for offline tests and a clearly unavailable state for unconfigured live operations.
