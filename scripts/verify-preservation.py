"""Verify unrelated host settings against backups in a real installation receipt."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def outside_block(raw: bytes, begin: str, end: str) -> bytes:
    start = raw.find(begin.encode())
    finish = raw.find(end.encode())
    if (
        start < 0
        or finish < start
        or raw.count(begin.encode()) != 1
        or raw.count(end.encode()) != 1
    ):
        raise ValueError("Expected one complete owned marker block")
    return raw[:start] + raw[finish + len(end.encode()) :]


def unowned_config(raw: bytes, manifest: dict, home: Path) -> dict:
    data = copy.deepcopy(tomllib.loads(raw.decode("utf-8-sig")))
    data.get("agents", {}).pop(manifest["config"]["worker_role"]["name"], None)
    for plugin in manifest["config"].get("disable_plugins", []):
        data.get("plugins", {}).get(plugin, {}).pop("enabled", None)
    disabled = {
        str((home / row["path"]).resolve()).replace("\\", "/").casefold()
        for row in manifest.get("disable_local", [])
    }
    skills = data.get("skills", {})
    if "config" in skills:
        skills["config"] = [
            row
            for row in skills["config"]
            if str(Path(row.get("path", "")).resolve()).replace("\\", "/").casefold()
            not in disabled
        ]
    return data


def verify(receipt_path: Path) -> dict:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads(
        (ROOT / "install-manifest.json").read_text(encoding="utf-8-sig")
    )
    target = Path(receipt["target_root"])
    changed = {
        Path(row["path"]).name: row
        for row in receipt["files"]
        if Path(row["path"]).parent == target
    }

    def pair(name: str) -> tuple[bytes, bytes]:
        row = changed.get(name)
        current = (target / name).read_bytes()
        if row is None:
            return current, current
        if not row.get("backup"):
            raise ValueError(f"No pre-install backup for {name}")
        return (receipt_path.parent / row["backup"]).read_bytes(), current

    before_agents, after_agents = pair("AGENTS.md")
    markers = manifest["agents"]["markers"]
    before_unowned = outside_block(before_agents, markers["begin"], markers["end"])
    after_unowned = outside_block(after_agents, markers["begin"], markers["end"])
    before_config, after_config = pair("config.toml")
    old_config = unowned_config(before_config, manifest, target.parent)
    new_config = unowned_config(after_config, manifest, target.parent)

    def differing_keys(before: object, after: object, prefix: str = "") -> list[str]:
        if isinstance(before, dict) and isinstance(after, dict):
            return [
                path
                for key in sorted(set(before) | set(after))
                for path in differing_keys(
                    before.get(key), after.get(key), f"{prefix}.{key}".strip(".")
                )
            ]
        return [] if before == after else [prefix]

    result = {
        "receipt": str(receipt_path),
        "agents_outside_combo_byte_identical": before_unowned == after_unowned,
        "agents_outside_combo_sha256": hashlib.sha256(after_unowned).hexdigest(),
        "unowned_config_semantically_identical": old_config == new_config,
        "unowned_changed_keys": differing_keys(old_config, new_config),
        "main_model_unchanged": tomllib.loads(before_config.decode("utf-8-sig")).get(
            "model"
        )
        == tomllib.loads(after_config.decode("utf-8-sig")).get("model"),
        "receipt_paths": len(receipt["files"]),
        "scope": "Compares Preferences/Memory text and non-owned config against receipt backups; no secret values emitted.",
    }
    if not all(
        result[key]
        for key in (
            "agents_outside_combo_byte_identical",
            "unowned_config_semantically_identical",
            "main_model_unchanged",
        )
    ):
        raise AssertionError(json.dumps(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.receipt.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
