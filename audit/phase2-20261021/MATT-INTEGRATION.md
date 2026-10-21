# Matt Pocock skills integration, 2026-10-22

Scope: bring Combo's Matt material from upstream `3cca18b` to `5beb35b` and decide which
newer Matt skills earn a place in active workflows. Rule: Phase 2 decision rule
([audit section 5](PHASE2-CAPABILITY-AUDIT.md)). Evidence tags: **[O]** observed by me,
**[A]** reported by a Haiku reader from source (five readers, spot-checked where a decision
depended on them), **[I]** inference. Nothing here is a measured quality gain.

## What changed

| Change | Where | Evidence |
| --- | --- | --- |
| Pin `matt` 3cca18b to 5beb35b | `sources.lock.json`, `curation/specialists.json` (6 ADAPT rows), generated `source-map.md` (+ Claude override copy) | the six owner files need no edit [A, checked in `tests.md:9`, `debug.md:35`, `review.md` conventions step and its conditional-reviewers line]: tdd and diagnosing-bugs changes are already present, code-review's added fanout is deliberately not adopted, ask-matt and codebase-design changes are routing or rename only |
| Library rebuilt through `scripts/build-full-library.py`; `EXPECTED_COUNTS.matt` 37 to 38 | `references/library/matt/**`, domain indexes, Claude override indexes | entries 330 to 331 (+pr, +chief-of-staff, -resolving-merge-conflicts) [O]; no other pack's file changed [O] |
| Path drift fixed | `retro` and `implement-spec` now under `engineering/`; `CONTEXT-FORMAT.md` is `GLOSSARY-FORMAT.md` | upstream rename [O] |
| One pointer sentence | `workflows/productivity.md`, agent-facing writing line, to `writing-for-agents/REFERENCE.md` | makes vendored content reachable; no new text copied |
| One pointer paragraph | `workflows/plan.md`, after the bounded-plan paragraph, to `wayfinder/REFERENCE.md` | owner chose the concept without the tracker mechanics; unmeasured prose, so it is a pointer plus a scope limit, not a gate |

The builder and validator also regenerated `audit/ab/source-coverage.*` and
`audit/curated-validation.json`; those pick up unrelated drift (workflow and practice counts,
entry description lengths), not Matt content.

Library loss to note: `resolving-merge-conflicts` was deleted upstream, so it left the pinned
library. Nothing in a workflow routed to it [A]; `git` history keeps the old copy.

## Verdict per candidate

| Skill | Verdict | Why |
| --- | --- | --- |
| retro | reference | disable-model-invocation upstream; its suggestions lean toward hooks, CI jobs, AGENTS.md edits; no failure record shows a gap [A] |
| wayfinder | pointer added to `plan.md` (owner decision 2026-10-22): idea only (destination, decisions not deliverables, decisions index, fog vs ticket); tracker, label, claim and subagent mechanics only for parallel sessions with authorization. No evidence that the tracker form beats a one-file form | tracker map, forced grilling, forced research subagents, branch pushes [O: lines 79, 115] |
| wizard | reference | `template.sh` writes plaintext `.env` (mode 0600) with no `.gitignore` check; agent must not run it [O: `write_env`, lines 140-151] |
| pr | reference | useful part (before/after test evidence) already follows `deliver.md` mapping; door classification is reasoning the model does unaided [A] |
| implement-spec | reject as default | mandatory implementer subagents and worktrees; draft PR when the tracker closes work through PRs or the user asks [O] |
| chief-of-staff | reject | "All work should be done in subagents" [O: line 20]; in-progress upstream |
| grilling, grill-me | reject as default | decision triage in `context.md` already covers the useful part; rest is a mandatory interview [A] |
| writing-fragments, shape, beats | reference | per-block user gates conflict with decision triage; in-progress upstream [A] |
| writing-for-agents | pointer added | techniques not in `productivity.md`, content already vendored |
| teach | owner decision | learner-progress state has no home today (Memory Base lessons are not learner progress) [A] |
| to-questionnaire | owner decision | `combo-productivity` description names questionnaires; method not in the workflow [O] |
| handoff, claude-handoff, loop-me, wait-what | none | covered by `productivity.md` or host-native, or out of scope [A] |
| git-guardrails-claude-code | already installed at user level (script matches upstream) | not wired in `settings.json`; fails open without `jq`; Bash matcher only, so blind to PowerShell [A]. Not touched |
| setup-ts-deep-modules | reference | user-invoked, TypeScript-only |

## Corrections to the pasted audit

- "Missing `template.sh`, `block-dangerous-git.sh`, `dependency-cruiser.config.cjs`" is builder
  policy, not a defect: the library excludes scripts and links them by commit
  (`build-full-library.py` `EXCLUDED_DIRS`) [O].
- The guardrails skill is already installed with its script [A].
- Its next step (pilot retro, wayfinder, wizard) conflicts with the evidence above.

## Checks run (after the edits) [O]

`build-full-library.py --check` OK (331 entries); `build-specialists.py --check` 0 files would
change; `validate-curated.cjs` 14 packages, 0 errors; `sync-context-core.py --check` OK;
`pytest tests` 92 passed, 1 failed (the playwright-missing UI journey test, failing before
this work). `setup-claude.py plan` reports 57 changed files (53 writes, 4 deletes of the old
`CONTEXT-FORMAT`, `resolving-merge-conflicts`, `in-progress/implement-spec`, `in-progress/retro`
installed copies); `apply` re-plans from source, so the plan file is not an input. **Not applied.** Codex install
not run.

## Rollback

Restore the tracked paths this work touched, not the whole tree:
`git checkout -- sources.lock.json curation scripts/build-full-library.py README.md DESIGN.md
audit/ab audit/curated-validation.json skills/combo/references skills/combo/workflows/productivity.md
candidates/common/combo/references/library adapters/claude/overrides/combo/references`.
Then remove the new untracked `matt` library folders (`pr`, `retro`, `implement-spec`,
`chief-of-staff`, `GLOSSARY-FORMAT.md`; review `git clean -n` first) and run
`git -C sources/matt checkout 3cca18b`.
