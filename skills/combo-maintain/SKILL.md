---
name: combo-maintain
description: Improve Combo from observed task failures, or maintain its installation, discovery, source manifest, verification evidence, and rollback. Use when the user asks to improve or maintain Combo, not for ordinary software development.
---

# Combo maintenance for Codex

Apply the shared [maintenance contract](../combo/practices/maintenance.md) for
behavioral improvement, evidence standards, rule ownership, and proportionate
validation. It is the same contract used by the Claude Code adapter. For
unresolved context-selection or reporting mechanics, consult
[context](../combo/practices/context.md); its outcome rules already live in
the workflows.

Locate the source checkout from an explicitly configured or supplied path.
Confirm `install-manifest.json` and `scripts/setup.py` exist before any
install operation. An installed skill directory is not automatically the
source checkout. Do not assume an OS-specific drive letter or an unrelated
working directory. Inspection-only work can end with findings.

## Codex installation procedure

1. Read `install-manifest.json` and the relevant source map. Run the existing
   static validator and `py scripts/setup.py plan` before a proposed update.
2. Review the plan and apply only changes within declared Combo package roots,
   the declared Codex worker adapter, exact managed config markers, and
   declared legacy skill visibility entries. Preserve unrelated user edits.
3. When the update is authorized, run `py scripts/setup.py apply`, then
   `py scripts/setup.py verify`; retain its backups and transaction receipt.
   Stop rollback on drift instead of overwriting later user changes.
4. Verify actual discovery and report the relevant check outcome. Do not
   present a clean installation as proof of behavioral improvement.

Do not run upstream installers or change the main model, memory, hooks,
credentials, permissions, or unrelated host settings through a source-library
reference.
