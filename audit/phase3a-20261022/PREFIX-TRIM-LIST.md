# Prefix trim list for this project, 2026-10-22

**Applied afterwards (owner approved):** the claude.ai connectors GitHub, Gmail and Google Drive were switched off by default (88 tools gone from the session, ~1.8K prefix tokens). Everything else below is still only a list.
Original note: when written, no settings, plugin, connector or skill had been changed. Sources: `prefix_inventory.py` (sizes from this session's first-call
attachments, chars/4 [E]; usage from this project's 43 transcripts incl. subagents) plus a count over all 35 real Claude project folders under
`~/.claude/projects` (harness temp folders excluded). Counts cover Claude Code only, not Codex, and only calls the model made.

## What this can and cannot buy
The prefix is ~91-104K tokens at every first call (23% of these sessions' Sonnet spend). The pieces below are the **trimmable** part, about 13K tokens at most (tier A 4.0K + tier B 3.0K + unused skills 5.7K + plugin leftovers).
The rest is host-owned: tool schemas ~33K (the Artifact tool alone ~9K), system prompt ~8K, `CLAUDE.md` ~3K, hook output ~3K, first message.
Rule of thumb from the audit: **1K prefix tokens = $0.09 over the 7 audited sessions = 0.17% of spend**, so tier A is about 0.7%, A+B+safe skills about 1.5%. This is hygiene, not a big cut.

## Tier A - zero calls in every project (safest)
| Item | Kind | Prefix tokens | Calls (this / all projects) | Note |
| --- | --- | ---: | --- | --- |
| `computer-use` | desktop MCP | 1,489 | 0 / 0 | largest single item; instructions block is most of it |
| `20dba7f1...` (GitHub connector, 45 tools) | claude.ai connector | 1,136 | 0 / 0 | duplicate of the local `github` MCP, which was used 29 times |
| `27628447...` (Gmail, 32 tools) | connector | 465 | 0 / 0 | |
| `PDF_Tools` (43 tools) | MCP | 351 | 0 / 0 | |
| `Desktop_Commander` (26 tools) | MCP | 258 | 0 / 0 | |
| `5b9d0f53...` (Drive, 11 tools) | connector | 159 | 0 / 0 | |
| `scheduled-tasks`, `9ce924e4...` | MCP / connector | 108 | 0 / 0 | |
| **Tier A total** | | **~3,970** | | |

## Tier B - used in other projects, unused here (per-project only)
| Item | Prefix tokens | Calls (this / all) | Note |
| --- | ---: | --- | --- |
| `Blender` (26 tools) | 1,322 | 0 / 17 | used in the guild-master/chibi project; keep there |
| `7cf8bc23...` (Atlassian, 41 tools) | 682 | 0 / 3 | |
| `1a59c906...` (Claude Docs) | 540 | 0 / 453 | heavily used elsewhere; do not touch globally |
| `claude-in-chrome` (22 tools) | 461 | 0 / 67 | Combo's e2e practice prefers the built-in browser; keep unless you never use it |
| **Tier B total** | **~3,005** | | |

Keep regardless: built-in `Claude_Browser`, `ccd_*` host servers, `visualize`, `terminal`, `codegraph`, `playwright`, `fetch`, `github` (local), `context7`, `exa`, `mcp-registry`.

## Plugins and skills
- `engineering` plugin: 10 skills + 9 of the 10 "needs authentication" servers (asana, atlassian, datadog, github, linear, notion, pagerduty, slack...), 0 calls anywhere, ~0.3K tokens. `design` plugin: used 8 times elsewhere; keep.
- Of the 102 listed skills, 85 had no call in any project (5.7K tokens). Largest: `dataviz` 362, `anthropic-skills:docs` 257, `code-review` 248, `anthropic-skills:pptx` 246, `:google-workspace` 244, `:computer-use` 242, `:docx` 240.
  **Do not trim blindly:** the host prompt tells the model to read `anthropic-skills:built-in-browser`, `:chrome-browser`, `:computer-use`, `:docs`, `:google-workspace` and `dataviz` before certain actions, so
  switching those off can break an instruction. Safer candidates: `microsoft-foundry` 126, `codegraph-affected` 121, `codegraph-link` 96, `find-skills` 94, `whip-design` 90, `whip-ui` 88,
  `git-guardrails-claude-code` 68, `setup-pre-commit` 64, `anthropic-skills:mcp-builder` 77, `:morning` 92, `:idea-generator-critic` 165, `:debug-by-logging` 129, `:delegated-code-writer` 126 (the last three are yours; check you do not want them).
- **Combo's own 14 skill entries cost 721 tokens** and the policy block ~740; keep both. Nine of the 14 entries show no model-launched `Skill` call in Claude Code (Codex use is not counted), which is routing, not a trim signal.
- Already off or disabled: `multi-model-orchestrator` (skillOverrides), plugins `ecc`, `ecc-hubs`, `mattpocock-skills`, `claude-mem`. Seven LSP plugins are enabled (gopls, typescript, csharp, clangd, pyright, jdtls, rust-analyzer); their prefix cost was not separable in these logs.

## How it could be applied (not done; verify before use)
`enabledPlugins` and `skillOverrides` already exist in `~/.claude/settings.json`, so per-plugin and per-skill switches are known to work at user scope; whether a project-level `.claude/settings.json`
overrides them was not tested. Claude.ai connectors are toggled in the app (a `set_session_connector_enabled` tool also exists for the current session). The saving appears only for new sessions.
Re-measure with `py -I prefix_share.py` after a change; the first-call context should drop by about the tokens above.
