# Phase 05 supplier settlement extension — local verification

Date: 24 November 2026  
Base revision: `4a91bfe` plus the documented working tree  
Scope: merchant-side, reviewed lump-sum supplier settlements; no external payment execution

## Implemented behavior

- A dedicated `/app/settlements` workspace is linked from the sidebar, quick-add menu and supplier rows in People.
- The merchant first chooses one registered supplier. Extracted names can suggest candidates but cannot change that supplier or auto-merge records.
- A reviewed alias may be remembered only after explicit human confirmation. An exact match to another registered supplier (for example, `Karim` versus `Karim Traders`) is rejected.
- Multiple original images/PDFs/messages can be uploaded. Two files are processed concurrently, while each file exposes request-driven upload, extraction and identity-check states.
- The original document and extracted party, invoice and amount remain visible together. Cropped/unreadable receipt amounts and invoice fields require correction or explicit source exclusion.
- Contradictory reviewed supplier messages remain a material blocker; Shongoti does not choose a winning amount. A reviewer must correct or exclude one source.
- One payment can be proposed oldest-due-first or manually split across several invoices. Integer-paisa capacity checks, invoice versions and settlement versions prevent over-allocation and stale recording.
- Final recording is an internal, balanced accounts-payable/source-account journal entry with idempotent allocation. It does not call or claim an external payment provider.

## Actual checks

| Command / boundary | Result |
|---|---|
| `pytest apps/api/tests/test_supplier_settlements.py -q` | 6 passed |
| `pnpm --filter @shongoti/web test` | 39 passed |
| `pnpm typecheck` | passed |
| `pnpm build` | passed; production bundle generated |
| clean SQLite `alembic upgrade head` and `alembic current` | migration `019_supplier_settlements` reached head |
| full `pytest apps/api/tests -q` | 193 passed; 1 pre-existing environment failure because local PostgreSQL database `shongoti` does not exist |
| browser layout check | not run: the CUA browser access host reported unavailable |

No live provider inference or external payment call was made in this verification. Existing AJ-03 evidence remains the current provider verification; it is not re-labelled as a test of this new UI journey.

Follow-up on working tree based on `dd36a66`, from the repository root. The backend command `node scripts/run-python.js -m pytest apps/api/tests -q -k 'not test_postgresql_live_connection_and_schema'` exited 0 with 193 passed and one deselected. It covers a posted two-invoice split and recovery after excluding a contradictory source. `pnpm test:web` exited 0 with 39 passing tests and `pnpm build` exited 0. GitHub Verify application run 45328698706 succeeded for `dd36a66` with its PostgreSQL 16 service and SQLite migrations. This CI job does not apply migration 019 on PostgreSQL or exercise the responsive settlement journey.

## Remaining gates

From repository root at `e8cb9f4` plus the migration compatibility changes, `pnpm db:migrate` initially exited 1 on PostgreSQL 18.1 at migration 007 because a boolean column used an integer default. Migrations 007, 008 and 016 now express the same defaults with SQLAlchemy boolean literals. On retry, `pnpm db:migrate` and `pnpm db:check` both exited 0 on the isolated PostgreSQL 18.1 test database and on a fresh SQLite database, reaching migration 019 on both. The local hardcoded PostgreSQL 16 test still requires its own environment.

P05-T04 and the full Phase 05 publication gate remain in progress. Upload/review/allocation/recording at 360/768/1440 px, including live extraction on synthetic files, still needs browser evidence. The partial implementation has a separately published receipt.
