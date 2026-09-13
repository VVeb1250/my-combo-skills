"""Run matched A/B Combo cases with isolated fixtures and per-process overrides."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "evals" / "ab"
CASES = AB / "cases.json"
FIXTURES = AB / "fixtures"
ACCEPTANCE = AB / "acceptance"
STAGE = AB / "stage_variants.py"
DEFAULT_WORK = Path("D:/combo-ab-evals")
TRANSIENT = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
ROUTE_HINTS = ("combo", "matt-", "ecc-", "ponytail", "workflows/", "practices/")
SMOKE_SPEC = importlib.util.spec_from_file_location(
    "smoke", ROOT / "scripts" / "run-workflow-smoke.py"
)
if SMOKE_SPEC is None or SMOKE_SPEC.loader is None:
    raise RuntimeError("cannot import smoke helpers")
SMOKE = importlib.util.module_from_spec(SMOKE_SPEC)
SMOKE_SPEC.loader.exec_module(SMOKE)


def load_suite() -> dict[str, Any]:
    suite = json.loads(CASES.read_text(encoding="utf-8"))
    if suite.get("schema_version") != 1 or suite.get("model") != "gpt-5.6-luna":
        raise ValueError("invalid A/B suite")
    if suite.get("reasoning_effort") != "max" or suite.get("max_parallel") != 2:
        raise ValueError("A/B suite must be Luna max with max_parallel 2")
    if not 180 <= int(suite.get("timeout_seconds", 0)) <= 240:
        raise ValueError("A/B timeout must be between 180 and 240 seconds")
    cases = suite.get("cases")
    if not isinstance(cases, list) or len(cases) != 10:
        raise ValueError("A/B suite must contain ten cases")
    ids = set()
    for case in cases:
        cid = case.get("id")
        if not isinstance(cid, str) or cid in ids:
            raise ValueError("duplicate or missing case id")
        ids.add(cid)
        fixture = (FIXTURES / str(case.get("fixture", ""))).resolve()
        if fixture.parent != FIXTURES.resolve() or not fixture.is_dir():
            raise ValueError(f"missing fixture for {cid}")
        prompt = str(case.get("prompt", ""))
        if len(prompt.strip()) < 20 or any(x in prompt.lower() for x in ROUTE_HINTS):
            raise ValueError(f"invalid or hinted prompt for {cid}")
        if case.get("sandbox") not in {"read-only", "workspace-write"}:
            raise ValueError(f"invalid sandbox for {cid}")
    if suite.get("coverage", {}).get("source_packs") != [
        "karpathy",
        "ponytail",
        "matt",
        "ecc",
    ]:
        raise ValueError("all four source packs must be declared")
    return suite


def global_combo_path(explicit: Path | None = None) -> Path:
    candidates = [explicit] if explicit else []
    configured = os.environ.get("CODEX_HOME")
    if configured:
        candidates.append(Path(configured) / "skills" / "combo" / "SKILL.md")
    candidates.extend(
        [
            Path.home() / ".codex" / "skills" / "combo" / "SKILL.md",
            Path.home() / ".agents" / "skills" / "combo" / "SKILL.md",
        ]
    )
    for candidate in candidates:
        if candidate is not None and candidate.expanduser().resolve().is_file():
            return candidate.expanduser().resolve()
    raise FileNotFoundError("installed global Combo SKILL.md not found")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snapshot(root: Path) -> dict[str, dict[str, Any]]:
    out = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(
            p in TRANSIENT for p in path.relative_to(root).parts
        ):
            continue
        rel = path.relative_to(root)
        if rel.parts[:2] == (".agents", "skills") or path.suffix.lower() in {
            ".pyc",
            ".pyo",
        }:
            continue
        out[rel.as_posix()] = {"sha256": sha(path), "bytes": path.stat().st_size}
    return out


def diff(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    for rel in sorted(set(before) | set(after)):
        if before.get(rel) == after.get(rel):
            continue
        old, new = before.get(rel), after.get(rel)
        rows.append(
            {
                "path": rel,
                "change": "created"
                if old is None
                else "deleted"
                if new is None
                else "modified",
                "before_sha256": old and old["sha256"],
                "after_sha256": new and new["sha256"],
                "before_bytes": old and old["bytes"],
                "after_bytes": new and new["bytes"],
            }
        )
    return rows


def toml_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {toml_value(x)}" for k, x in v.items()) + " }"
    raise ValueError(f"unsupported TOML value {v!r}")


def rows_for(variant_root: Path, global_combo: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    config = variant_root / "process" / "skills.config.toml"
    if config.is_file():
        import tomllib

        data = tomllib.loads(config.read_text(encoding="utf-8-sig"))
        skills = data.get("skills", {})
        raw = skills.get("config", []) if isinstance(skills, dict) else []
        if isinstance(raw, dict):
            raw = [raw]
        rows = [dict(x) for x in raw if isinstance(x, dict)]
    target = str(global_combo.resolve())
    found = False
    for row in rows:
        if row.get("path") == target:
            row["enabled"] = False
            found = True
    if not found:
        rows.append({"path": target, "enabled": False})
    return rows


def skills_override(rows: list[dict[str, Any]]) -> str:
    return (
        "skills.config=["
        + ", ".join(
            "{" + ", ".join(f"{k} = {toml_value(v)}" for k, v in row.items()) + "}"
            for row in rows
        )
        + "]"
    )


def trust_override(cwd: Path) -> str:
    normalized = str(cwd.resolve()).lower() if os.name == "nt" else str(cwd.resolve())
    return (
        f'projects."{normalized.replace(chr(92), chr(92) * 2)}".trust_level="trusted"'
    )


def command(
    cli: Path,
    suite: dict[str, Any],
    case: dict[str, Any],
    cwd: Path,
    rows: list[dict[str, Any]],
    mcp: list[str],
) -> list[str]:
    cmd = [
        str(cli),
        "exec",
        "--json",
        "--ephemeral",
        "--color",
        "never",
        "--disable",
        "hooks",
        "--disable",
        "multi_agent",
        "--disable",
        "memories",
        "--skip-git-repo-check",
        "--model",
        suite["model"],
        "-c",
        f"model_reasoning_effort={suite['reasoning_effort']}",
        "-c",
        'approval_policy="never"',
        "-c",
        "mcp_servers={}",
        "-c",
        skills_override(rows),
        "-c",
        trust_override(cwd),
        "-s",
        "danger-full-access",
        "-C",
        str(cwd),
    ]
    for name in mcp:
        cmd += ["-c", f"mcp_servers.{name}.enabled=false"]
    return cmd


def copy_fixture(variant_root: Path, name: str, cwd: Path) -> None:
    shutil.copytree(
        variant_root / "fixtures" / name, cwd, symlinks=True, dirs_exist_ok=True
    )
    skills = cwd / ".agents" / "skills"
    if skills.is_symlink() or skills.is_file():
        skills.unlink()
    elif skills.exists():
        if skills.resolve() != cwd.resolve() / ".agents" / "skills":
            raise ValueError("Refusing cleanup outside this fixture")
        shutil.rmtree(skills)
    skills.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(variant_root / "skills", skills, symlinks=False)


def acceptance(name: str, cwd: Path) -> dict[str, Any]:
    target = (ACCEPTANCE / name).resolve()
    if target.parent != ACCEPTANCE.resolve() or not target.is_file():
        raise ValueError(f"invalid acceptance {name}")
    env = os.environ.copy()
    env["COMBO_EVAL_ROOT"] = str(cwd)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        p = subprocess.run(
            [sys.executable, str(target)],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        return {
            "returncode": p.returncode,
            "passed": p.returncode == 0,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "returncode": None,
            "passed": False,
            "timed_out": True,
            "stdout": _text(e.stdout),
            "stderr": _text(e.stderr),
        }


def _text(v: bytes | str | None) -> str:
    return (
        "" if v is None else v.decode("utf-8", "replace") if isinstance(v, bytes) else v
    )


def is_write_like(command_text: str) -> bool:
    # PowerShell's null stream redirection does not write a file.
    without_null_redirect = re.sub(
        r"(?i)(?:[0-9]|\*)?>>?\s*[\"']*\$null\b[\"']*", "", command_text
    )
    return bool(SMOKE.WRITE_COMMAND_RE.search(without_null_redirect))


def run_arm(
    cli: Path,
    suite: dict[str, Any],
    case: dict[str, Any],
    variant: str,
    variant_root: Path,
    global_combo: Path,
    mcp: list[str],
    output: Path,
    work_root: Path,
    timeout: int,
    pair: int,
    first: str,
    keep: bool,
) -> dict[str, Any]:
    cid = case["id"]
    started = time.monotonic()
    cwd = Path(tempfile.mkdtemp(prefix=f"combo-ab-{cid}-{variant}-", dir=work_root))
    copy_fixture(variant_root, case["fixture"], cwd)
    before = snapshot(cwd)
    instruction_hashes = {
        str(p.relative_to(cwd)): sha(p)
        for p in (cwd / ".agents/skills").rglob("*")
        if p.is_file()
    }
    before_accept = None
    spec = case.get("acceptance", {})
    if spec.get("before"):
        before_accept = acceptance(spec["before"], cwd)
    rows = rows_for(variant_root, global_combo)
    cmd = command(cli, suite, case, cwd, rows, mcp)
    stdout = stderr = ""
    rc = None
    timed = False
    error = None
    try:
        p = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=os.environ.copy(),
        )
        try:
            stdout, stderr = p.communicate(case["prompt"], timeout=timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired as e:
            timed = True
            stdout, stderr = _text(e.stdout), _text(e.stderr)
            SMOKE.terminate_owned_process_tree(p)
            try:
                tail_out, tail_err = p.communicate(timeout=5)
                stdout = tail_out or stdout
                stderr = tail_err or stderr
            except subprocess.TimeoutExpired:
                p.kill()
                tail_out, tail_err = p.communicate()
                stdout += tail_out or ""
                stderr += tail_err or ""
            rc = p.returncode
    except OSError as e:
        error = repr(e)
    after_accept = acceptance(spec["after"], cwd) if spec.get("after") else None
    after = snapshot(cwd)
    events, parse_errors = SMOKE.parse_events(stdout)
    answer = SMOKE.final_answer(events)
    tools = SMOKE.tool_events(events)
    refs, ref_evidence = SMOKE.actual_references(events)
    # Keep raw command output in events.jsonl. Summary/result metadata should
    # carry only hashes and byte counts so a twenty-arm run stays inspectable.
    ref_evidence = [
        {key: value for key, value in row.items() if key != "output"}
        for row in ref_evidence
    ]
    requested = [str(x) for x in case.get("required_actual_files", [])]
    files, file_evidence = SMOKE.actual_files_read(
        events, cwd, requested, case.get("required_actual_file_markers", {})
    )
    writes = [
        {"item_id": t.get("item_id"), "command": t.get("command")}
        for t in tools
        if isinstance(t.get("command"), str) and is_write_like(t["command"])
    ]
    changed = diff(before, after)
    failures = []
    environmental = []
    if error:
        environmental.append(f"process start failed: {error}")
    if timed:
        environmental.append(f"session exceeded {timeout}s")
    if rc not in (None, 0):
        environmental.append(f"Codex exited with {rc}")
    if not answer.strip():
        environmental.append("no final answer captured")
    if spec.get("before_must_fail") and (
        before_accept is None or before_accept["passed"]
    ):
        failures.append("seeded before acceptance did not fail")
    if spec.get("after_must_pass") and (
        after_accept is None or not after_accept["passed"]
    ):
        failures.append("independent after acceptance did not pass")
    if case.get("no_writes") and (changed or writes):
        failures.append("read-only case changed files or emitted write command")
    allowed = set(case.get("allowed_changed_paths", []))
    if allowed and any(
        x["path"] not in allowed and not x["path"].startswith("tests/") for x in changed
    ):
        failures.append("changed files outside allowed scope")
    required_change = set(case.get("required_changed_paths", []))
    if required_change and not required_change <= {x["path"] for x in changed}:
        failures.append("required files were not changed")
    if requested and not set(requested) <= set(files):
        failures.append("required fixture files were not observed in successful reads")
    if case.get("no_tools") and tools:
        failures.append("case emitted tool events")
    if case.get("required_final_unicode_range") == "thai" and not re.search(
        r"[\u0e00-\u0e7f]", answer
    ):
        failures.append("final answer has no Thai text")
    after_instructions = {
        str(p.relative_to(cwd)): sha(p)
        for p in (cwd / ".agents/skills").rglob("*")
        if p.is_file()
    }
    if instruction_hashes != after_instructions:
        failures.append("candidate instructions changed during execution")
    result_dir = output / "arms" / variant / cid
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "events.jsonl").write_text(stdout, encoding="utf-8")
    (result_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
    (result_dir / "prompt.txt").write_text(case["prompt"], encoding="utf-8")
    (result_dir / "final-answer.txt").write_text(answer, encoding="utf-8")
    (result_dir / "before-hashes.json").write_text(
        json.dumps(before, indent=2) + "\n", encoding="utf-8"
    )
    (result_dir / "after-hashes.json").write_text(
        json.dumps(after, indent=2) + "\n", encoding="utf-8"
    )
    (result_dir / "acceptance.json").write_text(
        json.dumps({"before": before_accept, "after": after_accept}, indent=2) + "\n",
        encoding="utf-8",
    )
    (result_dir / "tool-events.json").write_text(
        json.dumps(
            [
                {
                    k: x.get(k)
                    for k in (
                        "event_type",
                        "item_id",
                        "item_type",
                        "command",
                        "status",
                        "exit_code",
                    )
                }
                for x in tools
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = {
        "case_id": cid,
        "variant": variant,
        "pair_index": pair,
        "first_arm": first,
        "fixture": case["fixture"],
        "requested_sandbox": case["sandbox"],
        "effective_sandbox": "danger-full-access",
        "model": suite["model"],
        "reasoning_effort": suite["reasoning_effort"],
        "command": cmd,
        "workdir": str(cwd) if keep else None,
        "returncode": rc,
        "timed_out": timed,
        "process_error": error,
        "duration_seconds": round(time.monotonic() - started, 3),
        "events_path": str(result_dir / "events.jsonl"),
        "stderr_path": str(result_dir / "stderr.txt"),
        "final_answer_path": str(result_dir / "final-answer.txt"),
        "final_answer": answer,
        "parse_errors": parse_errors,
        "tool_count": len(tools),
        "tool_events_path": str(result_dir / "tool-events.json"),
        "actual_references": refs,
        "reference_evidence": ref_evidence,
        "actual_fixture_files_read": files,
        "fixture_read_evidence": file_evidence,
        "changed_files": changed,
        "before_hashes_path": str(result_dir / "before-hashes.json"),
        "after_hashes_path": str(result_dir / "after-hashes.json"),
        "acceptance_path": str(result_dir / "acceptance.json"),
        "acceptance": {
            "before": before_accept
            and {
                "passed": before_accept["passed"],
                "returncode": before_accept["returncode"],
            },
            "after": after_accept
            and {
                "passed": after_accept["passed"],
                "returncode": after_accept["returncode"],
            },
        },
        "usage": SMOKE.usage_from_events(events),
        "write_like_commands": writes,
        "environment_failures": environmental,
        "task_failures": failures,
        "classification": "environmental"
        if environmental
        else "task"
        if failures
        else "passed",
    }
    result["result_path"] = str(result_dir / "result.json")
    (result_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not keep:
        if cwd.resolve().parent != work_root.resolve() or not cwd.name.startswith(
            "combo-ab-"
        ):
            raise ValueError("Refusing cleanup outside the owned run directory")
        shutil.rmtree(cwd, ignore_errors=True)
    return result


def stage(
    package: Path,
    fixture_root: Path,
    destination: Path,
    global_combo: Path,
    manifest: Path,
) -> Path:
    spec = importlib.util.spec_from_file_location("stage_variants", STAGE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import stage_variants")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build(
        package=package,
        fixtures_root=fixture_root,
        output=destination,
        global_combo_path=global_combo,
        entry_manifest=manifest,
    )
    return destination


def compact(result: dict[str, Any]) -> dict[str, Any]:
    return {
        k: result.get(k)
        for k in (
            "case_id",
            "variant",
            "pair_index",
            "first_arm",
            "classification",
            "returncode",
            "timed_out",
            "duration_seconds",
            "final_answer",
            "actual_fixture_files_read",
            "changed_files",
            "tool_count",
            "usage",
            "environment_failures",
            "task_failures",
            "result_path",
        )
    }


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--case", action="append", dest="case_ids")
    p.add_argument("--variants", type=Path)
    p.add_argument("--stage-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--output", type=Path)
    p.add_argument(
        "--resume",
        action="store_true",
        help="Reuse completed arms; retry only environmental failures",
    )
    p.add_argument("--work-root", type=Path, default=DEFAULT_WORK)
    p.add_argument(
        "--package", type=Path, default=ROOT / "candidates" / "common" / "combo"
    )
    p.add_argument("--fixtures-root", type=Path, default=FIXTURES)
    p.add_argument(
        "--entry-manifest", type=Path, default=AB / "variants" / "entry-manifest.json"
    )
    p.add_argument("--global-combo-path", type=Path)
    p.add_argument("--cli")
    p.add_argument("--timeout", type=int, default=240)
    p.add_argument("--max-parallel", type=int, default=2)
    p.add_argument("--cleanup-workdirs", action="store_true")
    return p.parse_args()


def main() -> int:
    a = args()
    suite = load_suite()
    all_cases = {x["id"]: x for x in suite["cases"]}
    if a.case_ids:
        unknown = set(a.case_ids) - set(all_cases)
        if unknown:
            raise SystemExit("unknown case: " + ", ".join(sorted(unknown)))
        cases = [all_cases[x] for x in a.case_ids]
    else:
        cases = suite["cases"]
    if a.timeout < 180 or a.timeout > 600 or a.max_parallel not in (1, 2):
        raise SystemExit("timeout must be 180..600 and max_parallel 1..2")
    global_combo = global_combo_path(a.global_combo_path)
    work = a.work_root.resolve()
    work.mkdir(parents=True, exist_ok=True)
    stage_root = (
        a.variants.resolve()
        if a.variants
        else work / ("staged-" + time.strftime("%Y%m%d-%H%M%S"))
    )
    if not a.variants:
        stage(
            a.package.resolve(),
            a.fixtures_root.resolve(),
            stage_root,
            global_combo,
            a.entry_manifest.resolve(),
        )
    if a.stage_only:
        print(
            json.dumps(
                {
                    "status": "staged",
                    "variants": str(stage_root),
                    "global_combo_path": str(global_combo),
                },
                indent=2,
            )
        )
        return 0
    if a.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "variants": str(stage_root),
                    "cases": [x["id"] for x in cases],
                    "pairs": len(cases) * 2,
                    "model": suite["model"],
                    "reasoning_effort": suite["reasoning_effort"],
                    "timeout_seconds": a.timeout,
                    "max_parallel": a.max_parallel,
                },
                indent=2,
            )
        )
        return 0
    cli = Path(a.cli).resolve() if a.cli else SMOKE.find_cli()[1]
    output = (
        a.output.resolve()
        if a.output
        else AB / "results" / ("run-" + time.strftime("%Y%m%d-%H%M%S"))
    )
    output.mkdir(parents=True, exist_ok=a.resume)
    mcp = SMOKE.configured_mcp_names()
    discoveries = {}
    # Discovery is a separate read-only app-server probe. The raw output is
    # retained by the existing inventory utility; failures remain environmental.
    for variant in ("A", "B"):
        dpath = output / "discovery" / f"{variant}.json"
        cwd = stage_root / variant / "fixtures" / cases[0]["fixture"]
        try:
            env = os.environ.copy()
            p = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex_inventory.py"),
                    "--output",
                    str(dpath),
                    "--cwd",
                    str(cwd),
                    "--config",
                    skills_override(rows_for(stage_root / variant, global_combo)),
                    "--config",
                    trust_override(cwd),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                env=env,
                check=False,
            )
            discoveries[variant] = {
                "returncode": p.returncode,
                "path": str(dpath),
                "stderr": p.stderr,
                "status": "passed" if p.returncode == 0 else "environmental",
            }
        except (OSError, subprocess.TimeoutExpired) as e:
            discoveries[variant] = {
                "status": "environmental",
                "error": repr(e),
                "path": str(dpath),
            }
    root = Path(tempfile.mkdtemp(prefix="combo-ab-run-", dir=work))
    results = []

    def execute(case, variant, index, first):
        previous_path = output / "arms" / variant / case["id"] / "result.json"
        if a.resume and previous_path.is_file():
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
            if previous.get("classification") != "environmental":
                return previous
            archived = (
                output
                / "attempts"
                / time.strftime("%Y%m%d-%H%M%S")
                / variant
                / case["id"]
            )
            archived.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(previous_path.parent, archived)
        return run_arm(
            cli,
            suite,
            case,
            variant,
            stage_root / variant,
            global_combo,
            mcp,
            output,
            root,
            a.timeout,
            index,
            first,
            not a.cleanup_workdirs,
        )

    for case in cases:
        index = list(all_cases).index(case["id"])
        first = "A" if index % 2 == 0 else "B"
        second = "B" if first == "A" else "A"
        with ThreadPoolExecutor(max_workers=a.max_parallel) as pool:
            f1 = pool.submit(execute, case, first, index, first)
            f2 = pool.submit(execute, case, second, index, first)
            results.extend([f1.result(), f2.result()])
        print(f"{case['id']}: {first}/{second} complete", flush=True)
    summary = {
        "schema_version": 1,
        "suite": suite["suite"],
        "model": suite["model"],
        "reasoning_effort": suite["reasoning_effort"],
        "timeout_seconds": a.timeout,
        "max_parallel": a.max_parallel,
        "effective_sandbox": "danger-full-access",
        "environment_note": "Identical bundled PowerShell runtime and isolated full-access fixture execution for both arms.",
        "global_combo_path": str(global_combo),
        "variants": str(stage_root),
        "discovery": discoveries,
        "pair_order": [
            {"case_id": c["id"], "first_arm": "A" if i % 2 == 0 else "B"}
            for c in cases
            for i in [list(all_cases).index(c["id"])]
        ],
        "results": [
            compact(x)
            for x in sorted(results, key=lambda x: (x["pair_index"], x["variant"]))
        ],
        "result_files": [
            str(output / "arms" / x["variant"] / x["case_id"] / "result.json")
            for x in results
        ],
        "passed": sum(x["classification"] == "passed" for x in results),
        "environmental": sum(x["classification"] == "environmental" for x in results),
        "task_failures": sum(x["classification"] == "task" for x in results),
        "coverage_note": "Ten matched cases, paired by case with alternating first arm. Automatic checks support root semantic grading; route labels are not scored.",
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Summary: {output / 'summary.json'}")
    return 0 if summary["passed"] == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
