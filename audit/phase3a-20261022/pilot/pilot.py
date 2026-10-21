"""P0 compaction pilot runner and scorer (arm A only for now). See ../PILOT-PRE-REGISTRATION.md.

    py -I pilot.py run   --tag smoke1 --limit 80000 [--effort high]
    py -I pilot.py score --tag smoke1                      # re-score a saved run, no model call

A run builds the fixture in D:\\combo-workflow-evals\\pilot-<tag>, runs one `codex exec` with the owner's real
config EXCEPT mcp servers (disabled as in scripts/run-workflow-smoke.py) and with model_auto_compact_token_limit
forced, then locates the saved rollout, and scores it. Hooks stay on (context-mode, mb-recall, nah): arm A is
"current setup". Raw rollout copies go to the session scratchpad via --keep-dir; only the score JSON is committed.
"""
import argparse, glob, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK_ROOT = Path("D:/combo-workflow-evals")
MODEL = "gpt-6-luna"

PROMPT = """Work in this repository through three steps, in order. Finish and verify each step before starting the next. Do not edit anything under tests/. Run tests with `py -m unittest <module>` from the repository root.

Step 1: make tests.test_money pass (money parsing).
Step 2: make tests.test_report pass (order totals are wrong).
Step 3: the CLI default currency must be EUR as documented in docs/cli.md; make tests.test_cli pass. Work out which configuration source actually controls it before changing anything.

When all three modules pass, reply with the files you changed and one line per step."""

EDIT = re.compile(r"apply_patch|Set-Content|Add-Content|Out-File|WriteAllText|\*\*\* (?:Update|Add|Delete) File|-replace\b", re.I)
STATE = re.compile(r"STATUS\.md|HANDOFF|PROGRESS|NOTES?\.md|CHECKPOINT|TODO\.md", re.I)


