# Inline-workflow cost experiment, 2026-10-22

Pre-registered in [PRE-REGISTRATION.md](PRE-REGISTRATION.md) before any session ran. **26 sessions** (2 smoke,
24 main), $0.25 + $2.99 reported, all on `claude-sonnet-5-5`; no advisor spend. Raw logs are git-ignored; kept here:
`inline-run1.summary.*`, `price_loads.inline-run1.out.txt`. Tags: **[O]** observed, **[I]** inference.

## What was compared
`full` = the installed entry skills (stub, then Read workflow, then Read `context.md`). `inline` = a plugin
(`combo-lab`) whose four entry skills (debug, deliver, plan, review) carry identical descriptions and already contain
the workflow and `context.md` text; the originals are switched off. Cases: bug-zero, inventory-feature, plan-adapters,
security-review, 3 repeats each. No credentials were involved (`--plugin-dir` plus `skillOverrides`).

## Results [O]
| | `full` | `inline` |
| --- | ---: | ---: |
| Outcome pass | 12/12 | 12/12 |
| Sonnet cost per run | $0.1243 | $0.1247 |
| Runs that loaded a workflow | 11/12 | 6/12 |
| Mean calls per run | 5.8 | 5.7 |

- **Prediction refuted.** I predicted about $0.015 saved per load (two removed re-reads at the previous model's
  price). Total cost is identical, and where both arms loaded a workflow (plan and review) `inline` cost **more in all
  6 paired runs**: plan $0.118/0.121/0.118 vs $0.135/0.127/0.129, review $0.107/0.103/0.103 vs $0.110/0.113/0.109;
  about +$0.009 per run (+8%).
- **Why [I]:** `inline` does remove a call (loaded runs: 1.0 load call vs 2.0), but a call now costs only about
  $0.0026, because the fitted rates for this model are $4.00 per Mtok cache write, **$0.10** cache read (was $0.20),
  $10.00 output, $2.00 input, exact to six decimals. The inline body also carries `context.md` (loaded runs add 3,588
  tokens vs 2,009), and `full` never reads it.
- **`context.md` was not read in any of the 11 loaded `full` runs** [O]: every load was Skill call plus one Read of the
  workflow file. In Phase 1 (previous model) it was read in 14 load events. The "Read context once" step in all 12
  workflows is currently being skipped by this model, so `context.md`'s invariants are not in context unless the
  workflow body repeats them.
- **Routing differs by arm:** the plugin-namespaced debug and deliver skills were never chosen (0/6) while plan and
  review were chosen 6/6; `full` loaded debug 2/3 and deliver 3/3. The cause was not isolated. Not-loaded runs cost
  no less ($0.129 vs $0.121 loaded in `inline`), so the routing difference did not change cost here.
- Smoke test: the plugin skill is invoked (`combo-lab:combo-review`) and no Combo file is read; one run failed the
  scorer only because "I changed nothing" was read as a claim of implementation (negation after the verb). Fixed in
  `scripts/run-outcome-compare.py` with a test; the smoke result rescored to 2/2.

## Re-pricing at the current model [O]
Phase 1's per-call price no longer holds. Mean Sonnet cost per run is $0.124 (was $0.188), calls per run 5.8 (was 8.8),
the prefix write is $0.076 per run, and a workflow load costs about $0.0105 per run (8.5%) in `full` (was $0.0236,
12.6%). The Phase 1 conclusions about proportions hold; its dollar figures are for the earlier model.

## Reading for the owner [I]
1. Folding the workflow and `context.md` into the entry skill is **not** a cost win at this model's prices; do not do it
   for cost. It also changes routing.
2. Making `context.md` conditional (audit item 10) saves nothing for this model: it is already not read. The open
   question is the other way: whether its invariants (own the outcome, decision triage, verify against intent) should be
   in the workflow bodies. That would cost about 1.8k tokens per loaded task (about $0.007 write plus about $0.0002 per
   later call) and has no measured quality effect either way (all cases pass).
3. The advisor did not run in this experiment; Phase 1's 9 advisor runs were a property of that period.

## Limits
One model version, four cases, three repeats, tiny tasks (3 to 10 calls), one machine. The `inline` arm's lower load
rate means its cost comparison rests on plan and review only (6 pairs). Cost is list price from fitted rates, not an
invoice. Not tested: the same comparison with the previous model, or longer sessions where the prefix is amortized.

## Harness changes (offline-tested)
`scripts/run-outcome-compare.py`: arm `inline` (`build_inline_plugin`, `skillOverrides`), negation-after fix in
`claims_implementation`; `tests/test_outcome_compare.py`: plugin builder and command tests, new negation cases.
