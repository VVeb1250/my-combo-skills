---
name: combo-author
description: Author or customize a Combo-like workflow pack for Claude Code, including entries, practices, host adapters, and installer changes. Use only when the user explicitly invokes /combo-author for customization or from-scratch authoring; not for ordinary task execution.
disable-model-invocation: true
user-invocable: true
---

# Combo authoring for Claude Code

Read the [shared authoring practice](../combo/practices/authoring.md) at
`${CLAUDE_SKILL_DIR}/../combo/practices/authoring.md` and follow it. This is an
explicit-only system entry; do not use it for ordinary task work.

For installation update, verification, or rollback, use
[combo-maintain](../combo-maintain/SKILL.md) instead.

Work in a source checkout when possible. Keep shared bodies host-neutral and put
Claude-specific frontmatter, `${CLAUDE_SKILL_DIR}` paths, invocation policy,
settings, and worker configuration in the adapter.
