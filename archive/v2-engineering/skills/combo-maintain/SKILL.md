---
name: combo-maintain
description: Maintain the installed Combo package, its discovery state, source manifest, adapter role, verification evidence, or drift aware rollback. Use for Combo installation and maintenance tasks, not ordinary software development.
---

# Combo maintenance

Use this skill when the user asks to inspect, update, verify, or roll back the
Combo installation. The configured source checkout is
`D:/0_person-project/my-combo-skills`; verify that it exists and contains
`install-manifest.json` before using it. If it moved, use an explicitly supplied
checkout path rather than inferring the current working directory. The checkout
is the source of truth for the package and its static install manifest.

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
