# Outcome comparison run 1 (2026-10-21)

`scripts/run-outcome-compare.py`, 8 cases, 3 repeats per cell. Claude `sonnet`
(claude-sonnet-5): arms `full` vs `no-claude-md` (48 sessions, $10.67 reported, not an
invoice, and a large share of the usage limit). Codex `gpt-6-luna`, effort high, arm `full`
only (24 sessions). Raw logs stay git-ignored.

## Outcome
| host / arm | pass | workflow loaded | mean tokens | mean tool calls | reported USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| claude / full | 23/24 | 17 | 327,877 | 9 | 5.69 |
| claude / no-claude-md | 24/24 | 7 | 250,134 | 8 | 4.98 |
| codex / full | 24/24 | 18 | 137,499 | 12 | - |

- **No outcome difference.** The suite is at its ceiling. The single Claude miss
  (`plan-adapters`, full, rep 2) is a lexical-scorer artifact: the answer is a valid
  plan that never uses the words "plan"/"proposed" required by the `planning intent`
  term group.
- **Scorer fix during the run:** the claim-of-implementation check flagged Thai
  "ไม่ได้แก้ไฟล์" ("did not edit files") as a claim; five Codex results were false
  failures. The check is now negation-aware and the stored records were rescored with no
  model calls (`--rescore`). No file changed in any of those runs.

## Cost [O]
- Without CLAUDE.md, Claude loaded a Combo workflow in 7/24 runs vs 17/24, and used
  about 24% fewer tokens (250k vs 328k) and 12% less reported cost. Largest cases:
  `bug-zero` 657k -> 441k tokens, 17.7 -> 12.7 tool calls, identical pass rate.
- Both arms solved the `shared-root-cause` trap 3/3, including the arm with no
  engineering policy at all.
- Codex loaded a workflow in all 18 runs of the six workflow cases and in neither
  negative case (translation, tiny label), the intended behavior.

## What it supports and does not
- Supports: on small, well-specified tasks, loading Combo workflows added cost and did
  not change measured outcomes. Item 10 (make the context read conditional) is consistent
  with this; it does not prove the read is wasted.
- Does not support removing the routing paragraph (item 11): no-claude-md also drops the
  whole engineering policy and preferences, the tasks are tiny, and every arm passes, so
  the suite cannot show whether Combo helps on harder work.
- Codex has no no-routing arm: a separate `CODEX_HOME` needs auth, which the harness
  never copies and the permission classifier blocked. The user can prepare homes and pass
  `--codex-home NAME=PATH`.
- n=3 per cell, one model per host, one author's environment.

## Next, if wanted (cost-conscious)
Design 2-3 harder cases where a workflow could plausibly matter (ambiguous requirement,
multi-file contract change, test-gap trap) and check them offline first; then run only
`full` vs `no-claude-md` with 3 repeats (about 18 Claude sessions).
