# A/B evaluation metrics

Generated `2026-09-09T12:02:36.591321Z` from the existing real Codex artifacts.

Cases are defined by `evals/ab/cases.json`. The report reads `probe-final` for `bug-zero` and `matched-rest` for the other cases. Re-run `python scripts/summarize-ab.py` after more arm result files appear.

## Coverage

| Measure | Value |
| --- | ---: |
| Expected cases | 10 |
| Expected arms | 20 |
| Result artifacts read | 20 |
| Pending or partial arms | 0 |
| Classifications | {"environmental": 3, "passed": 15, "task": 2} |

## Discovery inventories

| Run | Arm | Repo-scoped combo entries | Global user combo disabled | Total entries |
| --- | --- | ---: | --- | ---: |
| probe-final | A | 1 | true | 110 |
| probe-final | B | 13 | true | 122 |
| matched-rest | A | 1 | true | 110 |
| matched-rest | B | 13 | true | 122 |

The selected discovery comparison is `probe-final`. Expected repo-scoped combo counts A=1 and B=13 verified: `true`. Global `combo` is disabled in both arms: `true`. Unrelated inventory preserved by the comparison: `true`.

Repo entries A: `combo`.
Repo entries B: `combo, combo-business, combo-content, combo-debug, combo-deliver, combo-investigate, combo-learning, combo-media, combo-plan, combo-productivity, combo-research, combo-review, combo-verify`.

## Arm-level results

Token columns retain reported input, cached input, derived uncached input, and output separately.

| Run | Case | Arm | State | Classification | Completion quality | Acceptance | Wall seconds | Input | Cached | Uncached | Output | Calls | Instructions |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| probe-final | bug-zero | A | completed-artifact | passed | recorded | before failed; after passed | 158.505 | 741,209 | 698,112 | 43,097 | 4,929 | 13 | 6 |
| probe-final | bug-zero | B | completed-artifact | passed | recorded | before failed; after passed | 122.479 | 277,836 | 228,608 | 49,228 | 3,975 | 12 | 4 |
| matched-rest | inventory-feature | A | completed-artifact | passed | recorded | before failed; after passed | 187.039 | 400,868 | 357,888 | 42,980 | 7,236 | 25 | 7 |
| matched-rest | inventory-feature | B | completed-artifact | passed | recorded | before failed; after passed | 234.500 | 595,940 | 556,800 | 39,140 | 9,016 | 18 | 8 |
| matched-rest | security-review | A | completed-artifact | passed | recorded | not configured | 95.503 | 155,092 | 134,400 | 20,692 | 3,521 | 14 | 5 |
| matched-rest | security-review | B | completed-artifact | task | recorded | not configured | 108.140 | 196,558 | 168,960 | 27,598 | 4,081 | 14 | 5 |
| matched-rest | plan-adapters | A | completed-artifact | environmental | deadline-incomplete | not configured | 247.749 |  |  |  |  | 13 | 4 |
| matched-rest | plan-adapters | B | completed-artifact | environmental | deadline-incomplete | not configured | 247.717 |  |  |  |  | 4 | 6 |
| matched-rest | trivial-label | A | completed-artifact | passed | recorded | not configured | 27.963 | 55,766 | 42,240 | 13,526 | 438 | 2 | 0 |
| matched-rest | trivial-label | B | completed-artifact | passed | recorded | not configured | 51.443 | 123,584 | 85,760 | 37,824 | 1,274 | 3 | 2 |
| matched-rest | translation-negative | A | completed-artifact | passed | recorded | not configured | 17.463 | 18,065 | 8,960 | 9,105 | 98 | 0 | 0 |
| matched-rest | translation-negative | B | completed-artifact | passed | recorded | not configured | 16.695 | 18,400 | 0 | 18,400 | 98 | 0 | 0 |
| matched-rest | thai-diagnosis | A | completed-artifact | passed | recorded | not configured | 130.848 | 188,579 | 141,568 | 47,011 | 5,400 | 6 | 4 |
| matched-rest | thai-diagnosis | B | completed-artifact | passed | recorded | not configured | 138.173 | 288,509 | 264,192 | 24,317 | 4,719 | 13 | 5 |
| matched-rest | thai-delivery | A | completed-artifact | environmental | deadline-incomplete | before failed; after passed | 248.375 |  |  |  |  | 37 | 8 |
| matched-rest | thai-delivery | B | completed-artifact | passed | recorded | before failed; after passed | 203.491 | 479,508 | 437,248 | 42,260 | 7,363 | 12 | 9 |
| matched-rest | content-repurpose | A | completed-artifact | passed | recorded | not configured | 100.542 | 128,717 | 109,056 | 19,661 | 3,774 | 9 | 6 |
| matched-rest | content-repurpose | B | completed-artifact | task | recorded | not configured | 91.686 | 183,472 | 163,584 | 19,888 | 2,948 | 7 | 5 |
| matched-rest | learning-lesson | A | completed-artifact | passed | recorded | not configured | 80.125 | 107,883 | 89,856 | 18,027 | 2,792 | 6 | 6 |
| matched-rest | learning-lesson | B | completed-artifact | passed | recorded | not configured | 54.673 | 56,554 | 36,352 | 20,202 | 1,458 | 2 | 2 |

## Pair view

Pair wall time is the maximum recorded arm duration, reflecting the harness pair's concurrent shape. A missing arm leaves it blank.

| Pair | Case | First arm | A classification | B classification | Pair wall seconds | Sum arm seconds |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 0 | bug-zero | A | passed | passed | 158.505 | 280.984 |
| 1 | inventory-feature | B | passed | passed | 234.500 | 421.539 |
| 2 | security-review | A | passed | task | 108.140 | 203.643 |
| 3 | plan-adapters | B | environmental | environmental | 247.749 | 495.466 |
| 4 | trivial-label | A | passed | passed | 51.443 | 79.406 |
| 5 | translation-negative | B | passed | passed | 17.463 | 34.158 |
| 6 | thai-diagnosis | A | passed | passed | 138.173 | 269.021 |
| 7 | thai-delivery | B | environmental | passed | 248.375 | 451.866 |
| 8 | content-repurpose | A | passed | task | 100.542 | 192.228 |
| 9 | learning-lesson | B | passed | passed | 80.125 | 134.798 |

## Aggregates

Completed result artifacts: `20`, with usage: `17`, missing usage: `3`. Summed fields: `{"cache_write_input_tokens": 0, "cached_input_tokens": 3523584, "input_tokens": 4016540, "output_tokens": 63120, "reasoning_output_tokens": 37624, "uncached_input_tokens": 492956}`.
Completed unique tool calls: `210`, by item type `{"command_execution": 197, "file_change": 13}`.

## Limits

- Only result.json artifacts present when this report ran are counted; absent arms remain pending or partial.
- Harness classification and failure strings are copied metadata derived from exit, timeout, answer, acceptance, and scope checks. A heuristic task flag, including write-like command detection, is not by itself proof of a real fixture write; changed_files and acceptance remain separate evidence.
- Acceptance and semantic evidence in the harness use keyword or metadata checks. They do not prove that a human would accept every answer.
- Instruction reads are inferred from successful completed command strings with a concrete skills Markdown path. Path evidence cannot prove that every command returned the intended bytes, and output is not re-read here.
- uncached_input_tokens is derived from reported input_tokens minus cached_input_tokens. Token fields are reported separately and are not converted into a total-input cost.
- Discovery verification compares inventory metadata and expected combo counts. It does not establish runtime routing quality or choose an architecture.
