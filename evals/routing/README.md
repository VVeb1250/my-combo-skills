# Routing probe

Measures which Combo entry Claude Code selects for a natural prompt, including
prompts where no entry should load. It is the prerequisite eval for audit items
10-12 (`audit/phase1-20261021/SOURCE-AUDIT.md`): no rule about routing or
context loading can be called overhead without it.

```powershell
py scripts/run-routing-probe.py                      # all cases, both arms
py scripts/run-routing-probe.py --cases pos-review-en --arms policy
py -m unittest tests.test_routing_probe              # validates cases, no model calls
```

## Arms

| Arm | Configuration | Question it answers |
| --- | --- | --- |
| `policy` | the user's real setup, including the global CLAUDE.md routing paragraph | does the current pointer plus descriptions route correctly? |
| `description-only` | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`; skill list unchanged | do the descriptions alone trigger a route? |

Both arms use `--strict-mcp-config`, `disableAllHooks`, Read/Glob/Grep/Edit/Skill
only, a fresh copy of `evals/v2/fixtures/bug-zero`, and `--model sonnet` by default.
Each session is stopped at its first Skill call, so cost and result reflect the
routing decision only.

## Cases (`cases.json`)

`negative` (no entry should load), `positive` (one entry per direct workflow, Thai
and English), and `confusable` (pairs flagged in audit 6.3: investigate/research,
review/verify, plan/deliver, debug/investigate, lesson vs implementation, and a
cross-workflow request for the router). `acceptable` lists every route that counts
as correct; `native_overlap` (optional, with a `note`) names a non-Combo skill the owner
confirmed is a legitimate better match, so routing there is not scored as a miss; ambiguous prompts accept both sides and exist to measure confusion, not
to fail a side.

## What a result does and does not show

- One sample per case and arm. A miss is a lead for repeats, not a verdict.
- A routing miss is not a worse answer: without a skill the model may still do the
  work well. Judge outcome quality with the existing `evals/v2` fixtures before
  changing instructions.
- The environment is the author's real skill set (80 skills), which is the
  population the descriptions compete in, but it is not portable.
- A skill invoked for a negative prompt, or an unrelated skill for a positive one,
  is recorded under the name it chose.
- Raw event logs stay in `evals/routing/results/` (git-ignored); commit only the
  compact `summary.md` and `summary.json` when a run informs a decision.
