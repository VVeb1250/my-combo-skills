"""Pilot A (unavailable-is-not-clean) and B (MCQ validity), baseline arm only.

One bare `claude -p` session per case: no tools, no MCP, hooks off, CLAUDE.md files
off, no session persistence, empty temp cwd. Raw results go to ./results/<case>.json.
Pre-registered scoring lives in PRE-REGISTRATION.md and score.py; read that first.

    py run_pilot.py A1 A2 B1 B2 B3 [--model sonnet]
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def run(case_id: str, model: str) -> dict:
    prompt = CASES[case_id]["prompt"]
    work = Path(tempfile.mkdtemp(prefix="pilot-"))
    env = dict(os.environ, CLAUDE_CODE_DISABLE_CLAUDE_MDS="1")
    cmd = [
        shutil.which("claude") or "claude", "-p", prompt,
        "--output-format", "json", "--max-turns", "1", "--model", model,
        "--tools", "", "--strict-mcp-config",
        "--settings", '{"disableAllHooks":true}', "--no-session-persistence",
    ]
    try:
        proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True,
                              text=True, encoding="utf-8", timeout=180)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"error": "unparseable", "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    return {"case": case_id, "model": model, "returncode": proc.returncode, "result": data}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="+")
    ap.add_argument("--model", default="sonnet")
    a = ap.parse_args()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    for c in a.cases:
        r = run(c, a.model)
        (out / f"{c}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        res = r["result"]
        print(c, "rc", r["returncode"], "cost", res.get("total_cost_usd"), "turns", res.get("num_turns"), file=sys.stderr)