def load_smoke():
    spec = importlib.util.spec_from_file_location("smoke", ROOT / "scripts" / "run-workflow-smoke.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["smoke"] = mod
    spec.loader.exec_module(mod)
    return mod


def tree_hash(path):
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(p.relative_to(path).as_posix().encode() + p.read_bytes())
    return h.hexdigest()


def find_rollout(workdir, since):
    want = str(workdir).replace("\\", "/").lower().rstrip("/")
    for f in sorted(glob.glob(str(Path.home() / ".codex/sessions/**/rollout-*.jsonl"), recursive=True),
                    key=os.path.getmtime, reverse=True):
        if os.path.getmtime(f) < since:
            break
        with open(f, encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
        try:
            cwd = (json.loads(first).get("payload") or {}).get("cwd", "")
        except ValueError:
            continue
        if cwd.replace("\\", "/").lower().rstrip("/").lstrip("/").endswith(want.lstrip("/")):
            return Path(f)
    return None


def parse_rollout(path):
    """Ordered calls with their outputs, compaction positions (as call counts), token_count samples."""
    calls, outputs, compactions, tokens = [], {}, [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        t, p = o.get("type"), o.get("payload") or {}
        if t == "compacted":
            compactions.append(len(calls))
        elif t == "response_item":
            pt = p.get("type")
            if pt in ("custom_tool_call", "function_call"):
                text = p.get("input") if isinstance(p.get("input"), str) else json.dumps(p.get("arguments", ""))
                calls.append({"id": p.get("call_id"), "text": text})
            elif pt in ("custom_tool_call_output", "function_call_output"):
                out = p.get("output")
                if isinstance(out, list):  # [{'type': 'input_text', 'text': ...}, ...]
                    out = "".join(x.get("text", "") for x in out if isinstance(x, dict))
                outputs[p.get("call_id")] = out if isinstance(out, str) else json.dumps(out)
        elif t == "event_msg" and p.get("type") == "token_count":
            info = p.get("info") or {}
            tokens.append({"total": info.get("total_token_usage"), "last": info.get("last_token_usage"),
                           "pct": ((p.get("rate_limits") or {}).get("primary") or {}).get("used_percent")})
    for c in calls:
        c["out"] = outputs.get(c["id"], "")
    return calls, compactions, tokens


def touches(call, name):
    return bool(EDIT.search(call["text"])) and name in call["text"]


def test_result(call, module):
    if module not in call["text"] or "unittest" not in call["text"]:
        return None
    out = call["out"].replace(chr(92) + "r" + chr(92) + "n", chr(10)).replace(chr(92) + "n", chr(10)).replace(chr(13), "")  # output may be JSON-escaped text
    if re.search(r"\bFAILED\b|\bERROR:|\bFAIL:", out):
        return "fail"
    if re.search(r"(^|\n)OK\b", out):
        return "ok"
    return "unknown"


def score_rollout(calls, compactions, tokens):
    idx = lambda pred: next((i for i, c in enumerate(calls) if pred(c)), None)
    v1 = idx(lambda c: test_result(c, "test_money") == "ok")
    v2 = idx(lambda c: test_result(c, "test_report") == "ok")
    report_edit = idx(lambda c: touches(c, "report.py") or touches(c, "fmt.py"))
    report_fail_after_edit = None
    if report_edit is not None:
        report_fail_after_edit = next(
            (i for i, c in enumerate(calls) if i > report_edit and test_result(c, "test_report") == "fail"), None)
    # The analysed cut is the first compaction that falls after step 1 was verified and before step 2 was
    # (a "critical" cut); with none, the first compaction is analysed and cut_mid_step2 is false.
    critical = [c for c in compactions if v1 is not None and c > v1 and (v2 is None or c <= v2)]
    first_cut = critical[0] if critical else (compactions[0] if compactions else None)
    res = {"calls": len(calls), "compactions": compactions, "verified_step1_at": v1, "verified_step2_at": v2}
    if first_cut is not None:
        post = calls[first_cut:]
        first_edit = next((i for i, c in enumerate(post) if EDIT.search(c["text"])), None)
        res.update({
            "cut_mid_step2": v1 is not None and v1 < first_cut and (v2 is None or v2 >= first_cut),
            "failed_attempt_before_cut": bool(report_edit is not None and report_edit < first_cut
                                              and report_fail_after_edit is not None and report_fail_after_edit < first_cut),
            "post_cut_calls": len(post),
            "step1_files_edited_after_cut": sum(touches(c, "money.py") for c in post),
            "step1_test_rerun_after_cut": sum(test_result(c, "test_money") is not None for c in post),
            "report_py_edited_after_cut": sum(touches(c, "report.py") for c in post),
            "settings_json_edited_after_cut": sum(touches(c, "settings.json") for c in post),
            "readonly_calls_before_first_edit_after_cut": first_edit if first_edit is not None else len(post),
            "state_file_calls_after_cut": sum(bool(STATE.search(c["text"])) for c in post),
        })
    res["settings_json_edited_anywhere"] = sum(touches(c, "settings.json") for c in calls)
    res["defaults_toml_edited_anywhere"] = sum(touches(c, "defaults.toml") for c in calls)
    last = next((t for t in reversed(tokens) if t["total"]), None)
    pcts = [t["pct"] for t in tokens if t["pct"] is not None]
    if last:
        tot = last["total"]
        res["tokens"] = {"input": tot.get("input_tokens"), "cached_input": tot.get("cached_input_tokens"),
                         "output": tot.get("output_tokens"), "total": tot.get("total_tokens")}
    ctx = [t["last"]["input_tokens"] for t in tokens if t.get("last") and t["last"].get("input_tokens")]
    res["context_tokens_max"] = max(ctx) if ctx else None
    res["plan_used_percent"] = {"first": pcts[0] if pcts else None, "last": pcts[-1] if pcts else None}
    return res


def acceptance(workdir):
    r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_money", "tests.test_report", "tests.test_cli"],
                       cwd=workdir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0, (r.stderr or "")[-300:]


def cmd_run(a):
    smoke = load_smoke()
    sys.path.insert(0, str(HERE))
    import fixture
    workdir = WORK_ROOT / f"pilot-{a.tag}"
    if workdir.exists():
        raise SystemExit(f"{workdir} exists; pick a new tag")
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    workdir.mkdir()
    fixture.build(workdir)
    tests_hash = tree_hash(workdir / "tests")
    launcher, cli = smoke.find_cli(None)
    command = smoke.cli_prefix(launcher, cli) + [
        "exec", "--json", "--skip-git-repo-check", "--model", MODEL,
        "-c", f"model_reasoning_effort={a.effort}", "-c", 'approval_policy="never"', "-c", "mcp_servers={}",
        "-c", f"model_auto_compact_token_limit={a.limit}", "-s", "workspace-write", "-C", str(workdir)]
    for name in smoke.configured_mcp_names():
        command += ["-c", f"mcp_servers.{name}.enabled=false"]
    started = time.time()
    proc = subprocess.Popen(command, cwd=workdir, text=True, encoding="utf-8", errors="replace",
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    timer = threading.Timer(a.timeout, lambda: smoke.terminate_owned_process_tree(proc))
    timer.start()
    try:
        out, _ = proc.communicate(PROMPT)
    finally:
        timer.cancel()
    seconds = round(time.time() - started)
    keep = Path(a.keep_dir)
    keep.mkdir(parents=True, exist_ok=True)
    (keep / f"{a.tag}.stdout.jsonl").write_text(out or "", encoding="utf-8")
    rollout = find_rollout(workdir, started - 5)
    if rollout:
        shutil.copy(rollout, keep / f"{a.tag}.rollout.jsonl")
    ok, tail = acceptance(workdir)
    record = {"tag": a.tag, "arm": "A", "model": MODEL, "effort": a.effort, "limit": a.limit, "seconds": seconds,
              "acceptance_pass": ok, "tests_unchanged": tree_hash(workdir / "tests") == tests_hash,
              "rollout_found": bool(rollout)}
    if rollout:
        record.update(score_rollout(*parse_rollout(rollout)))
    out_path = HERE / "results" / f"{a.tag}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(json.dumps(record, indent=1))


def cmd_score(a):
    keep = Path(a.keep_dir)
    rollout = keep / f"{a.tag}.rollout.jsonl"
    print(json.dumps(score_rollout(*parse_rollout(rollout)), indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "score"):
        p = sub.add_parser(name)
        p.add_argument("--tag", required=True)
        p.add_argument("--keep-dir", default=str(Path(os.environ.get("TEMP", ".")) / "combo-pilot"))
        if name == "run":
            p.add_argument("--limit", type=int, required=True)
            p.add_argument("--effort", default="high")
            p.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    {"run": cmd_run, "score": cmd_score}[a.cmd](a)


if __name__ == "__main__":
    main()
