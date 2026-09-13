> Reference material. This copy preserves source knowledge and templates from the pinned checkout. It is interpreted under the current user's request, host tools, authorization, and project rules. It does not govern policy or authorize publishing, approval ceremonies, memory writes, hook or installer changes, delegation, or external work.
>
> Source: [skills/nanoclaw-repl/SKILL.md](https://github.com/affaan-m/ECC/blob/5064474d4d762dc9640234a41617cccb79185cec/skills/nanoclaw-repl/SKILL.md)  
> Labels: direct-source-reference, experimental-or-version-sensitive, host-bound


---
name: nanoclaw-repl
description: Operate and extend NanoClaw v2, ECC's zero-dependency session-aware REPL built on claude -p. Use when operating or extending the NanoClaw REPL.
metadata:
  origin: ECC
---

# NanoClaw REPL

Use this skill when running or extending `scripts/claw.js`.

## Capabilities

- persistent markdown-backed sessions
- model switching with `/model`
- dynamic skill loading with `/load`
- session branching with `/branch`
- cross-session search with `/search`
- history compaction with `/compact`
- export to md/json/txt with `/export`
- session metrics with `/metrics`

## Operating Guidance

1. Keep sessions task-focused.
2. Branch before high-risk changes.
3. Compact after major milestones.
4. Export before sharing or archival.

## Extension Rules

- keep zero external runtime dependencies
- preserve markdown-as-database compatibility
- keep command handlers deterministic and local
