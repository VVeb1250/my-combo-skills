# Phase 1 closeout, 2026-10-21

Phase 1 goal: audit `my-combo-skills` against current upstream sources and vendor
guidance, apply the low-risk updates, and decide with evidence what to do about the
instruction-modernization items. Detail: `SOURCE-AUDIT.md`. This file is the status.

## Status of the audit's proposal list

| # | Item | Status | Where / evidence |
| --- | --- | --- | --- |
| 1 | Replace M2D authority wording; regenerate | **Done** (source). Claude install unaffected: its override library never contained M2D | `c76623f` |
| 2 | `bun.md` Bun 1.4 refresh | **Not done.** Blocked: `build-specialists.py` allows only the single ECC pin, so this needs item 13 or a hand-written non-generated note | audit section 7 |
| 3 | `debug.md`: prove a forced red landed | Done, installed in Claude | `c76623f`, `8c917f4` |
| 4 | `tests.md`: seam catches/misses note | Done, installed in Claude | same |
| 5 | `simplicity.md`: project component first; moved code keeps validation | Done, installed in Claude | same |
| 6 | `review.md`: state assumed load | Done, installed in Claude | same |
| 7 | `mcp.md`: pin MCP packages | Done, installed in Claude | same |
| 8 | Trigger text for `combo-investigate` / `combo-review` | Done, installed in Claude. Description-only routing improved on the changed cases (5/12 vs 0/4 baseline; control unchanged, n=3) | `routing-probe-post-install/` |
| 9 | Negative-trigger and discovery eval | **Done**: 31-case routing probe + outcome harness (10 cases, Claude and Codex) | `evals/routing/`, `evals/compare/` |
| 10 | Make `context.md` load conditional / split | **Deferred.** Cost evidence says little to save from the file itself | below |
| 11 | Shrink the Skill-tool routing pointer / policy ladder | **Not recommended.** Pointer raises routing (27/31 vs 19/31) and no outcome loss was measurable, but nothing here shows Combo helps on hard work either | below |
| 12 | "New non-trivial logic leaves a small check" rule | **Deferred** (tied to the parked Shortcut experiment) | audit 3.2 |
| 13 | Full re-pin of the four packs | **Deferred.** Not needed for anything Phase 1 changed; the only content reason is `bun` | audit 2 |

Not installed: the **Codex** copy. Only `setup-claude.py` was applied; Codex still has
the pre-Phase-1 files until `setup.py` is run with its own plan/verify.

## What the evidence settled

1. **Upstream drift is small where Combo adapts it.** Karpathy 0 commits; Ponytail's rewrite
   agrees with Combo's stance; Matt's changes to adapted files are a few lines; 1 of 27
   ECC specialists needs a real refresh. No new upstream skill justified a new workflow.
2. **Routing:** with the CLAUDE.md routing paragraph, Claude picks the intended entry
   27/31 (17/18 on direct requests); with descriptions alone 19/31. No over-triggering in
   either arm. (n=1 per cell in run 1; the 5-case rerun used 3 repeats.)
3. **Outcome:** every arm on both hosts solved essentially every case, including two
   built to be hard (return-contract change across callers; one-function fix with
   tempting neighbours). Sonnet and `gpt-6-luna` do not need Combo's workflows to get
   these tasks right; quality is not what separates the arms here.
4. **Cost:** loading a workflow added turns (bug-zero 19.7 vs 13.7), ~24% more tokens and
   ~12% more reported cost per task. Tokens per turn were equal, so the driver is extra
   Skill calls and reads, not the size of `context.md` (about 1.8k tokens). [I]

## What it did not settle
- Whether Combo helps on genuinely hard or ambiguous work. No case found so far is hard
  enough to separate arms for these models, and finding one is costly.
- The effect of the routing paragraph alone: the Claude comparison removes all of
  CLAUDE.md, and an isolated Codex home was blocked (credentials, below).
- Library quality (533 references), six non-engineering workflows, six practices.

## Tooling left behind
- `scripts/run-routing-probe.py` (routing; stops at first Skill call), `evals/routing/`
- `scripts/run-outcome-compare.py` (outcome + cost, both hosts, `--rescore` for
  scorer fixes without model calls), `evals/compare/` (10 cases, hidden acceptance)
- Offline tests for cases, scoring, and hard-case fixtures: `tests/test_routing_probe.py`,
  `test_outcome_compare.py`, `test_hard_cases.py`. Suite: 55 of 56 pass before these; the
  one failure (`test_outcome_eval` UI journey) is an unrelated missing `playwright` module.
- Gotchas recorded in the READMEs: Windows `mkdtemp` ACL blocks the Codex sandbox; Thai
  negation fooled the claim regex; routing runs must stop at the Skill call to be cheap.

## Spend and limits
About 150 Claude sessions and 25 Codex sessions, roughly $17 of reported Claude cost
(not an invoice) and a large share of the usage limit; the 62-session first routing run
partly crashed on Windows temp cleanup and was resumed. Lesson saved to memory: state
session count and expected usage before launching, drop ceiling cases, pilot first.

Credential-related steps (finding auth files, copying auth into a separate home, even via
a Codex session) were denied by the permission classifier and were not worked around.

## Rollback and verification
- Claude install receipt: `backups/claude-20261020-192315-626800/receipt.json`
  (`py scripts/setup-claude.py rollback --receipt <file>`).
- Generated files check: `py scripts/build-specialists.py --check`,
  `py scripts/build-full-library.py --check`, `node scripts/validate-curated.cjs`.
- Commits: `02824ad` audit, `c76623f` items 1/3-8, `9e1e453` routing probe, `8c917f4`
  install and rerun, `34323d7` outcome harness, `e916f5e` hard cases and pilot. Nothing
  pushed.

## Suggested Phase 2 (owner decides)
1. Install the same files into Codex (`setup.py plan` first), then re-run the routing
   probe's Codex equivalent only if a Codex routing question exists.
2. Cheap, evidence-backed wins: `bun.md` as a hand-written note (item 2 alternative);
   leave 10-12 until a case exists where Combo changes the result.
3. Decide whether Combo's value case is cost/clarity or hard-task quality. If hard-task
   quality, source real failures from past sessions (Matt's own bar: an observed failure)
   instead of synthetic cases; that is the only affordable way to find a discriminating case.
4. Re-pin (item 13) only when a content reason appears; go through `sources.lock.json`
   and the generators, never by hand.
