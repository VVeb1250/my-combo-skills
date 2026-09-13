"""Read-only lexical audit of the selected Combo bundle; findings need review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PATTERNS = {
    "instruction_override": r"ignore (?:all |the )?(?:previous|above|prior) instructions|disregard (?:the )?(?:system|your) (?:prompt|instructions|rules)",
    "authority_or_identity": r"you are now\b|new instructions:|<\s*(?:system|assistant)\s*>",
    "bypass_user": r"without (?:asking|telling|informing|confirming with) the user",
    "secret_transfer_shape": r"(?:print|echo|cat|send|upload).{0,20}(?:\.env|credentials|api[_ -]?key)",
    "external_sink": r"webhook\.site|pastebin|ngrok|requestbin|burpcollaborator|\.onion\b",
}
HIDDEN = set(
    map(
        chr,
        [
            0x200B,
            0x200C,
            0x200D,
            0x200E,
            0x200F,
            *range(0x202A, 0x202F),
            *range(0x2060, 0x2065),
            0xFEFF,
        ],
    )
)


def audit(root: Path) -> dict:
    patterns = {
        key: re.compile(value, re.IGNORECASE) for key, value in PATTERNS.items()
    }
    findings = []
    hashes = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".yaml",
            ".json",
            ".txt",
        }:
            continue
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        hashes[relative] = hashlib.sha256(raw).hexdigest()
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            findings.append({"path": relative, "pattern": "non_utf8", "line": None})
            continue
        for number, line in enumerate(content.splitlines(), 1):
            for name, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    findings.append(
                        {
                            "path": relative,
                            "line": number,
                            "pattern": name,
                            "match": match.group(0),
                            "context": line[:360],
                        }
                    )
            hidden = sorted({f"U+{ord(char):04X}" for char in line if char in HIDDEN})
            if hidden:
                findings.append(
                    {
                        "path": relative,
                        "line": number,
                        "pattern": "hidden_characters",
                        "codes": hidden,
                    }
                )
    return {
        "root": str(root),
        "files": len(hashes),
        "findings": findings,
        "hashes": hashes,
        "limit": "Lexical candidates only, not a semantic safety verdict or an execution audit.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("skills/combo"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.root.resolve())
    if not report["files"]:
        parser.error("No instruction files found; check --root")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "files": report["files"],
                "findings": len(report["findings"]),
                "output": str(args.output),
            }
        )
    )
