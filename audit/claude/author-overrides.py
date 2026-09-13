"""Author the reviewed Claude adapter from the shared Combo source package."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "adapters/claude"
OVERRIDES = ADAPTER / "overrides"
entries = json.loads(
    (ROOT / "evals/ab/variants/entry-manifest.json").read_text(encoding="utf-8")
)["entries"]
for entry in entries:
    name = entry["name"]
    target = entry["target"]
    path = OVERRIDES / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
name: {name}
description: {entry["description"]}
disable-model-invocation: false
user-invocable: true
---

Read the [shared workflow](../combo/{target}) at
`${{CLAUDE_SKILL_DIR}}/../combo/{target}` and complete the requested task
at the user's stopping point. Load only the relevant practices and references.

For Plan Mode, delegation, or context resumption, consult
[Claude execution](../combo/references/claude-code.md).
""",
        encoding="utf-8",
    )

router = (ROOT / "skills/combo/SKILL.md").read_text(encoding="utf-8")
router = router.replace("$combo", "/combo")
router = router.replace(
    "---\n\n# Combo task router",
    "disable-model-invocation: false\nuser-invocable: true\n---\n\n# Combo task router",
    1,
)
router = router.replace(
    "## Boundaries and resumption",
    "## Claude execution\n\nUse the [Claude execution guide](references/claude-code.md) when Plan Mode,\nsubagent delegation, tool boundaries, or compaction matter to the selected path.\n\n## Boundaries and resumption",
)
router = router.replace(
    "in the Codex adapter, not here.", "in the Claude adapter, not here."
)
(OVERRIDES / "combo/SKILL.md").write_text(router, encoding="utf-8")

policy = (
    (ROOT / "POLICY.md")
    .read_text(encoding="utf-8")
    .split("## Combo task routing")[0]
    .rstrip()
)
policy += """

## Combo task routing in Claude Code

For substantive engineering, research, content, learning, business, media, or
productivity work, invoke the matching `combo-*` skill with the Skill tool.
Use `/combo` for uncertain or cross-workflow requests. Choose one primary path
and load its shared workflow, then only the relevant supporting references.
Continue using loaded guidance on follow-ups; simple chat, one-sentence
translation, and tiny understood edits can stay inline. Native tool-specific
skills remain responsible for browser and artifact operations.

Honor the requested stopping point. In normal execution, a request to build
continues through implementation and verification. An active Plan Mode retains
its native read-only and approval boundary. When authorized independent work
benefits from delegation, give `combo-worker` explicit context and file ownership.
The host's configured memory and permission rules remain authoritative.
"""
(ADAPTER / "POLICY.md").write_text(policy, encoding="utf-8")

changed = []
for source in (ROOT / "skills/combo/references").rglob("*.md"):
    body = source.read_text(encoding="utf-8")
    revised = body.replace(
        "Current host rules, user authorization, native tools, and M2D remain authoritative.",
        "Current host rules, user authorization, native tools, and the host's configured memory remain authoritative.",
    )
    revised = revised.replace(
        "Memory is governed by the named M2D authority and does not belong in combo runtime references.",
        "Memory is governed by the host's configured authority; this source does not activate another memory system.",
    )
    if revised != body:
        destination = OVERRIDES / source.relative_to(ROOT / "skills")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(revised, encoding="utf-8")
        changed.append(source.relative_to(ROOT / "skills").as_posix())
print(
    json.dumps(
        {"workflow_entries": len(entries), "memory_navigation_adaptations": changed}
    )
)
