"""Verify Combo source/install state and rehearse a v2 receipt on copies."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from collections import Counter
from pathlib import Path

import setup

ROOT = setup.ROOT
NATIVE_PREFIXES = (
    "browser:",
    "chrome:",
    "computer-use:",
    "documents:",
    "imagegen",
    "pdf",
    "presentations:",
    "sites:",
    "spreadsheets:",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inventory_entries(path: Path) -> list[dict] | None:
    if not path.is_file():
        return None
    payload = read_json(path)
    try:
        return payload["skills"]["data"][0]["skills"]
    except (KeyError, IndexError, TypeError):
        raise ValueError(f"Invalid inventory shape: {path}")


def _inventory_key(row: dict) -> str:
    """Compare the complete discovery record without allowing reordering."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def verify_inventory(
    before: list[dict] | None,
    after: list[dict] | None,
    live_packages: set[str] | None = None,
) -> dict:
    if before is None or after is None:
        return {"available": False}
    live_packages = live_packages or setup.manifest_package_names()
    before_native = {
        (row["name"], row.get("path"), row.get("enabled"))
        for row in before
        if row["name"].startswith(NATIVE_PREFIXES)
    }
    after_native = {
        (row["name"], row.get("path"), row.get("enabled"))
        for row in after
        if row["name"].startswith(NATIVE_PREFIXES)
    }
    if before_native != after_native:
        raise AssertionError("Native browser/artifact discovery changed")
    # The installer may add or disable declared Combo entries.  Every other
    # discovered skill must retain its identity, path, enabled state, and
    # scope.  This catches unrelated drift in the expanded full-library run.
    before_unrelated = Counter(
        _inventory_key(row) for row in before if row.get("name") not in live_packages
    )
    after_unrelated = Counter(
        _inventory_key(row) for row in after if row.get("name") not in live_packages
    )
    if before_unrelated != after_unrelated:
        raise AssertionError("Unrelated skill discovery changed")
    return {
        "available": True,
        "before_count": len(before),
        "after_count": len(after),
        "native_count": len(after_native),
        "active_combo": sorted(
            row["name"]
            for row in after
            if row["name"] in live_packages and row.get("enabled")
        ),
        "live_packages": sorted(live_packages),
    }


def rehearse_receipt(receipt_path: Path) -> int:
    receipt = read_json(receipt_path)
    with tempfile.TemporaryDirectory(prefix="combo-rollback-check-") as temporary:
        tmp = Path(temporary)
        state = tmp / "state"
        target_root = state / ".codex"
        backup = tmp / "backup"
        backup.mkdir()
        copied = json.loads(json.dumps(receipt))
        copied["target_root"] = str(target_root)
        for index, row in enumerate(copied["files"]):
            target = target_root / Path(row["path"]).relative_to(
                Path(receipt.get("target_root") or Path(row["path"]).anchor)
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            source = Path(row["path"])
            # The receipt represents an applied state. For a deleted file the
            # target stays absent; for a write, copy its current applied bytes.
            if row.get("after_sha256") is not None and source.exists():
                shutil.copyfile(source, target)
            row["path"] = str(target)
            if row.get("backup"):
                source_backup = receipt_path.parent / row["backup"]
                if not source_backup.is_file():
                    raise ValueError(f"Missing receipt backup: {source_backup}")
                shutil.copyfile(source_backup, backup / row["backup"])
        test_receipt = backup / "receipt.json"
        test_receipt.write_text(json.dumps(copied), encoding="utf-8")
        setup.rollback(test_receipt, target_root)
        for row in copied["files"]:
            assert (
                setup.digest(setup.existing(Path(row["path"]))) == row["before_sha256"]
            ), row["path"]
    return len(copied["files"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--receipt", type=Path, help="Applied receipt to rehearse on copies"
    )
    parser.add_argument(
        "--before-inventory",
        type=Path,
        default=ROOT / "audit" / "v2" / "baseline-codex.json",
        help="Discovery inventory captured before installation",
    )
    parser.add_argument(
        "--after-inventory",
        type=Path,
        default=ROOT / "audit" / "v2" / "after-codex.json",
        help="Discovery inventory captured after installation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "audit" / "v2" / "verify.json",
        help="Where to write the verification report",
    )
    args = parser.parse_args()

    validation_path = ROOT / "audit" / "curated-validation.json"
    validation = (
        read_json(validation_path)
        if validation_path.is_file()
        else {"errors": ["validation report missing"]}
    )
    if validation.get("errors"):
        raise SystemExit(f"Validation errors: {validation['errors']}")
    live_packages = setup.manifest_package_names()
    skills_root = ROOT / "skills"
    package_dirs = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if package_dirs != live_packages:
        raise SystemExit(
            "Unexpected live source packages: "
            f"{sorted(package_dirs)}; manifest declares {sorted(live_packages)}"
        )

    before = inventory_entries(args.before_inventory)
    after = inventory_entries(args.after_inventory)
    report = {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validation": validation,
        "inventory": verify_inventory(before, after, live_packages),
        "inventory_paths": {
            "before": str(args.before_inventory),
            "after": str(args.after_inventory),
        },
        "rollback_rehearsal_files": None,
    }
    if args.receipt:
        report["rollback_rehearsal_files"] = rehearse_receipt(args.receipt.resolve())
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
