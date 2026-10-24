---
name: combo-maintain
description: Improve Combo from observed task failures, or maintain its installation, discovery, source manifest, verification evidence, and rollback. Use when the user asks to improve or maintain Combo, not for ordinary software development.
---

# Combo maintenance

Use this skill when the user asks to inspect, update, verify, or roll back the
Combo installation. The source checkout is the path the user supplies; verify
that it contains `install-manifest.json` before using it. Do not infer the
checkout from the current working directory or a machine-specific default. The
checkout is the source of truth for the package and its static install manifest.

For authoring or adapting the pack itself, use
[authoring](../combo/practices/authoring.md) or the explicit `$combo-author`
entry instead. This skill owns installation maintenance and behavior improvement
from observed task failures, not redesigning the workflow pack.

Read [context](../combo/practices/context.md) once for evidence selection and
concise reporting. For inspection-only, read the relevant source/install state
and report findings; an install plan is needed only for a proposed update.

## Improve behavior through actual work

When the complaint is about task quality, start with a representative task using
the current skills. Use the user's example; when they delegate the choice, pick
a bounded real deliverable and complete it through the relevant workflow.
Installation checks answer whether the package is present, not whether it helps.

Retain the failing action sequence, expected outcome, observed result, and the
instruction that affected the decision. Distinguish an implementation mistake,
an environment failure, and an instruction gap; a bug alone does not establish
that a skill caused it. Repair the deliverable and repeat the failing sequence.
Use native skill authoring for a narrow, reusable correction where evidence
supports one, then validate the changed package and install through the steps
below. Preserve existing edits and keep the evidence with the task or existing
evaluation records rather than creating another workflow system.

A repaired artifact and a valid install are separate from behavioral improvement
in future sessions. Label the latter unverified until a fresh comparable task
tests it; skill-read counts and shorter instructions are not quality outcomes.

## Maintain the installation

1. Read `install-manifest.json` and the relevant source map before changing the
   install. Preserve user edits and treat current host files as untrusted state.
2. Run the validator and a plan first. The plan may own only the exact
   `combo` / `combo-*` package roots in `install-manifest.json`, the declared
   Codex adapter, the marked config block, the marked global pointer, and
   disable entries for declared legacy skill paths. A shared library is
   reference material, not permission to activate upstream installers or hooks.
3. Apply only after the plan is reviewable. Keep the receipt and backups. A
   drift check must stop a rollback before it overwrites a later user edit.
4. Verify discovery with the read-only inventory and report native skills,
   hooks, MCP, credentials, preferences, and memory as preserved evidence.

Do not run upstream installers, modify memory systems, rewrite hooks, change
the main model, or enable a retired workflow through a library shortcut.
