# Phase 2 capability audit, 2026-10-21

Scope: find capabilities that add something to Combo beyond what the current model plus the
current Combo already do, and decide Adopt / Pilot / Reference / Reject per candidate. Phase 1
(`../phase1-20261021/`) is the baseline and is not repeated. Out of scope: token optimisation,
caveman, model routing, Codex install.

Evidence tags: **[O]** observed by me in a file or command output; **[A]** reported by a Haiku
reader that read the source through `gh api` (read-only; not independently re-read by me);
**[I]** inference; **[H]** hypothesis, needs a test. A claim with no tag is a decision.

## 1. Method and what it did not cover

- Combo side: read all 12 workflows, 11 practices, the specialist index, the library indexes,
  `install-manifest.json`, the override listing, `PHASE1-CLOSEOUT.md`, `SOURCE-AUDIT.md`. [O]
- Library depth (533 refs) was inventoried by three Haiku readers against 49 named
  mechanisms (not topics). Every "missing" that mattered was re-checked by me with
  case-sensitive, word-boundary Python search over `skills/combo` and
  `adapters/claude/overrides` (script output reproduced in section 2). [O]
- External sources: 8 Haiku readers, each pinned to a commit SHA, read through `gh api` only.
  Nothing was cloned, installed or executed. I re-read the claims that drive a decision:
  the supply-chain tri-state tests, the Product-Manager-Skills license, the impeccable
  license, and the sample-size arithmetic. [O]
- Not read: Combo's other 14 library domain files beyond the indexes, `references/angular/`,
  `run_loop.py` / `aggregate_benchmark.py` in skill-creator, impeccable's Rust per-rule
  coverage, Playwright `trace` subcommand source, `@axe-core/*` wrapper packages, Learning
  Commons KG connector. No tests from any external repo were run.
- No model session was spent on evaluation in this phase. Reader agents were Haiku 5.5.
  One reader tried a session hand-off (denied, no effect); two left scratch files
  (`/tmp/speckit_tests.txt`, `/tmp/sk_sel.txt`, outside the repo).
- Stars and installs were not used as evidence.
- **Not hunted this phase** (no lead supplied and no search run): productivity and
  coordination; SEO and editorial quality beyond the marketing A/B skill; learning beyond
  the K-12 repo; incident or operations tooling. These rows are Unknown, not "nothing
  exists". The hunter covered eight engineering/research/stats gaps only.

## 2. Combo inventory (what exists)

Status rules (mechanical): **implemented** = a workflow or practice states the mechanism with a
concrete step or pass/fail criterion. **partial** = a workflow or practice names the concern
without a criterion. **reference-only** = exists only under `references/library/` or
`specialists/`, no workflow or practice routes to it. **missing** = no match after word-boundary
search. Table covers the mechanisms that mattered for candidates.

| Mechanism | Status | Evidence |
| --- | --- | --- |
| Spec-vs-code requirement fidelity | implemented | `workflows/review.md` step 3 [A] |
| Requirement-to-evidence mapping | partial | `deliver.md` "Map every acceptance condition to actual evidence"; no stable IDs, no uncovered-requirement list [O] |
| Trigger-to-consequence per finding | implemented | `review.md` step 4 [O] |
| Evidence verdict that blocks false confidence | **mostly implemented** | `verify.md` has pass/fail/inconclusive/blocked for checks; `security.md` ends "Do not label an unexercised concern as verified"; `review.md` step 5 separates unresolved concerns and the closing line asks for evidence and limits with a no-finding result [O]. Uncovered remainder: an empty result, a scan that did not run, or an unreachable source reported as clean |
| Threat model, source-to-sink | partial | `security.md` "identify trust boundary, asset, actor"; grep: no "threat model"/"source-to-sink" in workflows or practices [O] |
| Registry-metadata supply-chain audit | missing | no typosquat/maintainer/registry hits outside generic `npm audit` text [A] |
| Profiling method (sampling vs instrumentation, off-CPU, flame graph) | partial | `debug.md` "measure a baseline"; grep for flame graph/off-CPU/py-spy: 0 files [O] |
| Bisect / trace replay | partial | `diagnosing-bugs` reference has bisect; not carried into `debug.md` [O] |
| Browser console/network evidence | implemented | `e2e.md` [A] |
| Automated accessibility engine (axe) | reference-only | `browser-qa`, `react-testing` references only [O: grep `axe` = 3 files, none workflow/practice] |
| Network mocking, trace capture | missing | grep `page.route`/trace viewer: 0 [O] |
| Deterministic UI anti-pattern detector | reference-only | `design-system` "AI Slop Detection" prose [A] |
| 3D reference comparison metric (IoU, width profile) | missing (view comparison only) | `outcome-evidence.md` row 1; grep `IoU`: 0 [O] |
| GLB/FBX roundtrip, GLTFLoader/AnimationMixer/KTX2 | reference-only / missing | grep: 0 hits [O] |
| Game development content | **missing entirely** | grep for gameplay/game loop/Unity/Godot/Unreal/Phaser: 1 incidental hit [O] |
| Deterministic replay, seeded simulation | partial | `tests.md` "pinned time or randomness" [O] |
| ML leakage, splits, guardrails | **reference-only; routed only from research** | only `ecc/mle-workflow`; `library/research.md` lists it and `workflows/research.md` points at that index, but ML work entering through combo-deliver or combo-business has no route (specialist index had no row before this phase) [O] |
| Power / sample-size planning | **missing** | grep `power analysis`: 0; `sample size`: 2 unrelated files [O] |
| Forecast held-out validation | implemented (thin) | `business.md` "validate on held-out periods" [O] |
| Opportunity-solution tree | missing | grep: 0 [O] |
| Voice-of-customer evidence handling | partial | `research.md` fact/inference split only [O] |
| Literature search record, DOI check, same-study dedup | partial | `research.md` coverage-gap line; DOI only in library reference [A] |
| Citation-count/venue caveat for new work | missing | grep `citation count`: 1 library file [O] |
| MCQ item validity (one defensible answer, distractors from misconceptions) | missing | grep `distractor`: 0; `defensible`: 5 unrelated [O] |
| Experiment design for growth/CRO | missing | `A/B` 6 library files, none workflow [O] |
| Skill routing and outcome evaluation | implemented outside workflows | `scripts/run-routing-probe.py`, `run-outcome-compare.py`, `validate-curated.cjs` [O] |

