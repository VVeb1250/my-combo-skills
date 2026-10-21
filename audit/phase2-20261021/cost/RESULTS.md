# Cost/clarity track: pricing Combo workflow loads, 2026-10-22

**Superseded in part, 2026-10-22:** these dollar figures are for the earlier model (`claude-sonnet-5`, $0.20 per Mtok cache read, with the advisor active). The current `claude-sonnet-5-5` prices cache reads at $0.10 and the same tasks cost about 0.66 times as much; see [../cost-experiment/RESULTS.md](../cost-experiment/RESULTS.md). The proportions and method stand.

**Model sessions run: 0. Cost of this analysis: $0.** It reprices the 48 Claude sessions of
Phase 1 (`evals/compare/results/claude-run1`, git-ignored raw logs, 8 cases x 2 arms x 3
repeats) from their stored per-turn token usage. Script: `price_loads.py`; full output:
`price_loads.out.txt`; per-run rows: `price_loads.json`. Tags: **[O]** observed in the data,
**[I]** inference.

## What it measures and how it was checked

- Cost of a run is a function of four token counts at list price: the fit on the Sonnet usage
  of 48 runs has R2 = 0.9999 (max error $0.0026) with rates of about $4.00 per Mtok for cache
  writes, $0.20 for cache reads and $9.07 for output [O]. Those are fitted from the logs, not
  looked up.
- Nine runs (the plan-adapters and security-review cells) **also billed `claude-opus-5`**: the
  owner's global advisor tool was active inside the harness sessions. That spend is separated
  [O]: it totals $2.52 of the $10.67 in Phase 1's reported cost, and in those cells it is
  larger than the Sonnet cost. It is not a Combo effect and is excluded from every number
  below unless labelled "advisor".
- The cost of a load is counterfactual: for each message that calls the Skill tool or reads a
  file under `skills/combo`, the extra API call (it re-reads the whole context) plus the text
  it adds (written once, then re-read on every later call). It assumes the run would have
  done the same other work without the load [I].
- Two analyzer bugs were found and fixed before reporting: the first fit treated advisor spend
  as Sonnet spend (R2 0.23), and the first path match missed JSON-escaped backslashes so it
  counted 1 workflow-file read instead of 21.

## Price of a workflow load (Sonnet, list price, Phase 1 task size)

| Event | Events seen | Tokens added to context | Mean cost per event |
| --- | ---: | ---: | ---: |
| Entry stub (the Skill call) | 24 | 667 | $0.0060 |
| Workflow file read | 21 | 1,012 | $0.0120 |
| `practices/context.md` read | 14 | 2,028 | $0.0149 |
| Another practice read | 10 | 1,615 | $0.0110 |

- A task that loads a workflow pays about **$0.033** for the load (full arm, 17 runs: 2.6
  load calls, 3,676 tokens added), which is **15% of a $0.219 Sonnet run** [O].
- Averaged over all 24 `full` runs including the ones that load nothing: $0.0236 per run
  (12.6%). Without CLAUDE.md the same cases pay $0.0061 per run because the workflow loaded in
  7 of 24 runs instead of 17.
- By workflow (all arms): debug $0.029, deliver $0.029, plan $0.025, review $0.036 per
  loaded task; review is the highest because it reads more files (3.0 load calls).
- Nothing loads on the negative cases (translation, trivial label): those cost the prefix only.

## Where the Sonnet cost goes, mean per run

| Bucket | `full` | `no-claude-md` | Difference |
| --- | ---: | ---: | ---: |
| Turn 1: writing the prefix (system, skill list, CLAUDE.md) | $0.0876 | $0.0702 | $0.0174 |
| Later calls: re-reading context | $0.0575 | $0.0427 | $0.0149 |
| Later calls: new content written | $0.0197 | $0.0151 | $0.0046 |
| Output | $0.0198 | $0.0203 | -$0.0005 |
| Total | $0.1876 | $0.1521 | **$0.0355 (19%)** |

(With the advisor included the totals are $0.237 and $0.208, a 12% difference, which is the
figure Phase 1 reported; the advisor spend dilutes the Sonnet difference.)

## What the difference is made of [O/I]

The `no-claude-md` arm removes the **whole** global CLAUDE.md, not only Combo's block:

- The CLAUDE.md prefix is 4,350 tokens (31,586 vs 27,236 tokens at the first call). Written
  once and re-read on later calls it costs **$0.017 for a one-call run, $0.024 for the mean
  run, $0.034 for a 20-call run**.
- Combo's own policy block is about 736 tokens (`adapters/claude/POLICY.md`, chars/4): about
  **$0.004 per mean run**, about 17% of the CLAUDE.md prefix. The rest of that prefix is the
  owner's own non-Combo instructions.
- The workflow load is the other half: $0.0236 per run on average.
- The two overlap in the buckets above (a bigger context also makes every later call cost
  more), so they do not sum exactly to the $0.0355 difference.

## Reading for the open audit items [I]

- **Item 11 (shrink the policy block / routing pointer):** at most about $0.004 per run could be
  saved, a few percent of a run. Phase 1 found the pointer raises routing from 19/31 to 27/31.
  The saving is small against that benefit.
- **Item 10 (conditional `context.md`):** the read costs $0.0149 per event and $0.0074 per
  average run in the full arm; it is the largest single load step. Making it conditional or
  folding its invariants into the workflow would save up to that amount where it is read, with
  the risk Phase 1 recorded that the model then lacks the yardstick before it judges.
- **Workflow read:** $0.0088 per average run. The entry stub, the workflow and `context.md` are
  three separate calls. Putting the workflow body in the entry stub would save about two extra
  calls (about $0.0074 each in re-read cost) but keeps the same text in context; it trades
  progressive disclosure for fewer calls. This was not tested.
- **The largest always-on cost is outside Combo:** the owner's own CLAUDE.md content is about
  $0.020 of the $0.024 per run.
- **Eval hygiene:** the advisor tool should be off inside harness sessions, or cost
  comparisons on plan and review cases are dominated by Opus calls.

## Limits

- Counterfactual attribution assumes no behaviour change from removing a load; it was not run.
- One model (`claude-sonnet-5`), tasks of 1 to 16 calls, 3 repeats per cell, one machine.
- Turn 1 is a cache write at the 1-hour rate. In a long warm session the prefix is amortized
  and a load is a one-time cost of a few cents; the share of a long task is lower than here.
- Cost at list price from fitted rates, not an invoice. Output cost of load messages was
  ignored (a lower bound; per-message output in the stream is a partial count).
- Not measured: whether a load changes quality. Phase 1 and pilots A and B found no outcome
  difference at this task size.

## What a controlled follow-up would need

A variant arm (for example an entry stub that inlines its workflow) needs a separate Claude
config home with authentication; the harness deliberately never copies credentials, so the
owner would prepare that home. Estimated size once it exists: 4 workflow cases x 2 arms x 3
repeats = 24 sessions, roughly $0.19 each at the Sonnet cost above with the advisor off,
about $4.5. Not started.
