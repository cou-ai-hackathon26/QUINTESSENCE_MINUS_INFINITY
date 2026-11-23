# Shongoti UI handoff — 23 November 2026

The owner approved merging the reviewed design into `main` and completing the remaining interface there. The authored landing design is preserved. Production React routes use the forest/paper/lime design, with distinct agent case review and a prominent voice workspace. `product-preview/` remains a historical reference; the actual application is `apps/web`.

Read `AGENTS.md`, `FULL_UI_REDESIGN_PLAN.md`, `docs/ui-redesign-progress.json`, `docs/UI_REDESIGN_PROGRESS.md` and the UIR checkpoint receipts before continuing. Original financial golden contracts remain authoritative. Do not restart or copy an old application. Preserve the owner's unrelated `docs/DATABASE_SETUP.md` changes.

## Review the product

Open `http://127.0.0.1:5173/` while the local web/API services run. Sign in or use the clearly labeled one-click judge workspace. Judge state is synthetic and in memory: a reload/reset starts its fixture state again. A new real account starts without these fixtures. Registration, password sign-in and HttpOnly cookie sessions use actual backend endpoints; phone verification and password recovery are unavailable.

Recommended review: Today → supplier case → inclusion clarification → recorded agent replay → approval queue → AI & Voice chat → Buying → Receiving → Cash planning. In the planner, set assumptions and select Compare to obtain the two paths; the empty initial chart is deliberate until the first calculation. The voice sample button is explicitly synthetic, never a transcript of the user's recording.

| Route | Purpose |
|---|---|
| `/`, `/login`, `/register`, `/demo`, `/onboarding` | Approved landing, authentication, judge entry and balanced opening setup |
| `/app` | Work queue, agent responsibilities, actual/fixture account mix and cashflow chart |
| `/app/cases`, `/app/cases/:id`, `/app/agents/:id` | Evidence-first reconciliation, support/blockers, recorded task/event receipts and deliberate replay |
| `/app/copilot`, `/app/evidence`, `/app/evidence/:id`, `/app/actions` | Text/audio review, source search/intake/corrections/private original download and owner approval |
| `/app/sales`, `/app/people`, `/app/money` | Sales vs collections, people/invoice links, account-specific manual accounting records |
| `/app/buying`, `/app/receiving`, `/app/stock`, `/app/demand` | Quotes, usable delivery counts, credit recovery, inventory/CSV review and unmet demand |
| `/app/planner`, `/app/reports` | Exact seven-day scenarios, saved assumptions/commitments, cash/revenue/dues and unsupported-profit suppression |
| `/app/inbox`, `/app/operations` | Alert states, user-triggered voice brief, reservation/pick, containers, handovers and scoped order changes |
| `/app/help`, `/app/connections`, `/app/settings`, `/app/scenarios` | Document/reference organizer, actual capability states, browser-local preferences and judge guide |
| `/pay/:token` | Scoped public invoice and dispute note; no merchant navigation or credentials |

## Truthful capability boundaries

- Agent orchestration currently returns recorded history synchronously. Animated replay is explicitly labeled; it does not establish live concurrent model agents. Public receipts are ordered and deduplicated. Private model reasoning is not displayed.
- MediaRecorder, microphone permission, actual analyser waveform, stop/review audio, upload, session history and typed chat are implemented. Browser QA uses a fake microphone device to verify capture, not to certify inference. Real STT requires a configured provider; unconfigured calls fail with 503 and retain the recording. Bangla speech playback needs an installed matching voice and always requires a tap.
- Canonical case support follows critical blockers and null/stale handling. Legacy chat/offer model scores are withheld where evidence-policy provenance is not established. No score is a correctness probability or execution permission.
- Retrieval currently includes a deterministic lexical-vector boundary; learned dense embedding quality and real RAG evaluations are not certified by these UI checks.
- Approval records review. Generic execution, gateway initiation and callbacks fail closed because no verified execution/validation adapter exists. A valid-looking client callback cannot post money. Manual ledger records remain separate from actual external transfers.
- Business Help is a document/reference organizer. Seeded legal text, rates, thresholds and dates are not certified as current or applicable. Verify with the relevant authority.
- Merchant mutations still lack a universal server idempotency contract. UI prevents concurrent confirm submissions; uncertain network outcomes require reconciliation before retry. Reservations are operational notes, not guaranteed atomic stock allocations. Container deposit references do not post cash automatically.
- No real merchant research, user adoption/savings study, deployed runtime, full screen-reader audit or measured production Core Web Vitals is claimed.

## Reproduce verification

From the repository, run `node scripts/verify-ui-redesign.mjs`. This runs all API tests with an in-memory fallback database and disabled provider keys, all frontend tests, then the production build. Raw sanitized logs, exit codes and source hashes are in `docs/evidence/ui-redesign/UIR-09/`.

The UI phase browser scripts are `scripts/check-{core,voice,commerce,inventory,planning,operations,support,final}-browser.mjs`. They require the local web/API and installed Chrome; each uses its own profile under ignored `tmp/`. They do not attach to a user's existing browser. Final route checks cover 20 workspaces at 360/390/768/1024/1440px. Screenshots and an actual frame-capture replay player are under `docs/evidence/ui-redesign/UIR-09/evidence/`. This is targeted browser/keyboard coverage, not blanket WCAG certification.

Use an isolated database when running a preview for validation, for example `DATABASE_URL=sqlite:///./apps/api/data/ui-design.db`; migrate it through revision 017 first. Use the existing `node scripts/run-python.js` launcher and `pnpm.cmd` on this Windows workspace. Never migrate/reset an owner's database merely to run UI checks. If a watcher claims reload but `/openapi.json` lacks current endpoints, restart only the owned preview process and verify the schema before testing.

## Next engineering work

Preserve the reviewed UI and assess it with the owner. Further backend capability work should have its own scoped contract: real provider receipts and evaluation; evidence-driven supplier acceptance; learned retrieval measurements; live agent transport if needed; transaction idempotency/concurrency; verified payment dispatch/validation; sale-time cost history; and consented merchant research. Do not turn an unavailable badge into a live badge from code inspection or credentials alone.

After every verified phase, commit, push normally, verify the exact remote tip, publish a receipt and verify that receipt commit. `scripts/ui-checkpoint.mjs` enforces explicit staging for UIR phases; never stage unrelated database notes or `.env` files.
