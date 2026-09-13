"""Verify the live transaction and rehearse its rollback on a private copy."""

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit/claude"
spec = importlib.util.spec_from_file_location(
    "combo_transaction", ROOT / "scripts/setup.py"
)
assert spec is not None and spec.loader is not None
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def outside_policy(raw):
    if b"<!-- BEGIN COMBO -->" in raw:
        start = raw.index(b"<!-- BEGIN COMBO -->")
        end = raw.index(b"<!-- END COMBO -->", start) + len(b"<!-- END COMBO -->")
        return raw[:start] + raw[end:].lstrip(b"\r\n")
    if raw.startswith(b"## Skill discipline"):
        return raw[raw.index(b"## Memory:") :]
    return raw


def main():
    report = json.loads((OUT / "install-receipt.json").read_text(encoding="utf-8"))
    receipt_path = Path(report["receipt"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    target = Path(receipt["target_root"])
    mismatches = [
        row["path"]
        for row in receipt["files"]
        if engine.digest(engine.existing(Path(row["path"]))) != row["after_sha256"]
    ]
    claude_row = next(
        row for row in receipt["files"] if Path(row["path"]).name == "CLAUDE.md"
    )
    before = (receipt_path.parent / claude_row["backup"]).read_bytes()
    after = Path(claude_row["path"]).read_bytes()
    policy_preserved = outside_policy(before) == outside_policy(after)
    with tempfile.TemporaryDirectory(prefix="combo-claude-rollback-") as temporary:
        folder = Path(temporary)
        clone = folder / ".claude"
        clone.mkdir()
        backups = folder / "backups"
        shutil.copytree(receipt_path.parent, backups)
        copy_receipt = json.loads(json.dumps(receipt))
        copy_receipt["target_root"] = str(clone)
        for row in copy_receipt["files"]:
            source = Path(row["path"])
            destination = clone / source.relative_to(target)
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            row["path"] = str(destination)
        copied = backups / "receipt.json"
        copied.write_text(json.dumps(copy_receipt), encoding="utf-8")
        engine.rollback(copied, clone)
        rollback_errors = [
            row["path"]
            for row in copy_receipt["files"]
            if engine.digest(engine.existing(Path(row["path"]))) != row["before_sha256"]
        ]
    result = {
        "receipt": str(receipt_path),
        "changed_paths": len(receipt["files"]),
        "live_bytes_match_receipt": not mismatches,
        "mismatches": mismatches,
        "claude_outside_combo_byte_identical": policy_preserved,
        "rollback_on_copy_passed": not rollback_errors,
        "rollback_errors": rollback_errors,
    }
    (OUT / "installation-verification.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result))
    assert not mismatches and policy_preserved and not rollback_errors


if __name__ == "__main__":
    main()
