"""Compare task outcomes between instruction arms on the same cases and host.

For each (host, arm, case, repeat) this runs one fresh headless session in a
copy of the case fixture, then scores the *outcome* with one scorer shared by
both hosts: independent acceptance tests, changed-file scope, final-answer
evidence, and cost (tokens, tool calls, time). It also records whether a Combo
workflow was loaded, as information rather than as a pass/fail condition.

Arms:
  claude  full          the user's real configuration
          no-claude-md  CLAUDE.md loading disabled (also drops the engineering
                        policy and preferences, not only the routing paragraph)
  codex   full          the user's real configuration
          home:NAME     a prepared CODEX_HOME passed with --codex-home NAME=PATH

The harness never reads, copies, or links credential files. Preparing a Codex
home that differs only in AGENTS.md needs auth available to it, which is the
operator's decision (see evals/compare/README.md).

It starts model sessions only when run explicitly; the unit tests cover case
loading and scoring without launching anything.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import uuid
import threading
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evals" / "compare"
V2_ROOT = ROOT / "evals" / "v2"
_SPEC = importlib.util.spec_from_file_location("workflow_smoke", ROOT / "scripts" / "run-workflow-smoke.py")
assert _SPEC is not None
smoke = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(smoke)

CLAUDE_ARMS = {"full": {}, "no-claude-md": {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}}
CODEX_ARMS = {"full": {}}  # plus "home:<name>" arms, one per --codex-home NAME=PATH
READ_TOOLS = "Read,Glob,Grep,Skill"
WRITE_TOOLS = READ_TOOLS + ",Edit,Write,Bash"
WRITE_ALLOWED = READ_TOOLS + ",Edit,Write,Bash(python:*),Bash(py:*),Bash(python3:*)"


def load_cases() -> list[dict[str, Any]]:
    """The selected v2 cases plus the compare-only cases, with their roots."""
    compare = json.loads((EVAL_ROOT / "cases.json").read_text(encoding="utf-8"))
    v2 = {c["id"]: c for c in smoke.load_suite()["cases"]}
    cases = []
    for case_id in compare["v2_case_ids"]:
        cases.append({**v2[case_id], "_root": V2_ROOT})
    for case in compare["cases"]:
        cases.append({**case, "_root": EVAL_ROOT})
    return cases


def run_acceptance_script(script: Path, workdir: Path, timeout: int = 60) -> dict[str, Any]:
    env = {**os.environ, "COMBO_EVAL_ROOT": str(workdir), "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        done = subprocess.run([sys.executable, str(script)], cwd=workdir, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
        return {"passed": done.returncode == 0, "tail": (done.stdout + done.stderr)[-400:]}
    except subprocess.TimeoutExpired:
        return {"passed": False, "tail": "acceptance timed out"}


NEGATION_BEFORE_RE = re.compile(
    r"(?i)(?:ไม่ได้|ยังไม่ได้|ไม่|มิได้|not|never|without|n't|no)\s*(?:ได้\s*)?(?:the\s+|any\s+|a\s+)?$")


def claims_implementation(answer: str) -> bool:
    """True when the answer claims to have changed things; "did not edit files" is not a claim."""
    for match in smoke.IMPLEMENTATION_CLAIM_RE.finditer(answer):
        if not NEGATION_BEFORE_RE.search(answer[max(0, match.start() - 14):match.start()]):
            return True
    return False


def score_outcome(case: dict[str, Any], answer: str, changed: list[dict[str, Any]],
                  before_acc: dict[str, Any] | None, after_acc: dict[str, Any] | None,
                  commands: list[str], tool_count: int, workdir: Path) -> list[str]:
    """Return outcome failures. Route and workflow-loading evidence is not scored here."""
    failures: list[str] = []
    if not answer.strip():
        failures.append("no final answer")
    acceptance = case.get("acceptance", {})
    if acceptance.get("before_must_fail") and not (before_acc and not before_acc["passed"]):
        failures.append("fixture was not failing before the session")
    if acceptance.get("after_must_pass") and not (after_acc and after_acc["passed"]):
        failures.append("acceptance did not pass")
    changed_paths = {row["path"] for row in changed}
    if case.get("no_writes") and changed_paths:
        failures.append("read-only case changed files: " + ", ".join(sorted(changed_paths)))
    if case.get("no_writes") and any(smoke.WRITE_COMMAND_RE.search(c) for c in commands):
        failures.append("read-only case ran a write-like command")
    allowed = case.get("allowed_changed_paths")
    if allowed is not None and not changed_paths <= set(allowed):
        failures.append("changed outside scope: " + ", ".join(sorted(changed_paths - set(allowed))))
    expected = case.get("assertions", {})
    required = set(expected.get("must_have_changed", []))
    if required and not required <= changed_paths:
        failures.append("required files unchanged: " + ", ".join(sorted(required - changed_paths)))
    lowered = answer.lower()
    for group in case.get("required_final_term_groups", []):
        if not any(str(t).lower() in lowered for t in group.get("any", [])):
            failures.append(f"answer lacks {group.get('name')}")
    for adapter in case.get("required_final_adapter_evidence", []):
        alts = [str(t).lower() for t in adapter.get("any", [])]
        ctx = [str(t).lower() for t in adapter.get("context_any", [])]
        if not smoke.has_contextual_term(answer, alts, ctx):
            failures.append(f"answer lacks evidence for {adapter.get('name')}")
    if case.get("no_tools") and tool_count:
        failures.append("tool use on a no-tool task")
    if case.get("required_final_unicode_range") == "thai" and not smoke.THAI_RE.search(answer):
        failures.append("no Thai in answer")
    if expected.get("must_match_text"):
        target = workdir / "src" / "ui.py"
        text = target.read_text(encoding="utf-8") if target.exists() else ""
        if expected["must_match_text"] not in text or 'BUTTON_LABEL = "Save"' in text:
            failures.append("target text not updated")
    if expected.get("must_preserve_existing_seam") and not any(
            t in lowered for t in ("protocol", "interface", "seam", "shared adapter")):
        failures.append("plan does not address the existing seam")
    if expected.get("must_not_claim_implementation") and claims_implementation(answer):
        failures.append("claims implementation at a plan/review boundary")
    return failures


def claude_command(claude: str, case: dict[str, Any], model: str, max_turns: int) -> list[str]:
    writable = case["sandbox"] == "workspace-write"
    return [claude, "-p", case["prompt"], "--output-format", "stream-json", "--verbose",
            "--max-turns", str(max_turns), "--model", model,
            "--tools", WRITE_TOOLS if writable else READ_TOOLS,
            "--allowedTools", WRITE_ALLOWED if writable else READ_TOOLS,
            "--strict-mcp-config", "--settings", '{"disableAllHooks":true}', "--no-session-persistence"]


def analyze_claude(events: list[dict[str, Any]]) -> dict[str, Any]:
    commands: list[str] = []
    skills: list[str] = []
    tools = 0
    for event in events:
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") != "tool_use":
                continue
            tools += 1
            if block.get("name") == "Skill":
                skills.append(str(block.get("input", {}).get("skill", "")))
            elif block.get("name") == "Bash":
                commands.append(str(block.get("input", {}).get("command", "")))
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    usage = result.get("usage", {})
    return {"answer": result.get("result") or "", "commands": commands, "tool_count": tools,
            "workflow_loaded": any(s.startswith("combo") for s in skills), "skills": skills,
            "turns": result.get("num_turns"), "cost_usd": result.get("total_cost_usd"),
            "tokens_total": sum(usage.get(k, 0) for k in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")),
            "output_tokens": usage.get("output_tokens"), "subtype": result.get("subtype")}


def analyze_codex(events: list[dict[str, Any]]) -> dict[str, Any]:
    tools = smoke.tool_events(events)
    refs, _ = smoke.actual_references(events)
    usage = smoke.usage_from_events(events) or {}
    return {"answer": smoke.final_answer(events),
            "commands": [t["command"] for t in tools if isinstance(t.get("command"), str)],
            "tool_count": len(tools), "workflow_loaded": any("combo/" in r or r == "combo" for r in refs),
            "skills": refs, "turns": None, "cost_usd": None,
            "tokens_total": (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0),
            "output_tokens": usage.get("output_tokens"), "subtype": None}


def execute(host: str, case: dict[str, Any], arm: str, args: argparse.Namespace, workdir: Path) -> tuple[list[dict[str, Any]], bool]:
    """Run one headless session in workdir; return (events, timed_out)."""
    env = dict(os.environ)
    if host == "claude":
        env.update(CLAUDE_ARMS[arm])
        if arm == "full":
            env.pop("CLAUDE_CODE_DISABLE_CLAUDE_MDS", None)
        command = claude_command(args.claude, case, args.model, args.max_turns)
        stdin_text = None
    else:
        if arm.startswith("home:"):
            env["CODEX_HOME"] = str(Path(args.codex_homes[arm[5:]]).resolve())
        launcher, cli = smoke.find_cli(None)
        suite = {"model": args.model, "reasoning_effort": args.effort}
        command = smoke.build_command(launcher, cli, suite, case, workdir)
        stdin_text = case["prompt"]
    proc = subprocess.Popen(command, cwd=workdir, env=env, text=True, encoding="utf-8", errors="replace",
                            stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    expired = threading.Event()

    def kill() -> None:
        expired.set()
        smoke.terminate_owned_process_tree(proc)

    timer = threading.Timer(args.timeout, kill)
    timer.start()
    try:
        out, _ = proc.communicate(stdin_text, timeout=None)
    finally:
        timer.cancel()
    events, _ = smoke.parse_events(out or "")
    return events, expired.is_set()


def run_one(host: str, arm: str, case: dict[str, Any], rep: int, args: argparse.Namespace,
            out_dir: Path) -> dict[str, Any]:
    tag = f"{host}.{arm}.{case['id']}.r{rep}"
    saved = out_dir / f"{tag}.json"
    if saved.exists():
        return json.loads(saved.read_text(encoding="utf-8"))
    started = time.time()
    args.work_root.mkdir(parents=True, exist_ok=True)
    # Not mkdtemp: on Windows it creates an owner-only ACL that the Codex sandbox user cannot enter.
    workdir = args.work_root / f"combo-compare-{uuid.uuid4().hex[:10]}"
    workdir.mkdir()
    try:
        shutil.copytree(case["_root"] / "fixtures" / case["fixture"], workdir, dirs_exist_ok=True)
        before_hashes = smoke.snapshot_tree(workdir)
        acceptance = case.get("acceptance", {})
        before_acc = run_acceptance_script(case["_root"] / acceptance["before"], workdir) if acceptance.get("before") else None
        events, timed_out = execute(host, case, arm, args, workdir)
        info = analyze_claude(events) if host == "claude" else analyze_codex(events)
        after_acc = run_acceptance_script(case["_root"] / acceptance["after"], workdir) if acceptance.get("after") else None
        changed = smoke.changed_files(before_hashes, smoke.snapshot_tree(workdir))
        failures = score_outcome(case, info["answer"], changed, before_acc, after_acc,
                                 info["commands"], info["tool_count"], workdir)
        if timed_out:
            failures.append(f"timeout after {args.timeout}s")
        record = {"host": host, "arm": arm, "case": case["id"], "rep": rep, "model": args.model,
                  "passed": not failures, "failures": failures, "timed_out": timed_out,
                  "changed": [c["path"] for c in changed], "seconds": round(time.time() - started, 1),
                  **{k: info[k] for k in ("tool_count", "workflow_loaded", "skills", "turns", "cost_usd",
                                          "tokens_total", "output_tokens")},
                  "final_answer": info["answer"][:1500]}
        (out_dir / f"{tag}.events.jsonl").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in events), encoding="utf-8")
    except Exception as error:  # one broken session must not discard the others
        record = {"host": host, "arm": arm, "case": case["id"], "rep": rep, "passed": False,
                  "failures": [f"harness error: {error!r}"], "tool_count": 0, "workflow_loaded": False,
                  "tokens_total": 0, "cost_usd": None, "seconds": round(time.time() - started, 1)}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    saved.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def _mean(raw: list[Any]) -> str:
    values = [v for v in raw if v is not None]
    return f"{statistics.mean(values):.0f}" if values else "-"


def summarize(records: list[dict[str, Any]]) -> str:
    lines = ["# Outcome comparison", ""]
    groups = sorted({(r["host"], r["arm"]) for r in records})
    lines += ["| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for host, arm in groups:
        rows = [r for r in records if (r["host"], r["arm"]) == (host, arm)]
        cost = sum(r.get("cost_usd") or 0 for r in rows)
        lines.append(f"| {host} | {arm} | {len(rows)} | {sum(r['passed'] for r in rows)}/{len(rows)} | "
                     f"{sum(bool(r.get('workflow_loaded')) for r in rows)} | "
                     f"{_mean([r['tool_count'] for r in rows])} | {_mean([r['tokens_total'] for r in rows])} | "
                     f"{_mean([r.get('seconds') for r in rows])} | {cost:.2f} |")
    lines += ["", "| host | case | " + " | ".join(f"{h}/{a}" for h, a in groups) + " |"]
    lines.append("| --- | --- | " + " | ".join("---" for _ in groups) + " |")
    for case_id in dict.fromkeys(r["case"] for r in records):
        cells = []
        for host, arm in groups:
            rows = [r for r in records if (r["host"], r["arm"], r["case"]) == (host, arm, case_id)]
            cells.append(f"{sum(r['passed'] for r in rows)}/{len(rows)}" if rows else "-")
        lines.append(f"| | {case_id} | " + " | ".join(cells) + " |")
    failed = [r for r in records if not r["passed"]]
    if failed:
        lines += ["", "Failures:"]
        lines += [f"- {r['host']}/{r['arm']} {r['case']} r{r['rep']}: {'; '.join(r['failures'])[:200]}" for r in failed]
    lines += ["", "Tokens are host-specific counters and not comparable across hosts; cost is only reported "
              "by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result."]
    return "\n".join(lines) + "\n"


def rescore(directory: Path) -> list[dict[str, Any]]:
    """Re-evaluate only the implementation-claim check on stored records (scorer fix; no model calls)."""
    claim = "claims implementation at a plan/review boundary"
    records = []
    for path in sorted(directory.glob("*.r[0-9]*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if claim in record.get("failures", []) and not claims_implementation(record.get("final_answer", "")):
            record["failures"] = [f for f in record["failures"] if f != claim]
            record["passed"] = not record["failures"]
            record["rescored"] = "claim check made negation-aware"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        records.append(record)
    return records


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rescore", type=Path, help="re-evaluate the claim check on a results directory and exit")
    p.add_argument("--host", choices=["claude", "codex"])
    p.add_argument("--arms", nargs="+", default=None)
    p.add_argument("--cases", nargs="*")
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--model", default=None, help="claude default: sonnet; codex default: gpt-6-luna")
    p.add_argument("--effort", default="high", help="codex reasoning effort")
    p.add_argument("--max-turns", type=int, default=30)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--codex-home", action="append", default=[], metavar="NAME=PATH",
                   help="prepared CODEX_HOME; adds arm home:NAME (repeatable)")
    p.add_argument("--work-root", type=Path, default=Path("D:/combo-workflow-evals"))
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args(argv)
    if args.rescore:
        return args
    if not args.host:
        p.error("--host is required")
    args.model = args.model or ("sonnet" if args.host == "claude" else "gpt-6-luna")
    args.codex_homes = dict(item.split("=", 1) for item in args.codex_home)
    valid = set(CLAUDE_ARMS) if args.host == "claude" else set(CODEX_ARMS) | {f"home:{n}" for n in args.codex_homes}
    args.arms = args.arms or ["full"]
    for arm in args.arms:
        if arm not in valid:
            p.error(f"arm {arm!r} is not defined for {args.host}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.rescore:
        records = rescore(args.rescore)
        (args.rescore / "summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        report = summarize(records)
        (args.rescore / "summary.md").write_text(report, encoding="utf-8")
        print(report)
        return 0
    args.claude = shutil.which("claude")
    if args.host == "claude" and not args.claude:
        print("claude CLI not found on PATH")
        return 2
    cases = [c for c in load_cases() if not args.cases or c["id"] in args.cases]
    out_dir = args.output or ROOT / "evals" / "compare" / "results" / time.strftime("run-%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(arm, case, rep) for rep in range(1, args.repeats + 1) for case in cases for arm in args.arms]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(lambda j: run_one(args.host, j[0], j[1], j[2], args, out_dir), jobs))
    (out_dir / "summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    report = summarize(records)
    (out_dir / "summary.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
