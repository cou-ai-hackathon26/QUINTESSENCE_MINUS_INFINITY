**Synthetic golden financial contracts**

These JSON files define independent expected behavior for Phase 02 onward. They are not observed merchant data and not a completed test suite. All monetary integers use **paisa** (`100 paisa = BDT 1`). Case IDs and expected values must survive refactoring.

- `reconciliation.json`: original supplier ambiguity, allocation history and partial answers.
- `cash-scenarios.json`: exact seven-day baseline, spending and conditional promise examples.
- `liquidity.json`: channel-specific shortage, actual versus promised receipt, reserve and illustrative fee.
- `posting.json`: ledger semantics, duplicate processing, allocation capacity and stale approval contracts.

Convert these into executable domain/API tests rather than loading their expected outputs as production answers. Do not change expected values to fit a faulty implementation. If a contract really is inconsistent, derive the correction independently, record the decision and retain a failing regression example.

Provider fee values here are **synthetic test configuration**, not current bKash/Nagad tariff claims. Dates use a specified business timezone/offset, not the machine's current date. Statistical forecasting quality is not established by these scenarios.
