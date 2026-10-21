# Moving the core context rules into the workflows: result, 2026-10-22

Criteria were fixed in [PRE-REGISTRATION.md](PRE-REGISTRATION.md) before the sessions ran. 12 sessions, $1.53 reported,
`claude-sonnet-5-5`, no advisor spend. Baseline: the `full` arm of the cost experiment (same cases, same model, earlier the
same day). Raw logs git-ignored; kept here: `moved-run1.summary.*`, `price_loads.moved-run1.*`.

## The change
`scripts/sync-context-core.py` copies the three invariant sections of `practices/context.md` (Own the outcome, Decision
triage, Verify against intent; about 790 tokens) into a marked block at the end of all 12 workflows, rewrites the
same-folder links so they resolve from `workflows/`, and turns "Read context once" into a pointer for the remaining
mechanics. `context.md` stays the single place to edit; `--check` and 5 tests keep the copies in step.

## Result against the criteria [O]
| Criterion (fixed beforehand) | Baseline | Moved | Met |
| --- | ---: | ---: | --- |
| Pass 12/12 | 12/12 | 11/12 | **No** (see below) |
| Workflow loaded in at least 9 of 12 | 11 | 10 | Yes |
| Cost per loaded run rises by at most $0.01 (predicted about +$0.0035) | $0.1241 | $0.1266 (+$0.0025) | Yes |
| `context.md` not read | 0 | 0 | Yes |

Other numbers: Sonnet cost per run $0.1243 to $0.1273 (+2.4%), calls 5.75 to 5.58, output 2,229 to 2,202 tokens. Per case
(baseline to moved): bug-zero $0.131 to $0.133, inventory-feature $0.143 to $0.141, plan-adapters $0.119 to $0.123,
security-review $0.104 to $0.113. One security-review run read `practices/security.md` (a conditional read; none in the
baseline).

## The one failure [O]
`plan-adapters` run 2: "answer lacks planning intent". The answer is a valid plan (it reads the three files, recommends a
`RetryingAdapter` decorator, lists three rejected alternatives, changes nothing), but the scorer's term group is the literal
words `plan`, `แผน`, `วางแผน`, `proposed` and this answer used none of them. The other 5 plan answers across both runs all
contain "plan". The same scorer message failed one run in Phase 1 (previous model). So this is a lexical false negative, not
a behavioural regression, but it is a miss on the literal criterion.

## Decision under the pre-registered rule
The rule said any unmet criterion means roll back, so the **installed Claude copy was rolled back** (receipt
`backups/claude-20261021-172316-542500`; earlier Phase 2 edits are intact; Codex was never given the move). The change stays
**staged, uncommitted, in the working tree** as a proposal: generator, test, 12 workflows, the `context.md` header, and a
small harness-builder tweak. Tests pass (89 plus the one old `playwright` failure). `setup-claude.py verify` reports the
expected gap between source and the installed copy.

## What this does and does not show
- Cost: about +$0.0025 per loaded task (+2%), inside the prediction and the noise. Routing unchanged (10 vs 11 of 12 loaded;
  one fewer inventory-feature load).
- Quality: not measurable here. All four cases are at the ceiling, so the test can neither show the rules help nor that they
  hurt; it only shows nothing visibly broke.
- n=3 per case, baseline from a separate run the same day, one model.

## Options for the owner
1. **Adopt**: `py scripts/setup-claude.py apply` (and `py scripts/setup.py apply` for Codex). Reasoning for: the three
   invariants are Combo's core contract and the current model never loads them (0 of 11 loads read `context.md`); the cost is
   about 2%. Reasoning against: no measured quality benefit and one literal miss.
2. **Discard**: `git checkout -- skills/combo/workflows skills/combo/practices/context.md scripts/run-outcome-compare.py
   tests/test_outcome_compare.py` and delete `scripts/sync-context-core.py` and `tests/test_context_core.py`.
3. **First fix the scorer**: add a non-lexical alternative to the `planning intent` group (for example `recommend`), since the
   miss is a false negative, then re-run only plan-adapters (3 sessions, about $0.4) before deciding.

## Update: scorer fix, re-run and decision (2026-10-22, later)
Owner chose option 3. Scorer: `planning intent` in `evals/v2/cases.json` now also accepts `recommend` and `แนะนำ`, with three
tests (accepts a recommendation without the word "plan"; still fails an answer with no planning signal; does not excuse an
implementation claim or a changed file). Rescoring the stored first run offline flips only the one miss (11/12 to 12/12). The
same rescoring pass also showed an unrelated discrepancy in Phase 1 data (a `claude-run1` no-CLAUDE.md plan-adapters record
failing EmailAdapter evidence under the current scorer); it is not caused by this change and was not investigated.

Re-run (pre-registered addendum): 3 sessions of plan-adapters on the moved install, $0.37 reported, Sonnet 5.5, no advisor.

| Criterion, on the 15 moved runs | Result | Met |
| --- | --- | --- |
| All pass the (fixed) scorer | 15/15 (first 12 rescored, re-run 3/3) | Yes |
| Load count on the first 12 at least 9; plan-adapters loads in the re-run | 10 of 12; 3/3 | Yes |
| Moved loaded runs within +$0.01 of the baseline loaded mean ($0.1241) | $0.1261 over 13 loaded runs (+$0.0020) | Yes |
| `practices/context.md` not read | 0 reads in all 15 | Yes |

plan-adapters cost: moved $0.122 to $0.127 (6 runs) against $0.118 to $0.121 baseline (3 runs), about +$0.004 per run, consistent
with the predicted +$0.0035. All three re-run answers open with "# Plan: ..." and contain "plan", so they would also have passed
the original scorer; the 11/12 miss was therefore not repeated.

**Decision: adopted.** Installed into Claude (receipt `backups/claude-20261021-175327-081800`) and Codex (receipt
`backups/20261021-175502-305400`), both `verify` clean, Codex `[memories]` intact. Not committed.

Caveats: the scorer was changed after seeing a result, so this is a decision on a repaired metric; the cost, load-count and
context-read criteria are untouched by that and carry the weight. Quality is still unmeasurable at this ceiling. n=3 to 6
per case, one model, baseline from an earlier run the same day. To undo: `py scripts/setup-claude.py rollback --receipt
backups/claude-20261021-175327-081800/receipt.json`, the same for Codex with `scripts/setup.py`, and `git checkout` of the
workflows and `context.md`.
