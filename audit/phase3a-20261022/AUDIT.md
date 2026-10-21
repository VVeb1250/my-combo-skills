# Phase 3A offline cost audit, 2026-10-22

No model calls for the numbers below (scripts in this folder; Haiku 5.5 used only for the blind labelling pass, ~$0.05).
No Combo file was edited. Tags: **[O]** observed, **[I]** inferred. Reproduce: `py -I audit_real_sessions.py --exclude <this session>`,
`audit_codex_compaction.py`, `state_file_reads.py`.

## 1. Where the money goes

**Harness runs (Phase 1-2, already priced):** $0.124 per task at `claude-sonnet-5-5`; the turn-1 prefix write is $0.076 of it (61%);
a workflow load is $0.0105 (8.5%); inlining the workflow saves nothing; moving the core rules into the workflows cost +$0.0025 [O]
(`../phase2-20261021/cost*/RESULTS.md`, `context-move/RESULTS.md`). Those tasks are 3-16 calls at ceiling, so they cannot show real-session cost.

**Real Claude sessions, 7 transcripts + 29 subagents of this repo's Combo work** [O], $44.40 priced + advisor:

| Bucket | $ | Share | Reading |
| --- | ---: | ---: | --- |
| Context re-read (cache read) | 23.17 | 52% | structural: context length x turns |
| Cache write | 13.19 | 30% | prefix + new tool results |
| Output | 8.04 | 18% | |
| Advisor (Opus 5.5), 9 calls | 9.06 | +20% on top | mean 212K input tokens per call, no cache fields [I: billed uncached at list]; ~$1 per call, grows with transcript length at call time. The user's chosen setup, not a cut |
| Tool-result carried cost [E] | Bash 4.42, Read 1.07, PowerShell 0.50, Grep 0.34 | Bash 10% | 768 Bash calls x ~820 tokens each, re-read on every later turn |
| Subagents | 2.11 | 5% | $1.60 is two deliberate Opus rechecks; 14 Haiku/combo-worker readers cost $0.28; 254 Haiku turns cost $0.52 in total |

Waste signals are tiny [O]: 1 repeated command, 0 repeated reads, 1 unexplained cache-write spike ($0.00), 2 compactions in 7 sessions.
Cost here is structural (long context re-read every turn) rather than avoidable duplicates. Opus/Haiku prices apply the Sonnet fit's structure
(write 2x, read 0.05x input) to the skill's list prices [I]; the skill text gives $0.20 for Sonnet cache reads, which the fit contradicts ($0.10).

## 2. Compaction (the new P0)

**Codex has it, Claude barely does** [O]: 32 compactions in 10 of 42 Codex rollouts (a rollout with compaction runs ~300-800 calls);
context drops from a mean 251K to 47K tokens. Docs: Codex keeps the most recent user messages under a 20K-token budget
(mean 12.6 kept), so what is lost is assistant-side state: verified results, failed attempts, decisions it reached itself.

| Instrument (10 calls after a compaction vs the next 10) | After | Control | Reading |
| --- | ---: | ---: | --- |
| Exact command repeats | 4/320 | 4/305 | none |
| Re-reads of an unedited file read before the cut | 30% | 25% | within noise |
| Project-instruction reloads (CLAUDE/AGENTS/SKILL) | 14% | 12% | within noise |
| **Calls touching a project state file (STATUS.md, plan/handoff docs)** | **13.8%** | **4.9%** | **~3x; 8 of 10 rollouts use one** |
| Haiku blind labels (redo / contradicted / re-asked / user correction) | 6/32 | 3/23 | all 6 post flags checked by hand: ordinary design feedback, 0 continuity failures; control flags not checked |

**Reading [I]:** no confirmed instance of post-compaction rework in 32 compactions, with instruments that mostly see recent, retained
context; the hypothesis is neither confirmed nor refuted. The one clear behaviour is that agents already recover through a project status
file, which `practices/project-knowledge.md` ("update the existing task or checkpoint") already points at. A new `.combowork/` tree is not
justified by this data; the open design question is when to create/update that file and what goes in it.

**Existing mechanisms the design must not duplicate:** Codex hooks `context-mode` PreCompact/SessionStart and `mb-recall` at SessionStart;
Codex config `model_auto_compact_token_limit` (forces compaction) and `experimental_compact_prompt_file` (custom compact prompt: a host-native
arm with no files) [docs via context7, `/openai/codex`]. Whether context-mode restores state after a compaction is not visible in the rollouts (open).

**Pilot outcome (arm A only):** see [PILOT-RESULTS.md](PILOT-RESULTS.md). Six forced-compaction sessions, 5 compacted (2 mid-step 2), all recovered with no redo and
no decision flip; the pre-registered stop rule says failure not demonstrated, so arms B and C were not run. The fixture is small and test-checked, a weak proxy for the user's long untested work.

