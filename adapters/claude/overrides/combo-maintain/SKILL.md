---
name: combo-maintain
description: Inspect, update, verify, or roll back the Combo installation for Claude Code, including source provenance and skill discovery. Use for package maintenance, not ordinary task execution.
disable-model-invocation: false
user-invocable: true
---

# Combo maintenance for Claude Code

The source checkout is the path the user supplies. Confirm it contains
`adapters/claude/install-manifest.json` and `scripts/setup-claude.py`; do not
infer the checkout from the current working directory or a machine-specific
default. Runtime workflows need only their installed package; this checkout is
needed for package maintenance.

For new workflows, entries, practices, host adapters, or structural pack
redesign, use explicit `/combo-author`. For observed failures or successes in
existing Combo behavior, this skill may fix an existing canonical rule without
creating a competing owner. Read the shared
[maintenance contract](../combo/practices/maintenance.md), also used by Codex.

Read [context](../combo/practices/context.md) only for unresolved evidence
selection or reporting mechanics; task workflows embed the context core. Inspection-only ends with findings; updates use the plan below.

Read the Claude manifest, inspect relevant changes, and run
`py scripts/setup-claude.py plan` before applying an update. A reviewable plan
plus the user's existing setup/update request authorizes that scoped work.
Use `apply`, then `verify`; keep the generated receipt and backups.

The installer owns only declared Combo skill files, `agents/combo-worker.md`,
the marked Combo policy, and the exact retired-plugin/skill visibility keys.
Preserve the host's model, effort, permissions, hooks, credentials, memory,
and unrelated plugins. Updating pinned source references does not activate
their installers or competing memory systems.

Rollback uses `py scripts/setup-claude.py rollback --receipt <receipt.json>`.
Stop on detected drift rather than overwriting a later user edit. Validate
actual Claude discovery and relevant behavior before reporting success.
