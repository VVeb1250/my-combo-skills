"""Copy the core context rules into every workflow so a workflow load needs no separate read.

practices/context.md stays the single place to edit. The CORE sections are copied verbatim
(headings demoted one level) into a marked block at the end of each workflow, and the
"Read context once" sentence becomes a pointer for the remaining mechanics.

    py scripts/sync-context-core.py          # rewrite the workflows
    py scripts/sync-context-core.py --check  # exit 1 if any workflow is out of date
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "skills" / "combo" / "practices" / "context.md"
WORKFLOWS = ROOT / "skills" / "combo" / "workflows"
CORE = ("Own the outcome", "Decision triage", "Verify against intent")
BEGIN = "<!-- BEGIN CONTEXT CORE (generated from practices/context.md by scripts/sync-context-core.py; edit there) -->"
END = "<!-- END CONTEXT CORE -->"
NEW_SENTENCE = ("Apply the context rules at the end of this file; read\n"
                "[context](../practices/context.md) only for evidence-selection or reporting\n"
                "mechanics that are unresolved.")
# the original instruction, or a previously generated pointer (any wrapping), so reruns converge
OLD_SENTENCE = re.compile(
    r"Read \[context\]\(\.\./practices/context\.md\) once for\s+evidence\s+selection\s+and\s+reporting\."
    r"|Apply the context rules at the end of this file;\s+read\s+\[context\]\(\.\./practices/context\.md\)"
    r"\s+only\s+for\s+evidence-selection\s+or\s+reporting\s+mechanics\s+that\s+are\s+unresolved\.")
SAME_DIR_LINK = re.compile(r"\]\((outcome-evidence|project-knowledge|build|delegation|design|e2e|security|simplicity|tests)\.md\)")


def core_block() -> str:
    text = CONTEXT.read_text(encoding="utf-8")
    sections = {m.group(1): m.group(0) for m in re.finditer(r"(?ms)^## (.+?)\n.*?(?=^## |\Z)", text)}
    missing = [name for name in CORE if name not in sections]
    if missing:
        raise SystemExit(f"context.md lacks core sections: {missing}")
    body = "\n".join(re.sub(r"^## ", "### ", sections[name].rstrip(), count=1) + "\n" for name in CORE)
    body = SAME_DIR_LINK.sub(lambda m: f"](../practices/{m.group(1)}.md)", body)  # links were relative to practices/
    return f"{BEGIN}\n## Context rules\n\n{body}{END}\n"


def render(workflow: str, block: str) -> str:
    text = workflow
    if BEGIN in text:
        text = text[: text.index(BEGIN)].rstrip() + "\n"
    text, _ = OLD_SENTENCE.subn(NEW_SENTENCE, text, count=1)
    return text.rstrip() + "\n\n" + block


def main(argv: list[str]) -> int:
    check = "--check" in argv
    block = core_block()
    stale = []
    for path in sorted(WORKFLOWS.glob("*.md")):
        current = path.read_text(encoding="utf-8")
        wanted = render(current, block)
        if wanted != current:
            stale.append(path.name)
            if not check:
                with path.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(wanted)
    if check:
        print(f"CONTEXT_CORE_{'STALE ' + ', '.join(stale) if stale else 'OK'} workflows={len(list(WORKFLOWS.glob('*.md')))}")
        return 1 if stale else 0
    print(f"rewrote {len(stale)} workflows" if stale else "already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
