# Pilot P0 results (arm A only), 2026-10-22

Pre-registered in [PILOT-PRE-REGISTRATION.md](PILOT-PRE-REGISTRATION.md); owner approved smoke + 3 baseline sessions with the mb ingestion side effect.
Runner and scorer: `pilot/pilot.py` (offline-tested, `pilot/test_pilot.py`); per-run scores: `pilot/results/*.json` (counts only; rollouts stay in the scratchpad).
Setup: `codex exec`, `gpt-6-luna`, effort high, workspace-write, owner's hooks on (context-mode, mb-recall, nah), MCP servers disabled, fresh fixture dir per run.

## What ran
6 Codex sessions, about a minute each, ~1% of the plan limit each: smoke1 (limit 65,000: no compaction, 12 calls), smoke2 (29,800: compaction after call 4,
i.e. mid-step 1), smoke3 (31,200: two compactions, the second mid-step 2), then base1-3 at 31,200. Three smokes were calibration of the forced limit
(a deviation from "1 smoke": the trigger fires ~1.1-1.9K tokens below the configured limit and the fixture context only spans 26K-31K).

| Run | Compactions (after call #) | Cut position | Accepted | Step-1 files edited after cut | Settings.json edited |
| --- | --- | --- | --- | ---: | ---: |
| smoke2 | 4 | mid-step 1 | yes | 1 (the step-1 fix itself) | 0 |
| smoke3 | 3, 11 | **mid-step 2** (step 2 verified at 13) | yes | 0 | 0 |
| base1 | 6 | **mid-step 2** (edit at 6, verified at 6+) | yes | 0 | 0 |
| base2 | 8 | step 3 | yes | 0 (1 benign test re-run) | 0 |
| base3 | 4, 5 | mid-step 1 | yes | 1 (the step-1 fix itself) | 0 |

All 5 compacting runs: hidden tests unchanged, all three modules pass, the config decision correct (defaults.toml, never settings.json), 10-17 calls.

## Reading
- **Stop rule met on thin evidence: the failure is not demonstrated in this fixture.** No verified step was redone and nothing was contradicted after a cut. Arms B (continuity rule) and
  C (custom compact prompt) were therefore **not run**; nothing to build on this evidence.
- **Only one of the three planted states was actually tested.** "Verified step not redone": tested at the two mid-step-2 cuts (smoke3, base1) - 0 step-1 edits, 0 step-1 test re-runs.
  "Decision survives the cut": the config source was first read *after* the cut in smoke3 and base1, so nothing could flip there; it was read *before* the cut in base2 and base3 and the
  correct file (defaults.toml, never settings.json) was edited after, which is weak evidence from cuts that were not mid-step 2. "Failed attempt not retried": never occurred (0 of 5 runs
  edited report.py/fmt.py and then saw a test fail before a cut; the model read fmt.py first), so it is untested, not passed.
- **Why this is a weak test [I]:** a 10-17 call task with unit tests gives the agent an external check after every cut, so recovery is nearly free; compaction here drops
  ~4K of a 30K context. The user's observed failures were long, tool-heavy, taste-driven work (Blender hair, no tests) where assistant-side state is the only record.
- Cut placement is not controllable at this scale (2 of 4 runs at the calibrated limit landed mid-step 2), so a bigger design needs a fixture whose context spans well above the base prompt.
- Contamination check: Codex native memory (`MEMORY.md`) has no mention of the fixture files or pilot directories, and no base run's injected messages name another pilot directory; runs are
  treated as independent.

## Deviations, stated after seeing data
1. Three calibration smokes instead of one (the trigger fires ~1.1-1.9K tokens below the configured limit and the context spans only 26K-31K).
2. The stop rule was applied on **n=2 valid mid-step-2 cuts**, one of them a calibration run (smoke3) and one baseline (base1); the pre-registration asked for 3 baseline sessions with such a cut.
3. Scorer changes made after the runs: decoding JSON-escaped test output (a bug fix: it hid step-1 verification in base1) and choosing the first compaction between step-1 and step-2 verification as the analysed cut
   instead of the first compaction (an analysis choice). The `smoke1` record had `acceptance_pass=false` from a harness bug (`python -I`); re-run and corrected, with a note in the file.

## Next-step options (owner decides)
1. **Stop here** (matches the pre-registered rule): keep the existing `project-knowledge.md` checkpoint rule; take the audit's other findings (Bash output volume, advisor timing) forward.
2. **Read the real case**: tell me the Codex session/date; reading its rollout around the cut is cheaper and closer to the failure than a synthetic fixture.
3. **Redesign the fixture** to be long and tool-heavy without tests (a generate-and-review task with decisions only in assistant text) and re-run arm A first; larger, and the same ceiling risk applies.

Side effects: the 6 rollouts are eligible for Memory Base ingestion under `D:\combo-workflow-evals\pilot-*` scopes (not checked whether the worker has run); those directories still exist and can be deleted.
