# Phase 4: Full active-source skill audit after PR #4

**Date:** 2026-10-27 · **Status:** Source-content audit complete; outcome improvements **unverified** · **PR:** stacked on [#4](https://github.com/VVeb1250/my-combo-skills/pull/4)

## Inventory and reproducibility

Read the upstream SKILL.md bodies for all **45 distinct skills** in the three pinned source packs: **Karpathy derivative 1**, **Ponytail 6**, **Matt 38**. Also inspected Ponytail's **six OpenClaw counterparts**, verified all six are **byte-for-byte identical in the body** after stripping frontmatter. That gives 51 actual SKILL.md files, 45 unique procedural bodies, not 51 independent skills. Matt groups: 20 engineering, 7 in-progress, 4 frozen misc, 7 productivity.

Source pins checked against their current public Git trees on October 27: Karpathy `2c606141936f1eeef17fa3043a72095b4765b9c2` (repo head last commit 2026-04-20); Ponytail `09c434ab73ca43761c5d8b0c5d341926c2fba710` (2026-10-18); Matt `5beb35b040e3de97e54fa9e386d7e42d15c295c2` (2026-10-19). The **Karpathy source is a third-party skill based on his public comments**, not evidence of a controlled evaluation conducted by Karpathy. Existing Combo full-library is a **reference**, not all these skills enabled at runtime.

Classification: `already-covered` = explicit compatible Combo owner; `targeted-change` = evidence of missing conditional handling with a minimal patch; `reference-only` = useful in a named case but no default trigger; `reject-default` = host-bound, unsupported ceremony, duplicate store, overfitting, or incompatible default. Classification is **not** a test pass or proof of causal improvement.

**Counts:** `already-covered` 17; `targeted-change` 3; `reference-only` 17; `reject-default` 8 = 45 distinct skills. **No new active Skill Entrypoint** is proposed.

## Most important findings

### 1. More skill entrances are not the current bottleneck

The phase 3A [cost audit](../../audit/phase3a-20261022/AUDIT.md) attributes ~0.4% of measured real-session cost to Combo's 14 entrypoint metadata and policy. Most loaded work and tool history comes from host prefix/context, not the number of entry labels. PR #4 keeps 14; this PR does too. Avoid combining the upstream Matts's interview→spec→tickets→TDD→two-agent review→retro flow with Combo's own workflow architecture.

### 2. Ponytail provides the strongest causal evidence among these three *for its own core coding skill*

[Ponytail's 2026-10-07 agentic A/B](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/benchmarks/results/2026-10-07-agentic.md) describes 39 tasks × 5 repetitions × 3 arms = 585 headless Opus 5.5 Claude Code sessions. Compared to no-skill, Ponytail 5 reported **53% less code**, **26% less modeled cost**, **41% less time** and **45% fewer output tokens**, but **hidden executable checks 87/90 vs 86/90**. Those checks cover **18 of 39** tasks; the 21 remaining tasks rely on other delivery/LLM completeness signals. Shell execution was **disabled during agent work**, so it cannot stand in for tool-driven debugging/long-run software development. It reports 98% vs 68% for leaving an appropriate test, but among cells that had a test, the injected-bug detection rate was **69% vs 77% baseline**; benefit primarily came from including tests more often. Published standalone findings for ponytail-review/audit are not a validated Combo A/B.

This is **not** evidence that importing Ponytail as an additional Combo Skill saves 26%; Combo already incorporates the philosophy. An independent Cursor comparison linked from its benchmark notes reports some long completion-forced tasks costing more tool effort. For Combo: keep completeness-before-LOC and the actual risk checks.

### 3. Karpathy: good constraints, no individual proof

The single derivative `karpathy-guidelines` advises surface assumptions, minimum complete change, surgical scope and evidence-backed completion. This is in Combo's `POLICY.md` and `context.md`. Its strict question-on-uncertainty advice and hypothetical 200→50-line heuristic are unsuitable as universal instructions. No per-clause current-model A/B was discovered in the inspected source.

### 4. Matt: observed-failure admission policy, not 38 proven outcomes

Matt's [SCOPE.md](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/SCOPE.md) requires an observed real-session failure before admitting a proposed change, and explicitly **freezes misc/**. That is a reasonable curation policy, not a quality lift measurement for each skill. A significant fraction of its engineering skills are **coordinated process components**, with forceful tracker, interview, TDD, review, subagent, or document-writing requirements. Do not interpret being in the repo as a universal best practice for this Combo user.

Its strongest *transferable* mechanisms already appear in Combo: decision triage, requirement-first verification, behavioral test seams, locality/deep modules, primary-source research, and evidence-based retro. In particular, `writing-for-agents` has explicit trigger-branch and completion-criterion thinking; Combo already links it from `productivity.md`. Keep this guidance behind conditional pointers.

### 5. Three small, discriminating gaps were patched

1. **Whole-repository audit vs diff review:** `workflows/review.md` now distinguishes explicit repo-wide audit, maps entry/data/trust flows, prioritizes consequential paths and reports uninspected areas. Reason: Ponytail-audit is genuinely different from a diff review; does **not** add another review skill.
2. **Stuck recovery:** `workflows/debug.md` now records a **compact attempt history only after repeated inconclusive probes**, changes the hypothesis/probe/boundary, and reuses existing project checkpoints. No auto logging middleware, file, hook or new skill. Reason: avoid repeating the same failed reasoning, not a default logging-first program.
3. **Read-only learning:** `workflows/learning.md` no longer offers exercises or finishes with practice regardless of explicit mode. Worked examples remain; retrieval exercises run when requested by the learner, or during an interactive course. Reason: respects stopping point and reduces teaching ceremony.

These are static correctness/intent-alignment patches, **not measured gains**. The baseline was not modified and no new model calls were required.

## Exhaustive source skill ledger (45 skills)

### Karpathy · core (1)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`karpathy-guidelines`](https://github.com/multica-ai/andrej-karpathy-skills/blob/2c606141936f1eeef17fa3043a72095b4765b9c2/skills/karpathy-guidelines/SKILL.md) | `already-covered` | One derivative skill, not Karpathy's own empirical skill evaluation. Assumptions, minimal complete scope and verifiable outcome are already owned by POLICY/context; do not import the rigid 'ask on any unclear detail' or LOC heuristic. |

### Ponytail · core (6)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`ponytail`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail/SKILL.md) | `already-covered` | Ponytail pressure in POLICY and simplicity practice already captures reuse-first and complete causal blast radius. Published 2026-10-07 controlled agentic A/B supports this approach for Opus 5.5, **not** a new Combo-specific gain. |
| [`ponytail-review`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail-review/SKILL.md) | `already-covered` | Existing review evaluates callers, load, risk, test evidence, and surgical remedy. No need for its fixed full report format or another reviewer. |
| [`ponytail-audit`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail-audit/SKILL.md) | `targeted-change` | Distinct from diff review: risk-first whole-repo audit, data/trust flow, expected load, and explicit coverage gaps. Add scope handling in existing review workflow, not another skill. |
| [`ponytail-debt`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail-debt/SKILL.md) | `reference-only` | Grep for code-comment shortcut ceilings and upgrade triggers is useful if this naming scheme is adopted. Existing `.combo/shortcuts` already stores preconditions, evidence, and fallback; avoid a second ledger. |
| [`ponytail-gain`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail-gain/SKILL.md) | `reject-default` | Scoreboard reports *upstream average* benchmark numbers, not local or Combo savings; don't add a runtime reporting skill. |
| [`ponytail-help`](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/skills/ponytail-help/SKILL.md) | `reject-default` | Specific to Ponytail installer, levels, command UX and band; not a Combo capability. |

### Matt · engineering (20)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`ask-matt`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/ask-matt/SKILL.md) | `already-covered` | Routing and phase boundaries already covered. Upstream main flow promotes default grilling, glossary, ticket pipeline and repeated skill transitions; excessive for Combo. |
| [`code-review`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/code-review/SKILL.md) | `already-covered` | Standards-versus-spec split and evidence-backed findings already in review workflow. Do not require two subagents, issue tracker setup or compulsory fixed-point interview. |
| [`codebase-design`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/codebase-design/SKILL.md) | `already-covered` | Deep modules, seam, dependency injection and locality are in design/simplicity. Fixed glossary wording and 'one adapter means hypothetical seam' are heuristics, not universal rules. |
| [`diagnosing-bugs`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/diagnosing-bugs/SKILL.md) | `targeted-change` | Combo already has repro, distinguishing probes and causal repair. Add **conditional compact attempt history on repeated non-discriminating probes**; don't import 'no hypotheses until a runnable repro' hard block. |
| [`domain-modeling`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/domain-modeling/SKILL.md) | `reference-only` | Useful for genuine ambiguous terminology/ADRs; project-knowledge and `.combo/specs` cover ownership. Avoid mandatory GLOSSARY files or repeated edits. |
| [`grill-with-docs`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/grill-with-docs/SKILL.md) | `reject-default` | Two-skill wrapper that invokes relentless interview and glossary editing; use when explicitly requested, not routine development. |
| [`implement-spec`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/implement-spec/SKILL.md) | `reference-only` | Frontier scheduling/worktrees may help large parallel task graphs. Not justified for one-agent or bounded tasks; forced subagent/merger/reviewer fanout increases cost. |
| [`implement`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/implement/SKILL.md) | `already-covered` | Implementation through behavioral seam and verification already in deliver. Do not unconditionally run full suite, code-review or commit. |
| [`improve-codebase-architecture`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/improve-codebase-architecture/SKILL.md) | `reference-only` | Changed-hotspot / deep-module opportunity selection is valuable on request; simplicity already contains hotspot signals. Don't auto-spawn scout, force temporary HTML, or grill after a survey. |
| [`pr`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/pr/SKILL.md) | `reference-only` | Evidence + blast-radius PR body can be borrowed for requested PR authoring. Not a standard extra diagram/door/visual gate. |
| [`prototype`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/prototype/SKILL.md) | `already-covered` | Bounded runnable prototype already conditional in plan/design/context. Avoid mandated HTML UX and prototype branch/commit when outcome doesn't require them. |
| [`research`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/research/SKILL.md) | `already-covered` | Primary-source investigation and optional bounded delegation are already covered. No automatic background worker or Markdown artifact. |
| [`retro`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/retro/SKILL.md) | `already-covered` | Observed-failure environmental improvements covered by `.combo/retro`, project knowledge and PR #4 maintenance. Distinguish mechanical check vs judgment guidance; keep capture conditional. |
| [`setup-matt-pocock-skills`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/setup-matt-pocock-skills/SKILL.md) | `reject-default` | Upstream tracker/labels/glossary bootstrap belongs to Matt ecosystem. Combo must not install or migrate into a competing tracker. |
| [`tdd`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/tdd/SKILL.md) | `already-covered` | Behavior-first red-green and seam catches/misses are in tests practice. Do not force preapproval of every test seam or test-first on tiny changes. Tautological oracle is a candidate if real tests fail. |
| [`to-spec`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/to-spec/SKILL.md) | `already-covered` | Spec synthesis is in plan and `.combo/specs` when opted-in. Avoid exhaustive user-story quotas and automatic tracker publication. |
| [`to-tickets`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/to-tickets/SKILL.md) | `reference-only` | Independent tracer-bullet slices/dependencies are in plan, but native tracker publishing and user quiz are only appropriate on multi-session explicit request. |
| [`triage`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/triage/SKILL.md) | `reference-only` | Role machine and external issue/PR intake can help when existing issue tracker uses these roles. Do not create role labels or triage pipeline for every project. |
| [`wayfinder`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/wayfinder/SKILL.md) | `reference-only` | Destination/decisions/fog mechanism already selectively linked from plan workflow. No mandatory issues, frontier claims or tracker-based decision map. |
| [`wizard`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/wizard/SKILL.md) | `reject-default` | Interactive setup script can write `.env` and GitHub secrets; do not generate/run as an automatic escape hatch. Manual use only with explicit scope, current UI verification and safety review. |

### Matt · in-progress (7)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`chief-of-staff`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/chief-of-staff/SKILL.md) | `reject-default` | Always delegate all work, grow a separate wiki, and consider environment overhaul on each request; conflicts with Combo's bounded delegation and existing `.combo/` ownership. |
| [`claude-handoff`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/claude-handoff/SKILL.md) | `reference-only` | Host-specific background-agent handoff shortcut; use native context controls and existing status/handoff artifacts instead. |
| [`loop-me`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/loop-me/SKILL.md) | `reference-only` | Trigger/checkpoint/workflow vocabulary suits recurring tasks only, not the core coding router or per-task state capture. |
| [`setup-ts-deep-modules`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/setup-ts-deep-modules/SKILL.md) | `reference-only` | Concrete dependency-cruiser boundaries for an explicitly chosen TS architecture. Requires package installs and directory conventions; never apply globally. |
| [`writing-beats`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-beats/SKILL.md) | `reference-only` | Grounding concepts before using them may inform long explanatory writing. Beat-by-beat user gates inappropriate for routine prose. |
| [`writing-fragments`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-fragments/SKILL.md) | `reference-only` | Unstructured ideation with append-only fragments useful only when user requests an iterative writing workspace. |
| [`writing-shape`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-shape/SKILL.md) | `reference-only` | Separate exploration and committed article structure can be useful on explicit co-writing sessions; force-per-paragraph consent is excessive for normal deliverables. |

### Matt · misc (upstream frozen) (4)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`git-guardrails-claude-code`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/git-guardrails-claude-code/SKILL.md) | `reference-only` | Host-only pre-tool safety hook; previous Combo audit notes a Bash-only matcher and jq dependency. Do not auto-install, and it is not a security boundary for every execution path. |
| [`migrate-to-shoehorn`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/migrate-to-shoehorn/SKILL.md) | `reject-default` | Special-purpose third-party TS test fixture library; requires dependency changes and may mask intended type safety. Use only if user explicitly asks and library fits. |
| [`scaffold-exercises`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/scaffold-exercises/SKILL.md) | `reject-default` | Tailored to AI Hero's exercise directory and lint command, not reusable as a Combo-wide teaching procedure. |
| [`setup-pre-commit`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/setup-pre-commit/SKILL.md) | `reference-only` | Concrete Husky/lint-staged steps on explicit request only; never add package managers/hooks/tooling as a mandatory Combo gate. |

### Matt · productivity (7)

| Skill | Decision | Actual mechanism / Combo implication |
| --- | --- | --- |
| [`grill-me`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/grill-me/SKILL.md) | `already-covered` | Thin wrapper around grilling; Combo's decision triage handles consequential questions without perpetual interviews. |
| [`grilling`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/grilling/SKILL.md) | `already-covered` | Frontier/prerequisite-order decision questioning is in context practice. Relentless full-tree interviews should be explicit opt-in. |
| [`handoff`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/handoff/SKILL.md) | `already-covered` | Portable minimal handoff already handled by productivity and project-knowledge; avoid an automatic new document after each session. |
| [`teach`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/teach/SKILL.md) | `targeted-change` | Full course workspace and retention loop intended for sustained teaching; **not** appropriate for a read-only explanation or exam cram. Make Combo learning exercises conditional on requested mode. |
| [`to-questionnaire`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/to-questionnaire/SKILL.md) | `reference-only` | Good principle: ask about the recipient and required response, not unknown domain facts. Already close to productivity/decision triage; retain as reference until a failure shows a gap. |
| [`wait-what`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/wait-what/SKILL.md) | `already-covered` | Explicit request to restate more simply; models and Combo presentation guidance can comply without a new skill. |
| [`writing-for-agents`](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL.md) | `already-covered` | Strong advice on routing pointers, progressive disclosure, completion criteria and pruning. Combo productivity already links it; avoid new always-on instruction text. |

## Other high-leverage areas (ranked; no additional defaults added)

| Rank | Area | Existing evidence | Next action |
| --- | --- | --- | --- |
| P0 | Stop unproductive debugging repetition | Existing `debug.md` loop can repeat unsuccessful probes; user-described failure mode | **Patched conditional attempt history**; test against a captured real failure when available |
| P0 | Read-only vs interactive teaching | Literal `learning.md` finished with unsolicited practice | **Patched**; no model calls needed to observe textual contradiction |
| P1 | Repo audit coverage transparency | `review.md` was a diff-oriented protocol even for whole-repo request | **Patched** with risk-based mapping and explicit unreviewed limits |
| P1 | Project/code architecture hotspots | `simplicity.md` already covers repeated edits, shotgun surgery, duplicated transitions | Do not add survey subagent/HTML report; read affected module via actual recent failures |
| P1 | Unnecessary external reviewers/browser/tool calls | Existing conditional `verification-economy` owner clarified by PR #4 | Keep conditional, measure only failed deliverables; avoid new review pipeline |
| P1 | Memory vs notes vs specs duplication | `.combo/` existing ownership and generated index already opt-in | No new chief-of-staff wiki, tracker, session diary or status format |
| P2 | Tests that are vacuous or tightly coupled to implementation | Matt TDD notes independent oracle and public test seams; Combo covers seams but not explicit tautology wording | Candidate only if real miss found; bare modern models may handle already |
| P2 | Longform editorial grounding | Matt writing-beats/shape distinguish prerequisite concepts from introduced ones | Reference for user-invoked co-writing only |
| P2 | Dependency boundary automation | Matt `setup-ts-deep-modules` can enforce selected TS architecture | Project-specific opt-in, never global dependency install |
| P2 | Domain-specific game/3D skill | Combo has 3D outcome evidence but no full RTS gameplay architecture shelf | Start from concrete RTS/map failures and measured outcomes; not an untested new skill pack |

## Evidence gaps / release safety

- **Not done:** a new live baseline-vs-Combo model comparison, individual Matt/each Ponytail skill A/B, full host installer apply/verify, or a promise of token savings.
- **Not claimed:** upstream freshness equals efficacy; registered source pin equals current API; a static wording improvement equals successful runtime behavior.
- **PR #4 is still draft.** This phase's changes are branched from its exact head so the second PR can target #4 and carry **only** the Phase 4 delta. No direct main writes.
- **Review after merge:** run existing `scripts/sync-context-core.py --check`, `scripts/build-specialists.py --check`, `scripts/build-full-library.py --check`, `node scripts/validate-curated.cjs`, `pytest tests`, and both installer `plan/verify` in real checkouts. Known historical `playwright` environment failure should be reported as such, not attributed to this patch.

## Decision

**No additional installed skills.** The transferable evidence from all three packs supports making the existing paths more context-sensitive, not importing entire pipelines. Three conditional text edits are the only proposed executable guidance changes. A rule stays `behavior-unverified` until task outcomes, not documentation, demonstrate its value.
