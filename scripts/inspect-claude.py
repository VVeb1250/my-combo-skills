"""Read Claude configuration structure without exposing credentials or env values."""

import json
from pathlib import Path

home = Path.home() / ".claude"
settings = json.loads((home / "settings.json").read_text(encoding="utf-8-sig"))
report = {
    "settings_keys": sorted(settings),
    "model": settings.get("model"),
    "effortLevel": settings.get("effortLevel"),
    "enabledPlugins": settings.get("enabledPlugins", {}),
    "env_keys": sorted(settings.get("env", {})),
    "hook_event_counts": {k: len(v) for k, v in settings.get("hooks", {}).items()},
    "skills": [],
    "commands": [],
    "agents": [],
}
for kind in ("skills", "commands", "agents"):
    folder = home / kind
    if not folder.exists():
        continue
    for path in sorted(folder.iterdir()):
        row = {
            "name": path.name,
            "symlink": path.is_symlink(),
            "junction": path.is_junction(),
            "target": str(path.resolve()),
        }
        if kind == "skills":
            entry = path / "SKILL.md"
            row["has_skill"] = entry.is_file()
            if entry.is_file():
                text = entry.read_text(encoding="utf-8-sig")
                row["frontmatter"] = (
                    text.split("---", 2)[1] if text.startswith("---") else None
                )
        report[kind].append(row)
output = Path(__file__).resolve().parents[1] / "audit/claude/local-inventory.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False))
