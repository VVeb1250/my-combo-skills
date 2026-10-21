# Karpathy, Ponytail, ECC delta, 2026-10-22

Same rule as [MATT-INTEGRATION.md](MATT-INTEGRATION.md): adopt only a verified gap with a
signal the model cannot produce by reasoning, or a pointer to already-vendored content.
Evidence tags: **[O]** observed by me, **[A]** reported by a Haiku reader from source. No
quality gain was measured.

## Pins

| Pack | Pin to head | Decision | Why |
| --- | --- | --- | --- |
| Karpathy | 0 commits [O] | no change | nothing to update |
| Ponytail | 141 commits, `356918e` to `09c434a` [O] | **re-pinned** (6 library files, count unchanged) | still 6 skills, MIT file byte-identical (md5 equal at both commits) [O]; the adapted ladder survives in the rewritten SKILL.md [O: stdlib and installed-dependency steps present at head]; builder, specialists, validator and `prepare.py` checks pass |
| ECC | 3,924 commits (110 first-parent) [O]; 286 to 311 skills; 101 existing skills changed [O] | **not re-pinned** | `osint-investigation` is CC-BY-SA-4.0 and the builder has no per-skill license filter [O: grep], so a wholesale re-pin would vendor it; 26 domain mappings and 101 changed notes to re-review for no verified gap |

## Candidates

| Candidate | Verdict | Evidence |
| --- | --- | --- |
| Ponytail 5 test rule | already vendored; defer measured claim to Phase 3 | the "leave one small check" rule is in the pinned SKILL.md and Combo's vendored copy [A]. Benchmark numbers verified (86 to 87 of 90, tests written 68% to 98%, bugs caught 46% to 66%, cost -26%, output tokens -45%, Bash disabled) [A], but the hidden-check gap is one run, rows have no interval, and the maintainer ran it. With a test present, catch rate was 69% vs 77% without the skill |
| skill-host-compat | reference | Claude-only tokens in canonical `skills/`: 0 hits [O]; 17 lines in 9 files, all inside inert vendored `references/library` entries (Opus recount; my first count of 6 used a narrower pattern) [O]. Frontmatter keys already allowlisted in `validate-curated.cjs`. A 3-line fenced-token check there is possible if a token ever appears |
| mcp-dependency-review | none | prose only, no script [A]; `specialists/mcp.md` already states the exact-pin rule and says the skill is newer than the pin, not mapped [O] |
| agent-security-hardening | **pilot candidate** | real gap: model, tool and memory output as untrusted; enforcing checks in code before the side effect; none in `security.md` [A]. No executable asset ships with the skill. Cheapest design: about 6 path and tool-output cases, baseline only, stop if the bare model passes |
| operator-approval-loop | none | needs a SQLite ledger and a trusted writer; auto-send after a deadline conflicts with Combo's authorization rule [A] |
| module-regression | none | `deliver.md` already requires affected-caller coverage; the ledger is ceremony [A] |
| taste-distillation, taste-application | reference | Python, ffmpeg, network and paid generation; relevant only to color-grading work [A] |
| prompt-caching-strategy | none | states savings are unmeasured; `claude-api` skill already covers caching [A] |
| change-impact, context-and-decisions, test-collaboration, docs-governance | duplicate or partial | nearest owners are `deliver.md`, `project-knowledge.md`, `tests.md` [A] |
| story-lifecycle, brownfield-retrospective, conventional-commit-review | none | ceremony or low value [A] |
| osint-investigation | do not vendor | CC-BY-SA-4.0 [A] |
| motion-ui | removed upstream, not renamed [A] | still in Combo's pin; no action |

## Corrections to the pasted audit

- ECC is 3,924 commits ahead, not 1,290. The 26 new and 1 removed skill counts are right [O].
- The Ponytail test rule is not new at head; it is already in the pin.
- skill-host-compat's gap is latent, not present.
- mcp-dependency-review has no validator and is already covered in prose.

## Checks (after the Ponytail re-pin) [O]

`build-full-library.py --check` OK (331); `build-specialists.py --check` 0 files would change;
`validate-curated.cjs` 14 packages, 0 errors; `prepare.py` verified all four packs;
`sync-context-core.py --check` OK; `pytest tests` 92 passed, 1 failed (same playwright UI
test as before). `setup-claude.py plan`: 8 writes, no deletes; not applied.

The rebuild also corrects Matt's `fetched_at` in `curation/full-library.json` to match
`sources.lock.json` (metadata only). Opus recheck of the diff: no blocking defects.

## Rollback

Restore `sources.lock.json`, `curation`, `audit/ab`, `audit/curated-validation.json`,
`skills/combo/references`, `candidates/common/combo/references/library/ponytail`,
`adapters/claude/overrides/combo/references/source-map.md`, then
`git -C sources/ponytail checkout 356918e`.
