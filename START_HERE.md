**Start or resume Shongoti in Antigravity**

Open **this `Shongoti` folder**, not its parent archive/research workspace. Use the same prompt for the first session and later sessions. Determine current progress from repository evidence, not an assumed starting phase.

Paste this prompt:

```text
Build and continue Shongoti from its actual current state. Work in this
repository and follow AGENTS.md and plan.md.

First read AGENTS.md, the execution contract and phase gates in plan.md,
docs/PROGRESS.md, docs/progress.json, docs/GIT_CHECKPOINTS.md,
docs/VALIDATION.md, docs/DECISIONS.md, docs/INTEGRATIONS.md and
docs/KNOWN_ISSUES.md.

Audit before editing: verify origin; inspect the working tree, available Git
history and branch state; fetch remote refs when accessible; inspect actual
source, migrations, tests and relevant evidence. Handle an empty repository
without treating it as a reason to restart.

Determine the last genuinely verified and published phase, any partial or
blocked work, and the next exact unblocked task. Cross-check tracker claims
against behavior, test results, evidence revisions and remote checkpoints.
Do not trust checkboxes, filenames, commit messages or static previews alone.
Run targeted verification when evidence is missing or stale; fix the tracker
with an explanation. Preserve existing work and do not rebuild verified phases.

Briefly report what is complete, what remains and where you will resume.
Then immediately implement the next task. Keep the original supplier-bill
reconciliation, connected merchant workflow, exact money rules and future
spending-impact scenarios. Never present mocks, synthetic results or missing
providers as working live services.

For EVERY phase: implement its tasks, run its required tests/build checks,
fix failures, and save sanitized actual evidence. Review the intended diff
for secrets and unrelated changes. Create a phase milestone commit with
the footer "Shongoti-Phase: XX", push it to the intended branch on origin,
and verify the remote checkpoint. Record the milestone SHA and observed
publication in the trackers/receipt, commit and push that receipt update,
and verify the final local tip is published. Never claim a tested but
unpublished phase is complete. Do not start the next phase until this gate
passes. The user already authorizes these phase commits and pushes to
sakibul-shovon/Shongoti; do not ask again for routine checkpoint permission.

If access, credentials or a push is blocked, preserve the work, record the
exact blocker and failed/unrun gate, and continue only independent tasks
whose prerequisites permit it. No force-push, fake success, weakened golden
tests, changed repository visibility or unauthorized deployment/actions.

Keep both progress trackers, integration state, known issues and checkpoint
records accurate. Continue through unblocked phases rather than stopping
after one phase or a proposed plan. At every session end leave exact task
IDs, actual test outcomes, Git publication state and the next resume action.
```

The initial handoff was documentation-only. Inspect the current state rather than hardcoding Phase 01 as the next phase. If a verified earlier phase lacks its required GitHub checkpoint, publish that checkpoint before beginning the next phase.

Useful files:

- `plan.md`: full product/domain context, architecture, ordered phases and gates.
- `docs/PROGRESS.md` and `docs/progress.json`: human/machine progress and checkpoint state.
- `docs/GIT_CHECKPOINTS.md`: mandatory commit/push/receipt protocol.
- `docs/VALIDATION.md`: evidence and verification requirements.
- `docs/DECISIONS.md`, `docs/INTEGRATIONS.md`, `docs/KNOWN_ISSUES.md`: decisions and observed gaps.
- `tests/fixtures/contracts/`: independent synthetic financial expectations.
- `docs/context/` and `docs/reference-ui/`: supporting references, not proof of implemented behavior.

Complete available local work before requesting unavailable external setup. A missing key or approval remains a real blocked gate; it cannot be replaced with a passing mock claim.
