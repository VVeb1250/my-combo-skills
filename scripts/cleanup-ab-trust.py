"""Remove only experiment-owned ephemeral project trust records after evaluation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOTS = (
    Path("D:/combo-ab-evals/combo-ab-run-tmjw_vry"),
    Path("D:/combo-ab-evals/combo-ab-run-siyimloi"),
    Path("D:/combo-ab-evals/combo-ab-run-wcq53nyr"),
)


def owned_keys() -> set[str]:
    keys = set()
    for report in (
        ROOT / "audit/ab/probe-final",
        ROOT / "audit/ab/matched-rest",
        ROOT / "audit/ab/diagnostic-repeat",
    ):
        for result in report.glob("arms/*/*/result.json"):
            data = json.loads(result.read_text(encoding="utf-8-sig"))
            path = Path(data["workdir"]).resolve()
            if path.parent not in tuple(root.resolve() for root in RUN_ROOTS):
                raise ValueError(f"Result is outside the three owned runs: {path}")
            keys.add(str(path).casefold())
    return keys


def remove_records(raw: bytes, keys: set[str]) -> tuple[bytes, list[str]]:
    text = raw.decode("utf-8-sig")
    before = tomllib.loads(text)
    expected = copy.deepcopy(before)
    headers = list(re.finditer(r"(?m)^\[[^\r\n]+\][ \t]*\r?$", text))
    removals = []
    removed = []
    for index, header in enumerate(headers):
        try:
            table = tomllib.loads(header.group() + '\ntrust_level = "trusted"\n')
        except tomllib.TOMLDecodeError:
            continue
        projects = table.get("projects", {})
        if len(projects) != 1:
            continue
        key = next(iter(projects))
        if key.casefold() not in keys:
            continue
        if before.get("projects", {}).get(key) != {"trust_level": "trusted"}:
            raise ValueError(
                "An owned temporary project record has additional user settings"
            )
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        block = text[header.end() : end]
        # Do not swallow comments or other settings added after the owned value.
        value = re.match(
            r"\r?\ntrust_level\s*=\s*[\"\']trusted[\"\'][ \t]*(?:\r?\n|$)", block
        )
        if value is None or block[value.end() :].strip():
            raise ValueError(
                "Owned project block has unexpected text; leave it for review"
            )
        removals.append((header.start(), end))
        removed.append(key)
        expected["projects"].pop(key)
    for start, end in reversed(removals):
        text = text[:start] + text[end:]
    if not expected.get("projects"):
        expected.pop("projects", None)
    if tomllib.loads(text) != expected:
        raise AssertionError("Cleanup would change unrelated configuration")
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + text.encode("utf-8"), removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = Path.home() / ".codex/config.toml"
    before = config.read_bytes()
    after, removed = remove_records(before, owned_keys())
    receipt = {
        "removed_count": len(removed),
        "removed_project_keys": removed,
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "after_sha256": hashlib.sha256(after).hexdigest(),
        "unrelated_config_semantically_identical": True,
        "applied": args.apply,
    }
    if args.apply and removed:
        backup = ROOT / "backups/ab-trust-cleanup" / receipt["before_sha256"]
        backup.mkdir(parents=True, exist_ok=True)
        (backup / "config.toml").write_bytes(before)
        temporary = config.with_name("config.combo-trust-cleanup.tmp")
        with temporary.open("xb") as stream:
            stream.write(after)
        if config.read_bytes() != before:
            temporary.unlink()
            raise ValueError(
                "Host config changed during cleanup; retry from current state"
            )
        temporary.replace(config)
        receipt["backup"] = str(backup / "config.toml")
    output = ROOT / "audit/ab/trust-cleanup.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
