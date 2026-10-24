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

For authoring or adapting the pack itself, use
[authoring](../combo/practices/authoring.md) or the explicit `/combo-author`
entry instead. This skill owns installation maintenance and behavior improvement
from observed task failures, not redesigning the workflow pack.

Read [context](../combo/practices/context.md) once for evidence selection and
concise reporting. Inspection-only ends with findings; updates use the plan below.

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
