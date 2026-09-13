"""Capture hashes only; never inspect memory stores or credentials."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
OUT = ROOT / "audit/claude"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    paths = [HOME / ".codex/config.toml", HOME / ".codex/AGENTS.md"]
    paths += list((HOME / ".codex/skills").glob("combo*/**/*"))
    paths += list((HOME / ".claude/skills").glob("*/**/*"))
    paths += list((HOME / ".claude/agents").glob("*"))
    paths += [HOME / ".claude/RTK.md"]
    files = {}
    for path in paths:
        if not path.is_file() or any(
            p.is_symlink() or p.is_junction() for p in [path, *path.parents]
        ):
            continue
        rel = path.relative_to(HOME).as_posix()
        if (
            rel.startswith(".claude/skills/combo")
            or rel == ".claude/agents/combo-worker.md"
        ):
            continue
        files[rel] = digest(path)
    settings = json.loads(
        (HOME / ".claude/settings.json").read_text(encoding="utf-8-sig")
    )
    settings.get("enabledPlugins", {}).pop("ecc-hubs@bundle", None)
    settings.get("enabledPlugins", {}).pop("ecc@ecc", None)
    settings.get("enabledPlugins", {}).pop("mattpocock-skills@mattpocock", None)
    overrides = settings.get("skillOverrides", {})
    overrides.pop("multi-model-orchestrator", None)
    if not overrides:
        settings.pop("skillOverrides", None)
    files["settings-unowned-semantic"] = hashlib.sha256(
        json.dumps(settings, sort_keys=True).encode()
    ).hexdigest()
    return files


if __name__ == "__main__":
    current = capture()
    if sys.argv[1] in {"before", "before-install"}:
        name = (
            "preservation-install-baseline.json"
            if sys.argv[1] == "before-install"
            else "preservation-baseline.json"
        )
        (OUT / name).write_text(json.dumps(current, indent=2), encoding="utf-8")
        print(f"Baseline: {len(current)} file/config hashes")
    else:
        baseline = OUT / "preservation-install-baseline.json"
        if not baseline.exists():
            baseline = OUT / "preservation-baseline.json"
        before = json.loads(baseline.read_text(encoding="utf-8"))
        initial = json.loads(
            (OUT / "preservation-baseline.json").read_text(encoding="utf-8")
        )
        preinstall_changes = [
            key
            for key in initial.keys() | before.keys()
            if initial.get(key) != before.get(key)
        ]
        changes = [
            key
            for key in before.keys() | current.keys()
            if before.get(key) != current.get(key)
        ]
        report = {
            "checked": len(before),
            "unchanged": not changes,
            "changed": changes,
            "unrelated_changes_observed_before_install": preinstall_changes,
            "baseline": baseline.name,
        }
        (OUT / "preservation.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(json.dumps(report))
        sys.exit(bool(changes))
