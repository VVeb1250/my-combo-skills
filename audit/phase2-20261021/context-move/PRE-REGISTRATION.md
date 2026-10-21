# Context-core move: pre-registration (written before the test sessions ran)

Date 2026-10-22. Owner: "ลองย้ายแล้วเทสใหม่". Session count and cost stated first: 12 sessions, about $1.5.

## Change under test
The three invariant sections of `practices/context.md` (Own the outcome, Decision triage, Verify against intent, about
790 tokens) are copied into every workflow by `scripts/sync-context-core.py` (single source stays `context.md`), and the
"Read context once" instruction becomes a pointer for the remaining mechanics. Installed into Claude for the test.

## Why test it
At the current model the "Read context once" step is skipped (0 of 11 loaded runs read `context.md`), so its invariants
were not in context at all. The move puts them where the model does read.

## Run
`py scripts/run-outcome-compare.py --host claude --arms full --cases bug-zero inventory-feature plan-adapters security-review --repeats 3 --workers 2 --output evals/compare/results/moved-run1`
Baseline: the `full` arm of `inline-run1` (same cases, same model `claude-sonnet-5-5`, run earlier the same day):
12/12 pass, 11/12 loaded a workflow, Sonnet cost $0.1243 per run, no combo file read other than the workflow.

## Acceptance (fixed now)
- Pass 12/12 on the harness scorer.
- Workflow loaded in at least 9 of 12 runs (baseline 11).
- Mean Sonnet cost per run that loaded a workflow rises by no more than $0.01 (prediction: about +$0.0035 for the extra
  ~790 tokens written once).
- The run does not read `practices/context.md` more than the baseline did (0), i.e. the move removes that need.
Fail on any one: roll back (`setup-claude.py rollback --receipt <receipt>` and `git checkout` of the workflows).

## Not measurable here
Whether the rules change behaviour: all four cases are at the ceiling (Phase 1, pilots A, B and the cost experiment).
This tests cost, routing and no-regression only; descriptive output length is reported as a clarity proxy.

## Addendum 2026-10-22 (written before the re-run, after the first result)
First run: 11/12, the miss being a lexical scorer false negative (valid plan with no "plan"/"proposed"). Owner chose to fix
the scorer and re-run only plan-adapters. Scorer fix: `planning intent` in `evals/v2/cases.json` also accepts `recommend` and
`แนะนำ`; three tests added (accepts a recommendation without the word "plan", still fails an answer with no planning
signal, does not excuse an implementation claim or a changed file). Rescoring the stored first run gives 12/12 (offline).

Re-run: 3 sessions of plan-adapters on the moved install (about $0.4), same command shape, output `moved-run2`.
Decision by the original criteria on the 15 moved runs (the first 12 rescored plus these 3):
- all 15 pass the (fixed) scorer;
- plan-adapters loads the workflow in 3/3 of the new runs and the overall load count stays at least 9 of 12 on the first 12;
- mean Sonnet cost of moved runs that loaded a workflow stays within +$0.01 of the baseline loaded-run mean ($0.1241);
- no run reads `practices/context.md`.
All hold: adopt (install to Codex too, verify, keep uncommitted). Any fails: discard.
Caveat recorded in advance: the scorer was changed after seeing a result, so this is a decision on a repaired metric, not a
clean confirmatory test; the unchanged parts (cost, load count, context reads) carry the weight.
