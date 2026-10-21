# Phase 2 integration plan, 2026-10-21

Companion to [PHASE2-CAPABILITY-AUDIT.md](PHASE2-CAPABILITY-AUDIT.md). Evidence tags as there:
**[O]** observed by me, **[A]** reported by a Haiku reader from source, **[I]** inference,
**[H]** hypothesis.

## 0. Status

- Four small source edits and one new addendum were made in the working tree. **Nothing is
  committed. Nothing is installed.** The Claude install plan was generated and not applied
  (section 6). Codex is untouched.
- **Measured improvement from any of these edits: none.** Each Adopt rests on a gap I
  verified by search and on a signal the model cannot produce by reasoning (a computed number
  or a tool result). That is a justification, not an outcome result.
- Decision rule used for every candidate: see audit section 5.

## 1. Adopt (done in the working tree)

| # | Change | Where | Why (gap, signal) | Added tokens when loaded |
| --- | --- | --- | --- | --- |
| 1 | Experiment sample size: formula, computed rows (exact quantiles: 31,231 / 163,092 / 14,749), assumptions to state, peeking caveat | new `skills/combo/references/addenda/experiment-sample-size.md`; one pointer sentence in `workflows/business.md` | Combo had no power or sample-size planning [O grep]; the two files of one third-party skill disagree with each other and with the formula (1% to 1.1%: 150k, 380,000, formula 163,092) [O: both files read, arithmetic in Python] | about 600 only when the business workflow follows the pointer; 30 in business.md |
| 2 | Conditional axe-core path: `violations` are findings, `incomplete` is needs-review not pass, clean run is not WCAG conformance | `practices/e2e.md`, one bullet | host has accessibility snapshots, no rule engine; README states about 57% of WCAG issues are detected automatically [A] | about 90, only on e2e work |
| 3 | Silhouette IoU with reference-only and model-only areas; bounding-box alignment hides scale error; thresholds are working targets | `practices/outcome-evidence.md`, 3D row | Combo compares views without a metric [O grep `IoU` = 0]; method read in source [A] | about 90, only on 3D reference work |
| 4 | Route for ML training and evaluation (leakage, splits, guardrails, calibration) | `specialists/INDEX.md`, one row | reference existed but was routed only from research; combo-deliver and combo-business had no route [O] | about 35, only when the index is opened |

Not adopted although proposed in the brief: see sections 2 to 4.

### Provenance of the Adopt set

