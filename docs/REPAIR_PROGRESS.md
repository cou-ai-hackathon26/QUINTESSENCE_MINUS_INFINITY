# Readiness repairs - 24 November 2026

Baseline: `c8a57ff`. User authorized fixes with existing successful workflows/UI preserved and minimal relevant testing, followed by one final integrated regression pass. Do not alter the owner's `DATABASE_SETUP.md` edit or existing merchant data.

| Phase | Scope | State |
|---|---|---|
| AJ-01 | Exact/atomic CSV, honest voice missing-data states, declared optional speech dependency, deployment recipe corrections | Complete local scope; milestone `1c00a2d` published |
| AJ-02 | Speech/privacy/auth limits, production secret/claim guards, grounding, compatible dependency maintenance and CI | Complete; milestone `4038f8b` published |
| AJ-03 | Final full regression, bounded real/browser smoke checks, current disclosures and handoff | All execution gates passed; evidence publication pending |

Observed AJ-01 checks: 13 backend CSV/stock tests passed; 5 voice UI tests passed. Optional missing speech no longer prevents API import. Docker daemon is unavailable; no actual image/runtime qualification is claimed. Deployment corrections require their own final execution evidence where available.

Preserve real Groq/Whisper/E5 and sequential specialist workflows, original financial goldens, owner approval and isolated Judge accounts. External payments remain owner-deferred. Large comparative benchmarks and wholesale refactoring are outside this urgent repair pass; never claim unmeasured accuracy or production readiness.

Final execution: 188 backend tests, 39 frontend tests, build and secret scan passed. Actual OCR/native PDF/scanned PDF/chat, three model specialist calls, Whisper compound proposals, English/Bangla online speech, ordinary login and browser checks passed. The first live specialist attempt hit provider 429; the bounded retry passed. The corrected remote CI run is green at `ba10a33`.

Next: publish the AJ-03 evidence milestone and receipt. No additional source changes are required by this repair scope. Docker runtime/production deployment and the existing financial/product follow-ups remain explicitly outside the verified local scope; see READINESS_HANDOFF.md.
