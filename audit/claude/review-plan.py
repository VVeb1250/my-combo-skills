"""Review only the allowed Claude changes without emitting private settings."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "claude_setup", ROOT / "scripts/setup-claude.py"
)
assert spec is not None and spec.loader is not None
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
manifest = setup.load_manifest()
home = Path.home()
changes = setup.build_plan(home, manifest)
root = home / ".claude"
relative = [row["path"].relative_to(root).as_posix() for row in changes]
assert all(
    path.startswith("skills/combo")
    or path in {"settings.json", "CLAUDE.md", "agents/combo-worker.md"}
    for path in relative
)
policy = next(row for row in changes if row["path"].name == "CLAUDE.md")
assert setup.outside_owned_policy(
    policy["before"], manifest
) == setup.outside_owned_policy(policy["after"], manifest)
settings = next(row for row in changes if row["path"].name == "settings.json")
before = json.loads(settings["before"])
after = json.loads(settings["after"])
for plugin in setup.DISABLE_PLUGINS:
    assert after["enabledPlugins"][plugin] is False
    after["enabledPlugins"][plugin] = before["enabledPlugins"][plugin]
after["skillOverrides"].pop("multi-model-orchestrator")
if not after["skillOverrides"] and "skillOverrides" not in before:
    after.pop("skillOverrides")
assert before == after
result = {
    "changed_paths": len(changes),
    "entries": sorted(
        path.split("/")[1] for path in relative if path.endswith("/SKILL.md")
    ),
    "outside_policy_identical": True,
    "unowned_settings_identical": True,
    "disabled_plugins": list(setup.DISABLE_PLUGINS),
    "skill_overrides": setup.SKILL_OVERRIDES,
    "main_model": before.get("model"),
    "effort": before.get("effortLevel"),
    "target": str(root),
}
(ROOT / "audit/claude/plan-review.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps(result))
