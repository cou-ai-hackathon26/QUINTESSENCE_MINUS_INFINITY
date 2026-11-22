**Mandatory GitHub checkpoint after every verified phase**

The user explicitly requires a local commit and a GitHub push for each completed phase, including the initial Phase 00 handoff. Standing authorization is limited to normal phase publication to `https://github.com/sakibul-shovon/Shongoti.git`. It does not authorize force-push, history rewriting, repository visibility changes, deployment, customer messaging or financial execution.

**Before implementation or resuming**

Read the trackers but independently inspect source/tests and actual Git state. Fetch the relevant remote refs when possible. Identify the current intended branch, whether it has a commit, whether local/remote histories diverge, and which verified phases lack publication. Do not discard unrelated working-tree changes or reset to a remote branch. Repair a missing earlier phase checkpoint before starting the next phase.

**Close each phase in this order**

1. Pass the phase acceptance tests and save actual sanitized evidence. Finish task records. Keep the phase `in_progress` while publication is pending.
2. Review the intended diff, untracked files and secret/private-data exclusions. Stage only the intended phase changes and required evidence/trackers.
3. Create a milestone commit such as `feat(phase-02): implement exact financial domain`, with the commit-body footer `Shongoti-Phase: 02`. Documentation phases may use `docs(...)`. An initial empty repository uses the existing intended branch; inspect rather than assuming a remote branch exists.
4. Push normally to the intended branch on `origin`. For a new branch, establish upstream explicitly. Never force-push or rewrite history to bypass a rejected push.
5. Verify the remote branch contains the milestone commit using an actual remote ref/fetch and ancestry check. Record the observed remote branch and milestone SHA only after this succeeds.
6. Write `docs/evidence/phase-XX/git-checkpoint.json` and update the phase's `git_checkpoint` in `docs/progress.json` plus the human tracker. Mark the phase complete only when implementation/tests and milestone publication are actually verified.
7. Commit the small tracker/receipt update, for example `docs(phase-02): record verified GitHub checkpoint`, with footer `Shongoti-Checkpoint-Receipt: 02`, and push it. Verify the final local branch tip is present on the remote before advancing.

The receipt refers to the milestone SHA, not its own commit SHA. Do not create an endless series of commits trying to record a file's containing commit hash inside itself. Later audits verify that the receipt commit is published using actual Git state.

**Receipt fields**

Record `phase_id`, `status`, `remote`, `branch`, `milestone_sha`, `verified_remote_tip_at_milestone`, `verified_at_utc`, and a summary of the observed verification. No fabricated values. The initial receipt-push observation can be reported in session output and verified from history on resume; do not invent a self-referential hash field.

**Failure behavior**

If a commit/push/verification fails, retain local work and evidence, record the exact error and `git_checkpoint.status = blocked`, and leave phase completion unclaimed. Resolve normal fetch/merge/conflicts carefully while preserving others' work. Request missing credentials or protected-branch decisions only when truly necessary; routine pushes already have user authorization. Never weaken tests or change provider/repository settings to manufacture completion.

A progress checkbox alone is insufficient. Completion means: **required work verified + milestone published + checkpoint receipt published**. The next phase must not begin until this gate is satisfied.
