# Real merchant and judge workflow repair

23 November 2026: the owner rejected a fixture-only judge experience. Judge entry must create an isolated, seeded merchant account that uses the same persistent APIs, uploads and configured inference as any other account. Seed examples are sample records, not alternate execution. Preserve the approved interface and the financial golden contracts.

| Phase | Required result | Gate |
|---|---|---|
| JR-01 | Remove production fixture interception, persist judge examples and case inputs, fix API/UI contracts and refresh/resume | Actual HTTP uploads and mutations, reload persistence and tenant isolation; publish checkpoint and receipt |
| JR-02 | Groq OCR/vision, native/scanned PDF, Whisper audio and source-grounded chat with typed proposals and receipts | Genuine unseen synthetic image/PDF/audio/text calls; exact schema checks, usage receipts and provider failure handling; publish checkpoint |
| JR-03 | Actual streamed/polled agent work, semantic/keyword evidence retrieval, actionable reviewed proposals | Model/tool receipts, current source versions, isolation and meaningful source/missing-fact tests; no invented execution; publish checkpoint |
| JR-04 | End-to-end page workflows, provider capability setup and handoff | Browser workflows use persisted HTTP data; accounting writes are exact/idempotent; payment/messages need their own verified provider, not just a button; publish verified scope and precise remaining setup |

The supplied Groq credential is stored only in ignored local .env. Never copy it into source, tests, evidence, URLs or output. Account model access was checked against the official models endpoint. Use provider-specific configured model IDs and verify actual task calls. Groq text, vision and Whisper models do not establish an embedding or Bangla TTS API; do not invent one.

Docs checked: https://console.groq.com/docs/models , https://console.groq.com/docs/vision , https://console.groq.com/docs/speech-to-text , https://console.groq.com/docs/structured-outputs .

External model inference is authorized for this implementation and bounded synthetic verification. This does not authorize sending real customer messages, charging customers or transferring real money. Use a real provider sandbox for such integration testing and request its exact setup when needed. Do not stop independent local work while credentials are pending.
