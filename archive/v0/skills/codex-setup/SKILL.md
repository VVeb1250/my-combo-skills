---
name: codex-setup
description: Audit or maintain this Codex installation's skills, discovery, plugins, configuration, and context cost. Use when setup is broken, skills duplicate or fail to trigger, or the user asks to renovate the install. จัดการ setup Codex. Skip ordinary application development.
---

# Maintain the installed combo

Read the current config and actual skill discovery before editing. Codex can
discover user `.codex/skills`, `.agents/skills`, repository skills, and enabled
plugin skills; moving one directory alone does not hide the others.

The maintained source and executable curation manifest are in
`D:/0_person-project/my-combo-skills`. Start with its README and manifest rather
than old parked-skill counts. `scripts/codex_inventory.py` uses read-only
app-server discovery without starting a model turn.

Compare discovery with intended ownership. Use Codex `[[skills.config]]` by path
for local visibility and plugin enablement for a whole plugin. Preserve unrelated
MCP, hook, credential, preference, and memory settings. Take a backup and provide
drift-aware rollback before changing global files.

Treat descriptions as discovery signals. Count actual invocations and user
corrections separately from schema validation and listing size. Do not claim
all-model reliability from a successful install or a few smoke checks.