| Clause | Source repo @ full SHA | License | Written in own words |
| --- | --- | --- | --- |
| 1 sample size | standard two-proportion normal-approximation formula (no repo). Contradicting tables from `coreyhaines31/marketingskills` @ `e85f3cbc2e4a79bf33b2a12e9bdd9087d414735b` are cited as counter-evidence only | formula: n/a; repo: MIT | yes, nothing copied |
| 2 axe path | `dequelabs/axe-core` @ `f86d97816094e342bb63044a11d713c4beb7b89c` (develop; full SHA fetched by me, the reader's was garbled), `doc/API.md` result types, README coverage claim | MPL-2.0 | yes, no text copied |
| 3 IoU | `majidmanzarpour/blender-game-skills` @ `f0ef29385a03de139957e6f700b801cdc00b7e29`, `world_gate.py` / `compose_review.py` method | MIT | yes, no code or thresholds copied |
| 4 ML route | Combo's own vendored ECC `mle-workflow` (already in `source-map.md`) | MIT (ECC) | n/a, pointer only |

`source-map.md` is generated and was not edited. The addendum carries its own "Source:" footer,
following `references/addenda/bun-1-4.md`. No file in the Adopt set copies text from the
CC BY-SA, CC BY-NC-SA or unlicensed sources.

## 2. Pilot (needs a test or owner approval)

**Update 2026-10-22: pilots A and B were run baseline-only (5 sessions, about $0.14) and
every case passed. Clauses A and B are rejected for now; see
[pilot-ab/RESULTS.md](pilot-ab/RESULTS.md).** Rows C to F below are still unrun. The table
keeps A and B as originally planned.

Session counts and cost are **estimates**: Phase 1 averaged roughly $0.10 reported cost per
session (about $17 over about 175 sessions); short single-turn cases should cost less.
Following the Phase 1 lesson, every model pilot starts baseline-only and stops if the
baseline already passes.

| Pilot | What it would show | Cost to run | Stop rule | Approval needed |
| --- | --- | --- | --- | --- |
| **A. Unavailable-is-not-clean clause** (review/security). Fixture: a scan or lookup that did not run or returned nothing, asked "is this dependency clean?" | whether the baseline reports clean on empty/unreached evidence, [H] only | 2 baseline sessions, then +2 with the clause if baseline fails; about $0.2 to $0.4 | baseline says unassessable in both: stop, reject the clause | sessions |
| **B. MCQ validity** (learning). 3 item-writing cases; score offline: exactly one key survives, each distractor maps to a named misconception | whether Gate A/B wording changes item quality [H] | 3 baseline sessions, then +3 with clause if any baseline item fails; about $0.3 to $0.6 | all baseline items pass: stop | sessions |
| **C. axe tool trial.** Scratch dir, `npm install axe-core` (network), run on a page with one known violation and one known `incomplete` | the tool path works on this host and `incomplete` appears as documented | 0 model sessions | n/a | `npm install` plus a browser run; wrappers `@axe-core/*` unverified |
| **D. impeccable detector.** *Read-only check done 2026-10-22 ([pilot-de/READONLY-CHECKS.md](pilot-de/READONLY-CHECKS.md)): telemetry defaults on but only in the roll commands; `detect` reaches no network code. Remaining blocker is the binary install and local Chrome.* Install and run on 3 fixture pages | whether it finds slop an LLM reviewer misses [H] | 0 model sessions for the tool; a second arm would need LLM review sessions, not scoped here | telemetry on by default with no off switch: stop | binary install, browser over CDP |
| **E. Supply-chain collector.** *Read-only check done 2026-10-22: urllib forwards `Authorization` on any redirect (confirmed in CPython source), token goes only to api.github.com so exposure is low but unenforced; the collector runs `gh auth token` even with `--offline`, so it must run with `gh` absent from PATH.* Run on a fixture lockfile with no `gh` token | tri-state output and the "measured nothing" refusal on this host | 0 model sessions | token or redirect leak confirmed: stop | network access to 8 hosts; overlaps `bundle-tools:secure-scan` |
| **F. Routing-probe resampling of misses.** Re-run the 4 policy-arm misses of run 1 (`pos-productivity-en` went to the external `agent-handoff-spec`, `conf-review-verify`, `conf-plan-deliver`, `conf-debug-investigate`) with 2 repeats each: `--cases <ids> --arms policy`, one invocation per repeat; the probe stops at the first Skill call | whether the misses are noise or stable (run 1 was one sample per cell) | 8 short sessions (4 cases x 2); the 30-session rerun in Phase 1 cost $0.86, so likely under $0.5 [I] | all 4 hit on both repeats: close | sessions |

Recommended order by cost per decision: D read-only check, E read-only check, A, B, C, F.

## 3. Reference (keep as note, no edit)

- spec-kit stable requirement IDs plus a coverage table [A]: prompt-only upstream, no test on
  its output; overlaps `deliver.md` evidence mapping.
- Profiling method (devops-skills) [A]: method correct, one overclaim, evals prose-only; add a
  `debug.md` clause only when a perf failure case exists.
- K-Dense research mechanics [A]: per-query record fields, DOI registration is not claim
  support, same-study linkage, citation-count ranking buries uncounted work. First clause to
  pilot if research gets a case (the brief flags this caveat).
- Game development: Combo has none [O]. Candidates are young or structural; leads only
  (deepholm seeded Godot determinism tests, Godot headless runner). Write a specialist only on
  an owner need.
- Remotion drift [A]: Combo's copy says `Img`, upstream says `CanvasImage`. Verify against the
  installed Remotion version before changing; upstream has no license, so no text copying.
- skill-creator `run_eval.py` [A]: repeat sampling with a 0.5 threshold is the only idea
  Combo's probe lacks (pilot F). Do not adopt the script: it writes into the project and has
  no isolation or cost report.
- rr, windbg-mcp, citeguard, statgate (hunt leads) [A]: unverified depth; OS-bound or young.

## 4. Reject

- `fp-check` [A]: verdict is TRUE/FALSE POSITIVE only, so uncertainty collapses to false
  positive; Stop hook fires on every session with open issues; Claude-only. Duplicates Combo's
  trigger to consequence to evidence.
- Vercel react-best-practices [A]: ECC reference already carries the categories and the
  compiler note; no license file.
- Code-graph tools (codebase-memory-mcp, code-review-graph): host-native codegraph and
  struct-search already cover it.
- Product-Manager-Skills text: CC BY-NC-SA 4.0 [O]. OST is a public framework a model
  already knows; copying text is not possible under an MIT-style package.
- marketingskills sample-size tables: contradict each other [O].
- Data-science leakage validator: checks file structure only [A]; `mle-workflow` already
  covers the content.
- Any adoption of hooks, forced verdicts, or always-on gates from any source.

## 5. Insertion points, rollback, verification

- Insertion points: only existing hand-written files and one addendum; no new workflow, no
  new entry skill, no dependency, no hook, no script. Workflows, practices and
  `specialists/INDEX.md` are not generated [O: `build-specialists.py` does not emit them].
- Both hosts read the same `workflows/` and `practices/`; Claude overrides cover entries,
  router, `claude-code.md` and library indexes only [O], so no override needed changing.
- Rollback of the source edits (uncommitted):
  `git checkout -- skills/combo/practices/e2e.md skills/combo/practices/outcome-evidence.md skills/combo/specialists/INDEX.md skills/combo/workflows/business.md`
  and delete `skills/combo/references/addenda/experiment-sample-size.md`.
  Rollback of an applied Claude install: `py scripts/setup-claude.py rollback --receipt <receipt.json>`.
- Verified after the edits [O]: `build-specialists.py --check` (0 files would change),
  `build-full-library.py --check` (OK, 330 entries), `validate-curated.cjs` (14 packages,
  0 errors), `pytest tests` (80 passed, 1 failed). The one failure is the same
  `playwright`-missing UI journey test recorded in Phase 1; it was failing before the edits.
  New relative links resolve. `test_outcome_eval` still sees `practices/context.md` in the
  edited `business.md`.
- Not verified: that any edit improves agent output; behaviour of the edited files inside a
  live Claude session; the Codex copy.

## 6. Install boundary (owner decision)

`py scripts/setup-claude.py plan` produced a plan of **6 files**: the 4 edited files, the new
addendum, and `skills/combo/.combo-owned.json`. Every `before_sha256` matched the installed
state, so the apply would change nothing else. I did not apply it; the previous apply was the
owner's. To apply: `py scripts/setup-claude.py apply`, then `verify`, keep the receipt.
Codex install (`setup.py plan`) is out of scope for this phase. The plan artifact in
`audit/claude/install-plan.json` was restored to its committed content; regenerate it with
`plan`.

## 7. Owner decisions requested

1. Apply the Claude install of the 6 files? (0 model sessions)
2. ~~Approve pilots A and B~~ Done 2026-10-22, all pass, clauses rejected.
3. Approve C (`npm install axe-core` in a scratch directory, network)?
4. Approve D and E read-only code checks first, and their installs only if clean?
5. Approve F (about 8 short sessions)?
6. Commit the working tree? Nothing was committed.
7. Carry-over from Phase 1: is Combo's value case cost and clarity, or hard-task quality? That
   decides whether more prose gates are worth piloting at all.

## 8. Unresolved risks

- No measured improvement; Phase 1 found a ceiling effect on current models, so these
  clauses may change nothing for strong runs. They cost tokens only on the specific task type.
- Silhouette IoU thresholds from the source are uncalibrated and not copied.
- axe guidance assumes the project can run it; wrappers were not verified.
- Licence readings are my interpretation, not legal advice.
- Haiku-reported claims in the audit were checked only where a decision depended on them.
- One reader attempted an unrequested session hand-off (denied, no effect); two left scratch
  files in `/tmp` outside the repo.
