"""Measure which Combo entry Claude Code selects for a natural prompt.

Two arms run every case in a fresh copy of a small fixture:

  policy            the user's real configuration, including the global
                    CLAUDE.md routing paragraph;
  description-only  CLAUDE.md loading disabled, so only the skill descriptions
                    can trigger a route.

The probe stops each session at the first Skill tool call (or at the final
answer), so it measures the routing decision, not the workflow that follows.
It starts headless `claude -p` sessions only when run explicitly; the unit tests
cover case validation and event analysis without launching a model.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "evals" / "routing" / "cases.json"
ARMS = {
    "policy": {},
    "description-only": {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"},
}
TOOLS = "Skill,Read,Glob,Grep,Edit"
NONE = "none"


def load_cases(path: Path = CASES_FILE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def entry_names() -> set[str]:
    """Names of the Combo entries shipped in this checkout."""
    return {p.name for p in (ROOT / "skills").iterdir() if p.name.startswith("combo")}


def analyze_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Reduce a stream-json transcript to the routing decision."""
    tools: list[str] = []
    first_skill = None
    text = ""
    result: dict[str, Any] = {}
    for event in events:
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    name = block.get("name", "")
                    if name == "Skill" and first_skill is None:
                        first_skill = str(block.get("input", {}).get("skill", ""))
                    elif first_skill is None:
                        tools.append(name)
                elif block.get("type") == "text":
                    text = block.get("text", "")
        elif event.get("type") == "result":
            result = event
    return {
        "routed": first_skill or NONE,
        "tools_before_skill": tools,
        "final_text": (result.get("result") or text)[:500],
        "result_subtype": result.get("subtype"),
        "cost_usd": result.get("total_cost_usd"),
    }


def score(case: dict[str, Any], analysis: dict[str, Any]) -> bool:
    return analysis["routed"] in case["acceptable"]


def build_command(claude: str, case: dict[str, Any], model: str, max_turns: int) -> list[str]:
    return [
        claude, "-p", case["prompt"],
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(max_turns), "--model", model,
        "--tools", TOOLS, "--allowedTools", TOOLS,
        "--strict-mcp-config",
        "--settings", '{"disableAllHooks":true}',
        "--no-session-persistence",
    ]


def record_from(case: dict[str, Any], arm: str, events: list[dict[str, Any]], seconds: float | None,
                timed_out: bool) -> dict[str, Any]:
    analysis = analyze_events(events)
    return {
        "case": case["id"], "arm": arm, "kind": case["kind"], "expected": case["expected"],
        "acceptable": case["acceptable"], **analysis,
        "pass": score(case, analysis), "seconds": seconds, "timed_out": timed_out,
    }


def run_one(claude: str, case: dict[str, Any], arm: str, model: str, max_turns: int,
            timeout: int, out_dir: Path) -> dict[str, Any]:
    saved = out_dir / f"{case['id']}.{arm}.jsonl"
    if saved.exists():  # finished earlier in this results directory: no new model call
        lines = [json.loads(x) for x in saved.read_text(encoding="utf-8").splitlines() if x.strip()]
        return record_from(case, arm, lines, None, False)
    fixture = ROOT / load_cases()["fixture"]
    env = {**os.environ, **ARMS[arm]}
    if arm == "policy":
        env.pop("CLAUDE_CODE_DISABLE_CLAUDE_MDS", None)
    events: list[dict[str, Any]] = []
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="combo-routing-", ignore_cleanup_errors=True) as work:
        shutil.copytree(fixture, work, dirs_exist_ok=True)
        proc = subprocess.Popen(
            build_command(claude, case, model, max_turns), cwd=work, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace",
        )
        timed_out = threading.Event()

        def expire() -> None:
            timed_out.set()
            proc.kill()

        timer = threading.Timer(timeout, expire)
        timer.start()
        try:
            for line in proc.stdout:  # type: ignore[union-attr]
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                events.append(event)
                # Routing is decided at the first Skill call; stop paying for the rest.
                if event.get("type") == "assistant" and any(
                    b.get("type") == "tool_use" and b.get("name") == "Skill"
                    for b in event.get("message", {}).get("content", [])
                ):
                    break
        finally:
            timer.cancel()
            proc.kill()
            proc.wait()
    record = record_from(case, arm, events, round(time.time() - started, 1), timed_out.is_set())
    (out_dir / f"{case['id']}.{arm}.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events), encoding="utf-8")
    return record


def run_safely(*args: Any) -> dict[str, Any]:
    try:
        return run_one(*args)
    except Exception as error:  # one broken session must not discard the others
        case, arm = args[1], args[2]
        return {"case": case["id"], "arm": arm, "kind": case["kind"], "expected": case["expected"],
                "acceptable": case["acceptable"], "routed": "error", "pass": False,
                "error": repr(error), "cost_usd": None}


def summarize(records: list[dict[str, Any]]) -> str:
    lines = ["# Routing probe", ""]
    for arm in ARMS:
        rows = [r for r in records if r["arm"] == arm]
        if not rows:
            continue
        lines.append(f"- **{arm}**: {sum(r['pass'] for r in rows)}/{len(rows)} routed acceptably")
        for kind in ("negative", "positive", "confusable"):
            sub = [r for r in rows if r["kind"] == kind]
            if sub:
                lines.append(f"  - {kind}: {sum(r['pass'] for r in sub)}/{len(sub)}")
    lines += ["", "| case | expected | " + " | ".join(ARMS) + " |", "| --- | --- | " + " | ".join("---" for _ in ARMS) + " |"]
    for case_id in dict.fromkeys(r["case"] for r in records):
        rows = {r["arm"]: r for r in records if r["case"] == case_id}
        first = next(iter(rows.values()))
        cells = [f"{'ok' if rows[a]['pass'] else 'MISS'} `{rows[a]['routed']}`" if a in rows else "-" for a in ARMS]
        lines.append(f"| {case_id} | `{first['expected']}` | " + " | ".join(cells) + " |")
    cost = sum(r["cost_usd"] or 0 for r in records)
    lines += ["", f"Reported cost (not an invoice): ${cost:.2f}. One sample per case and arm; "
              "a miss is a lead for repeats, not a verdict."]
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--output", default=None, help="results directory (default evals/routing/results/run-<time>)")
    p.add_argument("--model", default="sonnet")
    p.add_argument("--arms", nargs="+", choices=list(ARMS), default=list(ARMS))
    p.add_argument("--cases", nargs="*", help="case ids; default all")
    p.add_argument("--max-turns", type=int, default=4)
    p.add_argument("--timeout", type=int, default=150)
    p.add_argument("--workers", type=int, default=3)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    claude = shutil.which("claude")
    if not claude:
        print("claude CLI not found on PATH")
        return 2
    cases = load_cases()["cases"]
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases]
    out_dir = Path(args.output) if args.output else ROOT / "evals" / "routing" / "results" / time.strftime("run-%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(c, arm) for c in cases for arm in args.arms]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(
            lambda j: run_safely(claude, j[0], j[1], args.model, args.max_turns, args.timeout, out_dir), jobs))
    (out_dir / "summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    report = summarize(records)
    (out_dir / "summary.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
