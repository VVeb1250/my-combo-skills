"""Verify pinned source checkouts and the reviewed Combo specialist shelf.

This command is intentionally a check. It never fetches, installs, or copies an
upstream skill. Use ``scripts/build-specialists.py`` for the explicit reviewed
shelf build after source pins have been inspected.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "sources.lock.json"
MANIFEST_PATH = ROOT / "install-manifest.json"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def includes_full_library(manifest: dict) -> bool:
    """Detect an explicitly staged full-source library in the manifest/tree."""
    for key in ("full_library", "full-library", "library"):
        value = manifest.get(key)
        if value is True or isinstance(value, dict):
            return True
    for entry in manifest.get("source_roots", []):
        if not isinstance(entry, dict):
            continue
        if any(
            "library" in str(key).lower() or "library" in str(value).lower()
            for key, value in entry.items()
        ):
            return True
        if entry.get("library") is True or entry.get("kind") in {
            "library",
            "full-library",
            "source-library",
        }:
            return True
        for value in (entry.get("source"), entry.get("target")):
            if isinstance(value, str) and "library" in value.lower():
                return True
    # A nested library is kept inside combo so sibling workflow links remain
    # package-local.  These names are deliberately explicit and do not cause
    # the check to run for the ordinary specialist/reference shelf.
    for relative in (
        "skills/combo/references/library",
        "skills/combo/references/full-library",
        "skills/combo/references/source-library",
        "skills/combo/references/upstream-library",
    ):
        if (ROOT / relative).is_dir():
            return True
    return False


def git(src: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(src), *args], text=True).strip()


def refresh_lock() -> list[dict]:
    rows = []
    for pack in ("karpathy", "ponytail", "matt", "ecc"):
        source = ROOT / "sources" / pack
        if not source.is_dir():
            raise ValueError(f"Missing source checkout: {source}")
        rows.append(
            {
                "pack": pack,
                "url": git(source, "remote", "get-url", "origin"),
                "commit": git(source, "rev-parse", "HEAD"),
            }
        )
    return rows


def verify_lock() -> list[dict]:
    if not LOCK_PATH.is_file():
        raise ValueError(f"Missing source lock: {LOCK_PATH}")
    locked = read_json(LOCK_PATH)
    if not isinstance(locked, list):
        raise TypeError("sources.lock.json must contain a list")
    current = {row["pack"]: row for row in refresh_lock()}
    mismatches = []
    for row in locked:
        pack = row.get("pack")
        if pack not in current:
            mismatches.append(f"unknown locked pack: {pack}")
            continue
        actual = current[pack]
        if row.get("commit") != actual["commit"] or row.get("url") != actual["url"]:
            mismatches.append(
                f"{pack}: locked {row.get('commit')} / {row.get('url')}, "
                f"checkout {actual['commit']} / {actual['url']}"
            )
    if {row.get("pack") for row in locked} != set(current):
        mismatches.append("sources.lock.json does not cover all four source packs")
    if mismatches:
        raise ValueError(
            "Source pin mismatch; inspect and intentionally refresh the lock:\n"
            + "\n".join(mismatches)
        )
    return locked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-lock",
        action="store_true",
        help="Write current checkout commits after an intentional source review",
    )
    args = parser.parse_args()
    if args.refresh_lock:
        rows = refresh_lock()
        LOCK_PATH.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    else:
        rows = verify_lock()

    builder = ROOT / "scripts" / "build-specialists.py"
    if builder.is_file():
        subprocess.run([sys.executable, str(builder), "--check"], check=True)
    manifest = read_json(MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise TypeError("install-manifest.json must contain an object")
    full_library_builder = ROOT / "scripts" / "build-full-library.py"
    if includes_full_library(manifest):
        if not full_library_builder.is_file():
            raise ValueError(
                "Manifest includes the full-source library but scripts/build-full-library.py is missing"
            )
        library = ROOT / "skills/combo/references/library"
        subprocess.run(
            [
                sys.executable,
                str(full_library_builder),
                "--check",
                "--output",
                str(library),
            ],
            check=True,
        )
    print(json.dumps({"status": "verified", "packs": [row["pack"] for row in rows]}))


if __name__ == "__main__":
    main()