**Real sessions read by hand (owner-chosen rollouts 2026-10-16 09:16, 10-19 05:21, 10-16 00:02; 19 compactions, 1,511 calls; Blender MCP setup, hair/face asset iteration, VRoid sampling):**
17 of 19 cuts resumed cleanly: same goal, constraints and the user's earlier corrections carried over (e.g. "skip the catalog test" survived a cut). Two failures, one of each kind:
1. *Re-exploration* (10-16 09:16, cut 1, CLI-heavy setup): after the cut the agent re-ran `--help` discovery and repeated a repository-add it had already completed (about 5-6 of the
   next 12 calls). Lost state = assistant-side tool knowledge; that setup flow had no `STATUS.md` entry, while the later asset work did. Cost: about six calls.
2. *Retained instruction not followed* (10-19 05:21, cut 6): the user had said earlier that the old generator was AI-only and to start by decomposing VRoid samples. Verified in the
   compaction record that **all 12 earlier user messages, including that one, were retained**, yet the first post-cut plan extended the project's existing generator and used VRoid only for
   classification; the user then wrote that the agent "forgot context I typed earlier". So the failure was salience (the agent followed its own plan/summary), not missing text. Whether it
   would have happened without a compaction is untested (no control).
Detectors: near-duplicate calls were higher after cuts (40% vs 20% in the 10-19 rollout) but the high cases are repeating export loops, not rework; a scan for Thai/English "you forgot / I already said"
cues found 1 hit in 56 post-cut user messages (the case above) and none elsewhere. The exact-repeat detector saw neither failure.

## 3. Ranking for Phase 3A (waste found, not savings promised)

1. **P0 continuity** - two real failures in 19 cuts (re-exploration; a retained instruction not followed); a quality fix, not a cost cut. Draft rules: `PROPOSED-RULES.diff`.
2. **Tool-call economy** - measured, small (`tool_output_offenders.py`): 800 shell calls, mean 819 tokens, carried $5.13 (11.6% of spend). Only 88 results are >= 2,000 tokens
   (carried $2.03, 4.6% of spend) and 68 of those commands were already bounded (head/tail/-n/-First); no command class is above 10% of the shell cost. Halving every large result saves about $1 (2%).
3. **Fixed prefix** - `prefix_share.py`: 91K-104K tokens at the first call in every session (the one resumed session at 662K excluded), paid once as a cache write and re-read every turn:
   $8.03 of $34.75 (23%) of those sessions' Sonnet spend. Rough make-up (chars/4 [E]): tool schemas ~33K (the Artifact tool alone ~9K), system prompt ~8K, deferred-tool names ~9K,
   skill listing ~8.7K, MCP instructions ~4.3K, CLAUDE.md ~3.2K, hook output ~3K, first message ~4.8K. Combo's own share (14 skill entries + the ~740-token policy) is about 1.6K tokens,
   ~1.5% of the prefix, ~0.4% of spend. Every 10K tokens trimmed from the prefix saves about $0.9 over these sessions, ~2% of spend; the levers are owner-side (unused MCP servers, plugins, skills), not Combo files.
4. **Advisor timing** - 9 calls at a mean 212K input tokens, ~$1 each, +20% on top; a call made at half the context costs about half. Owner decision, not a Combo rule.
5. Shortcut/avoided work, deterministic scripts - no measured waste in these logs (repeats ~0); keep as policy, do not tune.
6. Output/Caveman - output is 18% of spend and already terse in these sessions; lowest.

**Phase 3A reading [I]:** no single Combo-controllable lever in these logs is above ~2% of spend. Cost is structural (a 100K-token prefix and a growing history re-read every turn, so turn count x context size),
and the largest single items are host/owner choices (advisor, prefix make-up, session length). Further Combo instruction edits for token cost are not supported by this evidence.

## 4. Outcome and status (closed 2026-10-22)
- **Rules applied** (owner-approved): the two sentences in `PROPOSED-RULES.diff` are in `practices/context.md` (core, so copied into all 12 workflows by `sync-context-core.py`) and
  `practices/project-knowledge.md`. Tests: 93 run, 1 failure, the known `playwright` module one in `test_outcome_eval`; `sync-context-core.py --check` OK.
  Installed into Claude (receipt `backups/claude-20261021-215540-087400/receipt.json`, `verify` clean). Installed into Codex too, on the owner's go-ahead: 83 files (the 14 rule files plus
  the Matt/Ponytail re-pin that had never reached Codex: 61 writes, 7 deletes under `references/library`), receipt `backups/20261021-215816-061900/receipt.json`, `verify` clean,
  the `[memories]` config untouched.
- **Connectors**: GitHub (claude.ai), Gmail and Google Drive turned off by default (88 tools removed from the session; they stay connected and can be re-enabled per session). Nothing else in
  `PREFIX-TRIM-LIST.md` was applied.
- **Not measured**: whether the continuity rule reduces re-exploration or ignored instructions (1 instance of each in 19 cuts); no further token-cut edits to Combo are supported by this data.
- **Open**: Bash output and advisor timing are owner-side choices; whether `context-mode` restores state after a Codex compaction is unknown.

## 5. Limits
Real logs carry no acceptance result, so this ranks waste, not cost per successful task. The sample is Combo-development sessions
(skewed to launching evals); harness subprocess spend lives in `evals/compare/results`. Codex logs have no price attached. The Haiku pass
saw a 10-call window plus recent messages, so it cannot see state compaction dropped. `n` is 32 compactions in 10 rollouts.