Finding [O]: no workflow routes into the engineering/ML library except through the `/combo`
router and the generic library indexes. "Reference-only" is Combo's dominant state for
anything specialised.

## 3. Capability gap matrix, all 12 workflows

Existing capability is the Combo status above. Recommendation key: Adopt = small patch now;
Pilot = needs a test or owner approval first; Reference = note only; Reject.

| Workflow | Candidate (source @ commit, license) | Mechanism | Gap | Evidence | Type | Collision | Dependencies | Validation | Rec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | github/spec-kit @ f90f7dd, MIT | stable FR/SC IDs, requirement-to-task coverage table | partial | `analyze` is prompt-only; deterministic code only checks file existence; no test asserts findings [A] | Practice (output shape) | Low (overlaps deliver mapping) | none | multi-requirement spec: uncovered IDs listed | Reference |
| plan | deanpeters/Product-Manager-Skills @ cfcb697, **CC BY-NC-SA 4.0** | OST (Torres), VoC evidence rules | missing | LICENSE read [O]; OST is a public framework; agent-scored 1-5 table [A] | Practice | Low | none | none | Reject text, Reference concept |
| deliver | awesome-gamedev-agent-skills @ 0a70cfc, Apache-2.0 | engine-pattern notes, structural validator | missing (game) | validator is structural; glTF skill describes KTX2 but body covers DRACO only; code never executed [A] | Specialist | Low | none | none | Reference |
| deliver | vercel-labs/agent-skills @ 063bee9, no LICENSE file (README says MIT) | 70 React rules | duplicate | ECC reference already carries 8 categories and the compiler note [A] | Reference | n/a | n/a | none | Reject |
| debug | arjunprabhulal/devops-skills @ 0c89b7e, MIT | profiling method | partial | method correct; one overclaim ("almost always IO or lock"); evals are prose, one rewards the overclaim [A] | Practice | Low | none | needs a perf failure case | Reference |
| debug | rr-debugger/rr, windbg-mcp (hunt leads) | record/replay, time-travel | partial | OS-bound (Linux x86-64 / Windows); depth not read [A] | Tool | n/a | OS, install | none | Reference (unverified) |
| review | trailofbits/skills @ a313174, **CC BY-SA 4.0** `supply-chain-risk-auditor` | tri-state verdict, coverage accounting, "measured nothing" refusal | mostly covered; remainder is "empty or unavailable result is not clean" | the collector's tests assert it: empty advisory = UNASSESSABLE until existence proven, clean needs a datum, all-sources-down refuses [O: test_collect.py:307, test_model.py:65]; this proves the code, not that a prose clause changes agent behaviour | Practice (idea) / Tool | Medium: host already has `bundle-tools:secure-scan` | tool: Python 3.11 stdlib, 8 network hosts, `gh auth token` sent as Bearer | clause: fixture where a scan did not run; tool: fixture lockfile | **Pilot** clause (unmeasured prose gate); Pilot tool |
| review | trailofbits `fp-check` | discovery vs verification split, 6 gates, hooks | duplicate | verdict is TRUE/FALSE POSITIVE only; uncertainty collapses to false positive; Stop hook fires every session, open issues #143 #289 #342 [A] | Practice/Hook | High (hooks, forces verdict) | Claude-only hooks | n/a | Reject |
| verify | dequelabs/axe-core @ f86d97816094e342bb63044a11d713c4beb7b89c, MPL-2.0 | rule engine; `incomplete` = needs review | missing natively | host has a11y snapshots, no rules; README states ~57% of WCAG issues auto-detected; wrappers not in this repo [A] | Tool | Low: host `design:accessibility-review` skill is review prose (not read this phase), so it does not supply a rule engine [I] | npm install + a browser | run on a page with a known violation | **Adopt conditional clause**; Pilot tool |
| verify | microsoft/playwright @ 66070a1, Apache-2.0 | tracing, route mocking, trace CLI | partial | MCP lists no trace capture; `playwright-cli` tracing needs global install [A] | Tool | Medium (host Playwright MCP) | global npm install, approval | none | Reference |
| investigate | codebase-memory-mcp, code-review-graph (hunt leads) | code graph | duplicate (host-native) | host already has codegraph MCP and struct-search; test depth unread [A] | Tool | High | install | none | Reject |
| research | K-Dense/scientific-agent-skills @ 593377b, MIT (mixed: some GPL-wrapping skills) | per-query record fields, DOI+Crossref registration check, DOI-first dedup | partial | scripts have mocked tests; DOI check is registration only; missing citation count ranks below zero (so new work buried) [A] | Practice | Low | requests, 2 hosts | none | **Reference** (prose, no computed signal; the owner's brief flags the citation-count caveat, so it is the first Pilot clause if research gets a case); scripts Reference |
| content | coreyhaines31/marketingskills @ e85f3cb, MIT `ab-testing` | hypothesis, guardrails, sample-size tables | partial | **the skill's two files disagree with each other and with the formula**: 1% to 1.1% is 150k per variant in `SKILL.md:87` and 380,000 in `references/sample-size-guide.md`, formula gives 163,092; `SKILL.md` 5%/10% says 27k, formula 31,231; no code [O: both files read, arithmetic in Python] | Practice | Low | none | recompute | Reject tables; see business |
| learning | anthropics/k12-teacher-skills @ 31fd6db, Apache-2.0 | Gate A (one survivor), Gate B (distractor reachable), rubric CSV | missing | both gates are prompted self-checks; CSV rubric has no judge or runner in repo; math only [A] | Eval asset / Practice | Low | none | 1-3 item fixture | **Pilot** |
| business | aiopshwang/data-analysis-ml-agent-skills @ 82a1dc2, MIT | prediction-time ledger, in-fold transforms, calibrator split | duplicate | validator checks file structure only; `mle-workflow` already covers timing, splits, leakage [A] | Reference | n/a | n/a | none | Reject (route existing) |
| business | experiment statistics (own formula; no external source) | power/sample-size, peeking | missing | verified arithmetic, section 4 [O] | Practice (addendum) | Low | none | recompute table in a test | **Adopt** |
| media | majidmanzarpour/blender-game-skills @ f0ef293, MIT | fixed-world silhouette IoU with reference-only/model-only residuals | missing | method sound; **no tests, one commit, thresholds undocumented, world_gate exits 0 always** [A] | Practice (idea) | Low | Blender bpy for the script | measure on a known-wrong model | **Adopt idea as conditional clause**; Reference script |
| media | pbakaus/impeccable @ dad8dbb, Apache-2.0 | Rust detector, 64 rules, three engines | partial | real and tested; telemetry default unverified; about 12 of 64 rule ids with no same-named fixture [A] | Tool | Medium | Rust binary, browser over CDP | run on a page with known slop | Pilot (approval) |
| media | remotion-dev/skills @ 039e8a2, **no license** | newer API names | drift | Combo copy says `Img`, upstream says `CanvasImage` [A] | Reference | n/a | n/a | check installed Remotion | Reference (flag drift) |
| productivity | **not hunted this phase; no lead supplied** | n/a | n/a | Combo's handoff/decision text exists (`productivity.md`, `context.md`); no external source was read for this workflow | n/a | n/a | n/a | n/a | Unknown |
| maintain | anthropics/skills `skill-creator` @ dbd4588, Apache-2.0 | repeat sampling with 0.5 threshold, description rewrite loop | partial | `run_eval.py` writes into the project `.claude/commands`, no isolation, no cost report; Combo's probe is stricter [A] | Eval | Low | claude CLI, sessions | re-sample only miss cases | Reference; Pilot repeat sampling |

Hunt leads without enough reading (all young, MIT, shallow checks) [A]: sterium-ai/deepholm
(seeded Godot determinism tests), wedo911/citeguard (Crossref client), yashchimata/statgate
(power/sequential code, correctness unchecked). Listed as leads, not recommendations.
No credible candidate was found for profiling-for-agents, threat-model tooling, or spec
consistency checkers.

## 4. Verified facts that drive decisions

- Supply-chain tri-state: `test_empty_advisory_answer_needs_proof_of_existence` asserts
  UNASSESSABLE then CLEAN once existence is proven; `test_clean_signal_demands_a_datum`
  asserts a CLEAN signal without a datum raises. [O, pinned SHA a313174]
- fp-check has no unassessable state, so it does not fill that gap. [A]
- Sample size, two-proportion normal approximation, alpha 0.05 two-sided, power 0.80,
  n per arm = (z_0.975 + z_0.80)^2 * (p1 q1 + p2 q2) / (p2 - p1)^2. Exact quantiles
  (`statistics.NormalDist`, squared z-sum 7.8489): 5% to 5.5% gives 31,231; 1% to 1.1% gives
  163,092; 10% to 11% gives 14,749. Rounded z (1.96, 0.84; 7.84) gives 31,196 / 162,908 /
  14,732, about 0.1% lower, which is what the Haiku reader's hand arithmetic used. The
  shipped addendum uses the exact values. [O, computed with Python]
- Marketing-skills contradiction, read from the pinned files: `SKILL.md:87` lists 150k per
  variant for baseline 1% and 10% lift and 27k for 5%; `references/sample-size-guide.md`
  lists 380,000 for 1% to 1.1%. [O]
- License readings, not legal advice [I]: CC BY-SA 4.0 and CC BY-NC-SA 4.0 text cannot be
  copied into an MIT-style package without taking on share-alike and, for the second,
  non-commercial terms. Vercel and Remotion carry no license file, so no copying. Combo
  therefore adopts ideas in its own words only and copies no text from the six sources
  marked above.

## 5. Ranking

Lens: does the candidate give the agent a signal it cannot get by reasoning (a computed
number or a tool result), weighed by evidence strength, generality, integration risk and
maintenance. Phase 1 showed prose the model already follows adds cost without measurable
gain, so a prose-only candidate ranks below any computed or tool signal.

**One decision rule, applied to every row.** Adopt = a clause or note that points the agent
at a computed or tool signal it cannot produce by reasoning, for a gap verified by search,
with no new dependency, hook or default behaviour; or a pointer that only makes
already-vendored content reachable, with no new text (item 4). Pilot = an unmeasured prose gate, or a
tool that needs an install or network, until a test or owner approval exists. Reference =
useful knowledge without a verified gap or without a usable license. Reject = duplicate of
Combo or host capability, or unsafe to adopt.

1. Experiment sample size computed in code (computed signal; verified gap; source tables wrong) **Adopt**
2. Fixed-camera silhouette IoU for 3D (computed signal; method sound; upstream untested) **Adopt as conditional clause**
3. axe-core as a conditional tool path (tool signal; native gap; install needs authorization) **Adopt as conditional clause**
4. ML evaluation route (mle-workflow) from the specialist index (routing fix, no new content) **Adopt**
5. Supply-chain "empty or unavailable is not clean" clause (prose gate) **Pilot, run 2026-10-22: bare model passed 2/2, clause rejected** ([pilot-ab/RESULTS.md](pilot-ab/RESULTS.md))
6. Learning MCQ gates (prose gate) **Pilot, run 2026-10-22: bare model passed 9/9 items, clause rejected** (numeric items only)
7. impeccable detector, supply-chain collector, axe/Playwright tooling (tool signal; install, network or telemetry questions) **Pilot, owner approval**
8. research clauses, spec-kit ID table, profiling clause, game-dev notes: **Reference**
9. fp-check, Vercel react rules, code-graph tools, PM-skills text: **Reject**

## 6. Limits of this audit

- Haiku-reported items [A] were spot-checked only where a decision depended on them.
- "Missing" is established by search over `skills/combo` and Claude overrides excluding
  Angular; the installed Claude copy was not diffed against the source tree this phase.
- No claim here is a measured improvement. Every Adopt below is justified by a verified
  gap, not by an outcome result; see the integration plan for what would prove value.
- Haiku one-pass reads can miss content; negatives were re-searched, positives on
  external repos were not.
