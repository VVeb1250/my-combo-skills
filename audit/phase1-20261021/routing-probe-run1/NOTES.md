# Routing probe run 1 (2026-10-21)

`py scripts/run-routing-probe.py`, model `sonnet` (claude-sonnet-5), 31 cases x 2 arms,
one sample each, 62 sessions, no timeouts or harness errors, reported cost $3.11
(not an invoice). Raw transcripts stay in the git-ignored `evals/routing/results/`.
Tested the **installed** pack: item 8's new `combo-investigate` / `combo-review`
descriptions were not installed yet (installed files still hold the old text), so
this run is the baseline for them, not a test of them.

| | policy | description-only |
| --- | --- | --- |
| negative (no entry should load) | 6/6 | 6/6 |
| positive | 17/18 | 11/18 |
| confusable | 4/7 | 2/7 |
| total acceptable | 27/31 | 19/31 |

## What it shows [O]
- Neither arm over-triggers: all six negatives (translation, tiny edit, fact, chat,
  regex, brief definition) loaded no Combo entry.
- With the CLAUDE.md routing paragraph, 17/18 positives routed to the expected entry.
  The one miss, `pos-productivity-en`, went to the user's own `agent-handoff-spec`
  skill in **both** arms: a native-skill overlap, consistent with Combo deferring to
  native skills, not necessarily an error.
- Without the paragraph, descriptions alone routed 11/18. Misses were debug (2),
  deliver, review-en, investigate, content. Hits included plan, verify, research,
  learning, business, media, maintain, review-th.
- The three policy-arm confusable misses were `none` and each is a defensible inline
  answer on this one-function fixture (`conf-review-verify`: no change existed to
  review; `conf-debug-investigate`: explained the `value or 1` cause directly).
  The fixture is too small to force a workflow; treat confusable results as weak.

## What it does not show
- A routing miss is not a worse answer: in `description-only` the model usually
  still did the task inline. No outcome comparison was run.
- n=1 per cell, one model, one tiny fixture, the author's 80-skill environment.
- Whether the +8 routing difference survives repeats is unknown.

## Consequence for audit items 10-12
- Item 11 (shrink the routing pointer): not supported yet. The pointer is associated
  with +6 positive routes in this sample. Before removing it, run an outcome
  comparison (the `evals/v2` fixtures) under both arms.
- Item 8: install the repo, then rerun `--cases pos-review-en pos-investigate-en
  conf-investigate-research conf-security-review --arms description-only` for the new
  descriptions (repeat 3x; one sample is noise).
- Item 10 (conditional context.md): this probe does not measure it.
