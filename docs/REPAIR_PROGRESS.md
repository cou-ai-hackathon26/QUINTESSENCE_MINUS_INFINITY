# Readiness repairs - 24 November 2026

Baseline: `c8a57ff`. User authorized fixes with existing successful workflows/UI preserved and minimal relevant testing, followed by one final integrated regression pass. Do not alter the owner's `DATABASE_SETUP.md` edit or existing merchant data.

| Phase | Scope | State |
|---|---|---|
| AJ-01 | Exact/atomic CSV, honest voice missing-data states, declared optional speech dependency, deployment recipe corrections | Complete local scope; milestone `1c00a2d` published |
| AJ-02 | Speech/privacy/auth limits, production secret/claim guards, grounding, compatible dependency maintenance and CI | Targeted checks passed; publication pending |
| AJ-03 | Final full regression, bounded real/browser smoke checks, current disclosures and handoff | Not started |

Observed AJ-01 checks: 13 backend CSV/stock tests passed; 5 voice UI tests passed. Optional missing speech no longer prevents API import. Docker daemon is unavailable; no actual image/runtime qualification is claimed. Deployment corrections require their own final execution evidence where available.

Preserve real Groq/Whisper/E5 and sequential specialist workflows, original financial goldens, owner approval and isolated Judge accounts. External payments remain owner-deferred. Large comparative benchmarks and wholesale refactoring are outside this urgent repair pass; never claim unmeasured accuracy or production readiness.

Next: implement AJ-02 security, grounding and dependency guards. Final regression is required after the last code change.
