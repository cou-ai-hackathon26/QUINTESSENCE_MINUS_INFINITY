# JR-02: Actual Groq inference

23 November 2026. Judge entry is a seeded, isolated merchant account using the same persistent HTTP APIs as normal accounts. It does not intercept file uploads or substitute canned AI answers.

Implemented: Groq strict-schema text and vision, native PDF parsing and scanned PDF rasterization, Whisper transcription, grounded merchant chat, typed proposed operations, original private source retention and actual provider receipts. A failed provider leaves missing values unknown and keeps the source downloadable. No inference output posts money. Required party/payment-account fields are checked in application code. Integer paisa output rejects strings, booleans and fractional values.

Verified against actual Groq calls through the running application:

- A newly generated invoice reference and BDT 1,763.55 were correctly extracted from text, PNG, native PDF and scanned PDF. See `groq-live-verification.json` for real request IDs, model IDs, token usage and latency.
- Synthetic Windows SAPI English speech produced a 500 BDT old-debt collection and a separate 200 BDT new credit sale via real Whisper and extraction. Source bytes and history survived round trips. See `groq-voice-verification.json`. This is not a Bangla speech-quality benchmark.
- Isolated installed Chrome exercised real image upload, real voice input, grounded chat, persisted history and 360/768/1440px layouts. Four browser checks and seven screenshots passed. See `evidence/browser-report.json`.

Offline checks are separate from genuine calls: full API suite 153 passed (including 11 focused provider contract tests), frontend suite 31 passed. Production TypeScript/Vite build passed. Test providers are explicit HTTP doubles and pytest clears local inference credentials. Non-blocking existing test warnings concern Starlette's BlockingPortal, datetime.utcnow and React act/router migration notices.

Commands from repository root:

```powershell
node scripts/run-python.js -m pytest apps/api/tests/ -q -p no:cacheprovider
pnpm.cmd test:web
pnpm.cmd build
node scripts/run-python.js scripts/verify-groq-live.py
powershell -File scripts/make-test-voice.ps1
node scripts/run-python.js scripts/verify-groq-voice.py
node scripts/check-groq-browser.mjs
```

Live scripts require the local API, configured ignored `.env`, network access and model quota. They use isolated synthetic judge tenants and make bounded paid requests. No secret or real merchant document is included in evidence. Synthetic audio/image files remain ignored under `tmp/`; the scripts recreate them locally.

Boundaries: documents are capped at 10 MB and PDFs at six pages; vision processes batches of at most three images and raster dimensions are bounded. Groq Bangla TTS and embeddings are not claimed. The optional Groq English speech-generation probe returned `model_terms_required`; the successful Whisper test uses local Windows speech instead. Agent canned findings, true semantic retrieval and reviewed posting workflows are JR-03 work, not certified by this phase. Actual payment delivery, customer messaging and production hosting require their own verified setup. No receipt is a calibrated correctness probability or permission to execute.

Provider references: https://console.groq.com/docs/models , https://console.groq.com/docs/vision , https://console.groq.com/docs/speech-to-text , https://console.groq.com/docs/structured-outputs . PDF library: PyMuPDF 1.28.2, https://pymupdf.readthedocs.io/en/latest/recipes-images.html .
