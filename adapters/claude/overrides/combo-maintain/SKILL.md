---
name: combo-maintain
description: Improve Combo from observed task failures, or inspect, update, verify, and roll back its Claude Code installation. Use for Combo quality or package maintenance, not ordinary execution.
disable-model-invocation: false
user-invocable: true
---

# Combo maintenance for Claude Code

Apply the shared [maintenance contract](../combo/practices/maintenance.md)
for behavioral improvement, evidence standards, rule ownership, and
proportionate validation. It is the same contract used by the Codex entry.
For unresolved context-selection or reporting mechanics, consult
[context](../combo/practices/context.md); its outcome rules already live in
the workflows.

Locate the source checkout from an explicitly configured or supplied path.
Confirm `adapters/claude/install-manifest.json` and
`scripts/setup-claude.py` exist before any install operation. The runtime
only needs the installed package; do not assume the checkout is on a
particular drive or silently use an unrelated working directory.
Inspection-only work can end with findings.

## Claude Code installation procedure

1. Read the Claude manifest and relevant source mappings; inspect changes
   and run `py scripts/setup-claude.py plan` before a proposed update.
2. Review the plan, preserving all non-Combo host state. An existing authorized
   setup/update request covers only its stated scope.
3. When authorized, run `py scripts/setup-claude.py apply`, then
   `py scripts/setup-claude.py verify`; retain its backups and receipt.
   Roll back with `py scripts/setup-claude.py rollback --receipt <receipt.json>`
   only when drift checks permit.
4. Validate actual Claude skill discovery and applicable checks, reporting
   behavioral improvement as unverified unless separately observed.

The installer owns only declared Combo skill files, its worker adapter,
marked policy, and exact retired-plugin/skill visibility keys. Preserve
the host's model, effort, permissions, hooks, credentials, memory,
unrelated plugins, and native skills. Pinned source references do not
authorize external installers or competing memory systems.
