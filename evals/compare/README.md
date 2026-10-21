# Outcome comparison

Compares **task outcomes**, not routing, between instruction arms on identical
cases. It is the second gate for audit items 10-12
(`audit/phase1-20261021/SOURCE-AUDIT.md`): the routing probe
(`evals/routing/`) shows which skill loads; this shows whether the work comes
out better, worse, or just cheaper.

```powershell
py scripts/run-outcome-compare.py --host claude --arms full no-claude-md --repeats 3
py scripts/run-outcome-compare.py --host codex --arms full --repeats 3          # gpt-6-luna, effort high
py -m unittest tests.test_outcome_compare                                      # no model calls
```

## Cases

Eight cases, the same for both hosts: the six `evals/v2` cases (seeded bug,
scoped feature, review-only, plan-only, tiny edit, translation negative) plus two
added here:

- `shared-root-cause`: the prompt names the cart, but the defect is in a helper
  shared with the invoice. Hidden acceptance checks both callers, so patching only
  the named caller fails.
- `diagnose-only`: explain a root cause without touching files; the answer must name
  the falsy-`or` cause and the None-versus-zero distinction.

## Scoring (one scorer for both hosts)

Outcome passes only if independent acceptance passes (where defined), changes stay in
the allowed paths, read-only cases change nothing, and the final answer contains the
required evidence. Whether a Combo workflow was loaded is recorded as information, not
as a pass/fail condition. Cost is reported as host counters (tokens, tool calls,
seconds; Claude also reports USD). Tokens are not comparable across hosts.

## Arms

| Host | Arm | Meaning | Caveat |
| --- | --- | --- | --- |
| claude | `full` | real configuration | |
| claude | `no-claude-md` | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | removes the whole CLAUDE.md (engineering policy, preferences, routing paragraph), not only the routing paragraph |
| claude | `inline` | `--plugin-dir` plugin whose debug/deliver/plan/review entry skills contain the workflow and `context.md` text; the four originals are switched off with `skillOverrides` | changes skill names (`combo-lab:combo-*`), which changed routing in the 2026-10-22 run; needs no separate config home or credentials |
| codex | `full` | real configuration, `-m gpt-6-luna`, effort `high` | |
| codex | `home:NAME` | `--codex-home NAME=PATH` (repeatable) | a prepared CODEX_HOME; prepare two that differ only in AGENTS.md to isolate it |

Why there is no "routing paragraph only" arm: isolating one paragraph needs a separate
config home (`CLAUDE_CONFIG_DIR` / `CODEX_HOME`) whose AGENTS.md or CLAUDE.md differs,
and a separate home needs working authentication. The harness never reads, copies, or
links credential files, so it does not build that home. If you want that arm, create the
home yourself (copy the Combo skills, edit only the instruction file, authenticate it),
then pass `--codex-home`.

## Windows notes
- The work directory is created with `mkdir`, not `mkdtemp`: Python 3.12+ gives
  `mkdtemp` directories an owner-only ACL that the Codex sandbox user cannot enter, which
  made a pilot report "Access denied" and fail for reasons unrelated to the arm.
- Default work root is `D:\combo-workflow-evals`, outside the repository and user
  profile, so no ancestor AGENTS.md or CLAUDE.md applies.
- Claude sessions allow only Read/Glob/Grep/Skill for read-only cases and add
  Edit/Write and `python`/`py`/`pytest`-prefixed Bash for writable cases.

## Reading results
One run is an anecdote. Use repeats, look at pass rates first, then cost; a cost
difference with equal pass rates is a efficiency lead, not a quality claim. Raw event
logs stay in `evals/compare/results/` (git-ignored); commit only `summary.md`/`.json`
for a run that informs a decision.
