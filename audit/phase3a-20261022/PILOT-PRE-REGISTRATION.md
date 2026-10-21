# Pilot P0: recovery after a forced mid-step compaction (Codex), pre-registration

Written before any session runs. Status: **arm A run (smoke + 3 baselines) on 2026-10-22 with the owner's OK; stop rule met, arms B and C not run.** Results and post-hoc deviations: [PILOT-RESULTS.md](PILOT-RESULTS.md).

## Question
After a compaction in the middle of a step, does the agent resume correctly, and does a continuity rule or a custom compaction prompt change that?
The audit found no confirmed rework in 32 real compactions, so the first job is to show the failure exists at all.

## Fixture (fresh directory per run, built by script, hidden acceptance tests)
Small repo, three ordered steps. The planted state is assistant-derived, because Codex retains recent user messages:
1. a step verified early whose files must not be touched again (its acceptance check must still pass at the end);
2. a tempting fix that fails for a reason found only by running it (must not be retried after the cut);
3. a decision reached by investigating the code (which of two config sources is authoritative), needed after the cut.
Compaction is forced mid-step-2 with `-c model_auto_compact_token_limit=N` (key confirmed in Codex docs; N calibrated in the smoke run;
tool output is padded with a large log read to cross it).

## Arms
- **A baseline:** current installed Combo and the owner's hooks as they are.
- **B continuity rule:** A plus a run-local skill/AGENTS text (not a repo edit): for multi-step work keep one status file, update it at start of a step,
  on a decision, on a verified result, on a blocker, and when a long step has progress; separate observed evidence from claims; read it after a cut and
  check it against files and `git diff`; the user's latest message wins.
- **C host-native:** A plus `-c experimental_compact_prompt_file=<prompt asking the summary to keep objective, decisions, verified state, failed attempts, next action>`.

## Metrics (scored by script from the rollout and the workspace)
resumed correctly (hidden acceptance passes); verified step touched or re-run after the cut; failed approach retried; decision flipped;
read-only calls before the first edit after the cut; state-file reads; cached/uncached input and output tokens to finish; ChatGPT plan `used_percent` before and after.

## Order and stop rules
1. **1 smoke session** (arm A): confirm a `compacted` event appears mid-step-2 and the metrics can be scored. Fix the fixture, not the metric.
2. **3 baseline sessions.** If all 3 recover with 0 redo, 0 retry, 0 flip, the failure is **not demonstrated**: report it and build nothing.
3. Otherwise **3 sessions each of B and C** (6 more). Maximum 10 sessions.
4. B or C counts as better only if it removes a failure seen in A without raising tokens-to-finish by more than 25%; with n=3 this is a signal, not a proof.

## Confounds, stated up front
`context-mode` PreCompact and `mb-recall` run in every arm; pilot rollouts will be ingested into `~/.memorybase/mb.db` under their own fixture scope (unique
directory per run). Model, effort and Codex version are pinned in the smoke run and recorded. No Combo file is edited; the winner, if any, becomes the next change.

## Decisions needed from the owner
1. OK to run the smoke plus 3 baseline sessions (4), with the mb ingestion side effect?
2. Which session or date did the failure you saw happen in? If it is one of the 10 compacting rollouts it can be read directly, which is cheaper than the pilot.
