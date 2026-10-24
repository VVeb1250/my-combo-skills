---
name: combo-author
description: >
  Author or customize a Combo-like workflow pack: add or revise workflows, practices, entries, templates, or host adapters; adapt Combo to another host; or design a smaller system from the same principles. Use only on explicit request; not for ordinary task execution.
---

# Combo authoring

Read [authoring](../combo/practices/authoring.md) and follow it. This is an
explicit-only system entry: use it when the user asks to customize this Combo
pack, adapt it to another host, or build a Combo-like system from scratch.
It is not a task workflow and does not authorize ordinary implementation,
review, or verification work.

For installation update, verification, or rollback of an existing install, use
[combo-maintain](../combo-maintain/SKILL.md) instead.

Work in a source checkout when possible. Installed-package edits are not durable
across updates. Keep workflow, practice, and reference bodies host-neutral; put
host-specific entrypoints and invocation policy in the adapter.
