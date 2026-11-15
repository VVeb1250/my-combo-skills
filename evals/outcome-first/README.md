# Outcome-first A/B/C experiment (candidate, behavioral result unverified)

A = no staged Combo; B = current main pinned to `2ec0e2033bdcc783ab021efa508eaf98d0c28786`; C = this branch. Same Codex model/effort, prompt, fixture, seeds, tools and timeout. This compares the whole Combo treatment (including routing/policy), not individual rules. No new global hooks, installation or paid runs occur automatically.

## Run on the machine with Codex

From the candidate checkout (PowerShell, keep directories outside checkout):

```powershell
git worktree add --detach ../combo-baseline 2ec0e2033bdcc783ab021efa508eaf98d0c28786
python evals/outcome-first/run.py --baseline ../combo-baseline --output ../combo-stage --work-root ../combo-work --stage-only
python evals/outcome-first/run.py --baseline ../combo-baseline --output ../combo-pilot --work-root ../combo-work --repeat 1 --allow-shared-host-policy
```

Pilot = 2 cases × 3 arms = 6 fresh sessions. Use `--case river` for three
sessions only. Repeat 3 for 18 sessions; use a NEW output directory.
Set `--model`, `--effort`, `--timeout` consistently if needed. If the CLI is not installed in the usual Windows npm location, supply `--cli <native-executable>`. Default Luna
max, 300 seconds per session. Arm order rotates across cases/repetitions.
No model calls with `--stage-only`; it checks the seeded mechanical failures
and stages the exact three treatments. Do not install the candidate globally.

Use a dedicated, matched Codex configuration (optional `--codex-home <prepared-home>`) with no global Combo routing
instructions (especially AGENTS.md or injected prompt), no extra plugins that
impose different workflows, and the same auth/model settings. The runner
disables discovered global combo* skill paths, hooks, MCP, memories and
multi-agent via existing process overrides. It cannot guarantee that other
global instructions or project ancestry are absent; inspect actual traces and
discovery. Known Combo instructions in the selected home or inherited workspace AGENTS files cause the runner to stop before live execution. A contaminated A is not a valid no-Combo result. B/C load their local source and policy; a substantive run without observed workflow-read evidence is classified inconclusive, not a model failure. The inherited harness uses danger-full-access: trusted
synthetic fixtures only, not filesystem isolation. Do not point at the real RTS
repo or give it secrets. Work directories are retained for audit, not deleted.
A/B/C results are bounded Codex evidence, not evidence for Claude or all models.

## Non-model self-test

```powershell
python -m unittest discover -s evals/outcome-first -p "test_*.py" -v
python scripts/sync-context-core.py --check
```

These exercise the independent mechanical grader with a known-pass synthetic
channel and deliberate defects, the full multi-seed acceptance (including
rejection of seed-invariant geometry), the legacy seeded failures, the label
control, staged treatment separation, locked renderer and arm order. They do not establish model behavior or visual quality.

## Cases

- **River:** 384 m synthetic patch; disconnected tributary and uniform width
  baseline. Five fixed seeds, topology, boundary exits, protected vehicle
  approach, widening, deterministic output and minimum geometric diversity.
  Independent renderer captures actual output after the session. Visual
  naturalness is deliberately NOT automatically graded. This is a 2D proxy,
  not a replacement for real RTS terrain, physical vehicle or LOS tests.
- **Label control:** exact existing trivial-label case; independent AST check
  confirms the edit and unchanged function. Inspect traces for workflow
  overhead, additional files, needless exploration and cost.

## Grade before unblinding

Open the original seeded outputs in `reference/` first, then SVGs in `blind/<case>/[random-id]/` at full view and zoom around junction.
Use identical zoom, seed and rubric. Do not open blind-key.json, raw answer,
source or named arm artifacts first. Compare to the starting generator and the
shared brief, not to an agent's claimed success. Score each dimension 0 (bad),
1 (partial), 2 (adequate), 3 (strong):
1. natural channel shape and curvature (not uniform straight strokes);
2. coherent confluence and bank transitions (not an abrupt Y/overlap);
3. meaningful variation across seeds without changing the intended structure;
4. protected approach and coherent geometry (mechanical evidence separately).

Any obvious major defect or score <2 on a required dimension = quality not
accepted. Record per-seed observations, overall verdict and why. Do not average
away an important defect. Then unblind and inspect summary.json, raw events,
final-answer.txt, acceptance.json, hashes and agent previews. Record first-pass
quality only if a real pre-refinement artifact exists in trace/previews; otherwise
unknown. Record corrections/iterations, elapsed time, usage and tool calls.
A premature-completion event is an explicit completion claim while a material
criterion is failed/unverified, not a session ending honestly incomplete.
Environmental interruptions, invalid treatments and missing evidence are
inconclusive; repeat the matched triplet rather than quietly discarding an arm.

B vs A estimates current Combo's contribution; C vs B estimates this candidate's
increment; C vs A checks net value. Prioritize quality and truthful completion,
then overhead. A small pilot does not establish superiority. For causal follow-up
use a second model under the same three conditions, not a different task.

## Real RTS follow-up (not automated here)

Freeze one actual failed revision, map seed bundle, screenshot viewpoints and
vehicle profiles; use separate clean worktrees with identical inputs and budgets.
Apply the same A/B/C treatments and compare actual render, confluence/road
junctions, vehicle mobility, LOS/cover/counterplay and generation time.
Keep technical results distinct from visual approval. No real RTS repository
or trace was supplied to this branch; do not treat the synthetic fixture as
proof of gameplay quality.
