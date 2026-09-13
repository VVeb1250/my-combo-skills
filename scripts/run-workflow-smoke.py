"""Run the fixture-backed Combo workflow smoke suite with native Codex CLI.

The harness deliberately measures observable work, rather than trusting a
skill name in the final answer. Each case runs in a fresh temporary directory,
and the model is never given the case's expected route or reference names.
This file only launches Codex processes when explicitly invoked by an operator;
the unit tests validate its setup without starting model sessions.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evals" / "v2"
CASES_FILE = EVAL_ROOT / "cases.json"
FIXTURES_ROOT = EVAL_ROOT / "fixtures"
TRANSIENT_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}

# These are only used to interpret captured events after a session. They never
# appear in prompts, so a model cannot satisfy a case by parroting the rubric.
KNOWN_SKILLS = {
    "combo",
    "matt-tdd",
    "matt-review",
    "matt-plan",
    "ecc-python",
    "ecc-security-review",
    "ponytail-review",
    "codex-research",
}
KNOWN_WORKFLOWS = {"debug", "deliver", "investigate", "plan", "review", "verify"}
KNOWN_PRACTICES = {"tests", "design", "simplicity", "security", "build", "e2e", "context", "delegation"}
TOOL_ITEM_TYPES = {
    "command_execution",
    "mcp_tool_call",
    "web_search_call",
    "file_change",
    "collab_tool_call",
    "computer_tool_call",
    "browser_tool_call",
}
WRITE_COMMAND_RE = re.compile(
    r"(?i)(?:\b(?:set-content|add-content|out-file|new-item|remove-item|rename-item|move-item|copy-item|apply_patch|git\s+(?:apply|commit|checkout|reset)|del\s|erase\s|rm\s|mv\s|cp\s)|>>|(?<![<>])>(?![=>]))"
)
THAI_RE = re.compile(r"[\u0e00-\u0e7f]")
IMPLEMENTATION_CLAIM_RE = re.compile(
    r"(?i)\b(?:i|we)\s+(?:have\s+)?(?:implemented|changed|modified|created|added|fixed)\b"
    r"|\b(?:implemented|modified|created|added)\s+(?:the|a|an)\s+(?:gateway|feature|fix)\b"
    r"|(?:แก้ไฟล์|สร้างไฟล์|เพิ่มไฟล์|ผมแก้|ฉันแก้)"
)


def load_suite(path: Path = CASES_FILE) -> dict[str, Any]:
    """Load and validate the static suite definition."""
    suite = json.loads(path.read_text(encoding="utf-8"))
    if suite.get("schema_version") != 2:
        raise ValueError("Unsupported eval suite schema")
    cases = suite.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise ValueError("v2 must contain exactly six cases")
    ids: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError(f"Invalid or duplicate case id: {case_id!r}")
        ids.add(case_id)
        fixture = FIXTURES_ROOT / str(case.get("fixture", ""))
        if not fixture.is_dir():
            raise ValueError(f"Fixture does not exist: {fixture}")
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Case {case_id} has no prompt")
        if case.get("sandbox") not in {"read-only", "workspace-write"}:
            raise ValueError(f"Case {case_id} has an unsupported sandbox")
    if suite.get("max_parallel") != 2 or suite.get("timeout_seconds") != 180:
        raise ValueError("v2 concurrency and timeout contract changed unexpectedly")
    return suite


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_tree(root: Path) -> dict[str, dict[str, Any]]:
    """Hash meaningful fixture files, ignoring interpreter caches."""
    result: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return result
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in TRANSIENT_DIRS for part in relative_parts):
            continue
        if path.suffix.lower() in TRANSIENT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    return result


def changed_files(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative in sorted(set(before) | set(after)):
        old = before.get(relative)
        new = after.get(relative)
        if old == new:
            continue
        rows.append(
            {
                "path": relative,
                "change": "created" if old is None else "deleted" if new is None else "modified",
                "before_sha256": old["sha256"] if old else None,
                "after_sha256": new["sha256"] if new else None,
                "before_bytes": old["bytes"] if old else None,
                "after_bytes": new["bytes"] if new else None,
            }
        )
    return rows


def find_cli(override: str | None = None) -> tuple[Path | None, Path]:
    """Return (launcher, native Codex executable).

    The npm ``codex.js`` file is only a wrapper that spawns the native binary.
    Prefer the binary directly so timeout cleanup cannot leave a child turn
    alive. ``--cli`` accepts either the native executable or its wrapper and is
    resolved to the sibling native binary in the latter case.
    """
    if override:
        requested = Path(override).expanduser().resolve()
    else:
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is unavailable; pass --cli explicitly")
        requested = (
            Path(appdata)
            / "npm"
            / "node_modules"
            / "@openai"
            / "codex"
            / "bin"
            / "codex.js"
        ).resolve()
    if requested.suffix.lower() == ".js":
        if not requested.is_file():
            raise FileNotFoundError(f"Installed Codex wrapper not found: {requested}")
        candidates = sorted(
            path
            for path in requested.parents[1].rglob("codex.exe" if os.name == "nt" else "codex")
            if path.is_file() and "vendor" in path.parts
        )
        if not candidates:
            raise FileNotFoundError(f"Native Codex executable not found beside: {requested}")
        return None, candidates[0].resolve()
    if not requested.is_file():
        raise FileNotFoundError(f"Native Codex CLI not found: {requested}")
    return None, requested


def cli_prefix(launcher: Path | None, executable: Path) -> list[str]:
    """Build the executable prefix, without spawning a wrapper process."""
    if launcher is None:
        return [str(executable)]
    return [str(launcher), str(executable)]


def build_command(
    launcher: Path | None,
    cli: Path,
    suite: dict[str, Any],
    case: dict[str, Any],
    workdir: Path,
    mcp_names: list[str] | None = None,
) -> list[str]:
    """Build one isolated, noninteractive Codex invocation."""
    command = cli_prefix(launcher, cli) + [
        "exec",
        "--json",
        "--ephemeral",
        "--disable",
        "hooks",
        "--disable",
        "multi_agent",
        "--disable",
        "memories",
        "--skip-git-repo-check",
        "--model",
        str(suite["model"]),
        "-c",
        f"model_reasoning_effort={suite['reasoning_effort']}",
        # No configured MCP server may start a background service or expose
        # memory/external-write surfaces during this local fixture run.
        "-c",
        "mcp_servers={}",
        "-c",
        'approval_policy="never"',
        "-s",
        str(case["sandbox"]),
        "-C",
        str(workdir),
    ]
    # The config override above is intentionally supplemented with per-server
    # disables. Codex config overlays may deep-merge maps, so an empty parent
    # map alone is not enough to prove that no configured MCP process starts.
    for name in (mcp_names or configured_mcp_names()):
        command.extend(["-c", f"mcp_servers.{name}.enabled=false"])
    return command


def configured_mcp_names() -> list[str]:
    """Read configured MCP table names without starting any server."""
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    config_path = codex_home / "config.toml"
    if not config_path.is_file():
        return []
    try:
        import tomllib

        data = tomllib.loads(config_path.read_text(encoding="utf-8-sig"))
        configured = data.get("mcp_servers", {})
        return sorted(str(name) for name in configured if isinstance(configured, dict))
    except (OSError, ValueError, TypeError):
        # A malformed local config will be reported by Codex itself. Do not
        # invent server names or mutate the user's config while preparing evals.
        return []


def run_acceptance(
    acceptance_path: Path, workdir: Path, timeout: int = 60
) -> dict[str, Any]:
    """Run an immutable acceptance unittest against the copied fixture."""
    resolved = acceptance_path.resolve()
    if not resolved.is_relative_to((EVAL_ROOT / "acceptance").resolve()):
        raise ValueError(f"Acceptance path escapes suite: {acceptance_path}")
    environment = os.environ.copy()
    environment["COMBO_EVAL_ROOT"] = str(workdir)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [sys.executable, str(resolved)],
            cwd=workdir,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "path": str(resolved),
            "returncode": completed.returncode,
            "passed": completed.returncode == 0,
            "timed_out": False,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "path": str(resolved),
            "returncode": None,
            "passed": False,
            "timed_out": True,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": _as_text(exc.stdout),
            "stderr": _as_text(exc.stderr),
        }


def _as_text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def terminate_owned_process_tree(process: subprocess.Popen[str]) -> None:
    """Stop only a timed-out Codex process and descendants it launched."""
    if os.name == "nt":
        # ``/T`` scopes the kill to this PID's process tree. This avoids the
        # dangerous broad task-kill patterns that could affect another user's
        # Codex or shell process.
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.terminate()
    else:
        process.terminate()


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    parse_errors = 0
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            parse_errors += 1
    return events, parse_errors


def item_type(event: dict[str, Any]) -> str | None:
    item = event.get("item")
    return item.get("type") if isinstance(item, dict) else None


def tool_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for event in events:
        event_item_type = item_type(event)
        if event_item_type not in TOOL_ITEM_TYPES:
            continue
        item = event.get("item") or {}
        output = item.get("aggregated_output", "")
        result.append(
            {
                "event_type": event.get("type"),
                "item_id": item.get("id"),
                "item_type": event_item_type,
                "command": item.get("command"),
                "status": item.get("status"),
                "exit_code": item.get("exit_code"),
                "output": output,
            }
        )
    return result


def final_answer(events: list[dict[str, Any]]) -> str:
    messages = []
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            messages.append(item["text"])
    return messages[-1] if messages else ""


def usage_from_events(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    usages = [event.get("usage") for event in events if event.get("type") == "turn.completed"]
    return usages[-1] if usages else None


def actual_references(events: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    """Find skill/workflow files in actual command paths/output, not claims."""
    refs: set[str] = set()
    evidence: list[dict[str, Any]] = []
    for event in events:
        # A started command only proves that a path was proposed. Count a
        # completed zero-exit command with non-empty output as byte-read
        # evidence, which separates an actual reference read from a route
        # claim or an abandoned command.
        if event.get("type") != "item.completed" or item_type(event) != "command_execution":
            continue
        item = event.get("item") or {}
        if item.get("exit_code") != 0:
            continue
        haystack = f"{item.get('command', '')}\n{item.get('aggregated_output', '')}"
        output = item.get("aggregated_output", "")
        if not isinstance(output, str) or not output.strip():
            continue
        found: set[str] = set()
        for skill in KNOWN_SKILLS:
            pattern = rf"(?i)[/\\]{re.escape(skill)}[/\\](?:SKILL\.md|references[/\\])"
            if re.search(pattern, haystack):
                found.add(skill)
        for workflow in KNOWN_WORKFLOWS:
            pattern = rf"(?i)[/\\]combo[/\\](?:workflows[/\\]){re.escape(workflow)}\.md"
            if re.search(pattern, haystack):
                found.add(f"combo/workflows/{workflow}")
        for practice in KNOWN_PRACTICES:
            pattern = rf"(?i)[/\\]combo[/\\](?:practices[/\\]){re.escape(practice)}\.md"
            if re.search(pattern, haystack):
                found.add(f"combo/practices/{practice}")
        if found:
            refs.update(found)
            evidence.append(
                {
                    "item_id": item.get("id"),
                    "references": sorted(found),
                    "command": item.get("command"),
                    "output": output,
                    "output_bytes": len(output.encode("utf-8")),
                    "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
                }
            )
    return sorted(refs), evidence


def actual_files_read(
    events: list[dict[str, Any]],
    workdir: Path,
    requested: list[str],
    markers: dict[str, list[str]] | None = None,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Record successful command output that includes requested fixture files."""
    found: set[str] = set()
    evidence: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") != "item.completed" or item_type(event) != "command_execution":
            continue
        item = event.get("item") or {}
        output = item.get("aggregated_output", "")
        if item.get("exit_code") != 0 or not isinstance(output, str) or not output.strip():
            continue
        command = str(item.get("command", ""))
        haystack = f"{command}\n{output}".replace("\\", "/").lower()
        matched = []
        for relative in requested:
            normalized = relative.replace("\\", "/").lower()
            absolute = str((workdir / relative).resolve()).replace("\\", "/").lower()
            marker_match = any(
                str(marker).lower() in output.lower()
                for marker in (markers or {}).get(relative, [])
            )
            if normalized in haystack or absolute in haystack or marker_match:
                found.add(relative)
                matched.append(relative)
        if matched:
            evidence.append(
                {
                    "item_id": item.get("id"),
                    "files": sorted(matched),
                    "command": item.get("command"),
                    "output_bytes": len(output.encode("utf-8")),
                    "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
                }
            )
    return sorted(found), evidence


def claimed_references(answer: str) -> list[str]:
    lowered = answer.lower()
    claims = {skill for skill in KNOWN_SKILLS if skill in lowered}
    claims.update(
        f"combo/workflows/{workflow}"
        for workflow in KNOWN_WORKFLOWS
        if f"workflows/{workflow}" in lowered or f"{workflow}.md" in lowered
    )
    claims.update(
        f"combo/practices/{practice}"
        for practice in KNOWN_PRACTICES
        if f"practices/{practice}" in lowered
    )
    return sorted(claims)


def ref_matches(actual: str, expected: str) -> bool:
    actual_lower = actual.lower()
    expected_lower = expected.lower()
    return actual_lower == expected_lower or (
        expected_lower.endswith("-") and actual_lower.startswith(expected_lower)
    ) or (
        expected_lower.endswith("/") and actual_lower.startswith(expected_lower)
    )


def has_contextual_term(
    text: str, alternatives: list[str], contexts: list[str], window: int = 140
) -> bool:
    """Require a meaningful nearby context, rather than a detached keyword."""
    lowered = text.lower()
    for alternative in alternatives:
        start = 0
        while True:
            position = lowered.find(alternative, start)
            if position < 0:
                break
            snippet = lowered[max(0, position - window) : position + len(alternative) + window]
            if any(context in snippet for context in contexts):
                return True
            start = position + len(alternative)
    return False


def run_case(
    suite: dict[str, Any],
    case: dict[str, Any],
    launcher: Path | None,
    cli: Path,
    output_dir: Path,
    work_root: Path,
    mcp_names: list[str],
    timeout: int,
    keep_workdir: bool,
) -> dict[str, Any]:
    case_id = case["id"]
    started = time.monotonic()
    workdir = Path(tempfile.mkdtemp(prefix=f"combo-eval-{case_id}-", dir=work_root))
    fixture = FIXTURES_ROOT / case["fixture"]
    shutil.copytree(fixture, workdir, dirs_exist_ok=True)
    before_hashes = snapshot_tree(workdir)
    acceptance_config = case.get("acceptance", {})
    before_acceptance = None
    after_acceptance = None
    if acceptance_config.get("before"):
        before_acceptance = run_acceptance(
            EVAL_ROOT / acceptance_config["before"], workdir
        )
    command = build_command(launcher, cli, suite, case, workdir, mcp_names)
    stdout = ""
    stderr = ""
    returncode: int | None = None
    timed_out = False
    process_error = None
    try:
        process = subprocess.Popen(
            command,
            cwd=workdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=os.environ.copy(),
        )
        try:
            stdout, stderr = process.communicate(case["prompt"], timeout=timeout)
            returncode = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = _as_text(exc.stdout)
            stderr = _as_text(exc.stderr)
            # This is the process launched by this harness. Do not use a broad
            # task-kill command that could terminate unrelated user processes.
            terminate_owned_process_tree(process)
            try:
                tail_stdout, tail_stderr = process.communicate(timeout=5)
                stdout += tail_stdout or ""
                stderr += tail_stderr or ""
            except subprocess.TimeoutExpired:
                process.kill()
                tail_stdout, tail_stderr = process.communicate()
                stdout += tail_stdout or ""
                stderr += tail_stderr or ""
            returncode = process.returncode
    except OSError as exc:
        process_error = repr(exc)

    after_hashes = snapshot_tree(workdir)
    if acceptance_config.get("after"):
        after_acceptance = run_acceptance(
            EVAL_ROOT / acceptance_config["after"], workdir
        )
        # Acceptance is configured with bytecode disabled, but take the final
        # snapshot after it anyway so the result reflects the complete run.
        after_hashes = snapshot_tree(workdir)

    events, parse_errors = parse_events(stdout)
    answer = final_answer(events)
    tools = tool_events(events)
    references, reference_evidence = actual_references(events)
    requested_files = [str(path) for path in case.get("required_actual_file_any", [])]
    files_read, file_read_evidence = actual_files_read(
        events,
        workdir,
        requested_files,
        case.get("required_actual_file_markers", {}),
    )
    claims = claimed_references(answer)
    writes_attempted = [
        {
            "item_id": event.get("item_id"),
            "command": event.get("command"),
        }
        for event in tools
        if isinstance(event.get("command"), str)
        and WRITE_COMMAND_RE.search(event["command"])
    ]
    changed = changed_files(before_hashes, after_hashes)
    assertion_results: dict[str, Any] = {}
    failures: list[str] = []

    if process_error:
        failures.append(f"Codex process could not start: {process_error}")
    if timed_out:
        failures.append(f"Codex session exceeded {timeout}s")
    if returncode != 0:
        failures.append(f"Codex exited with {returncode}")
    if not answer.strip():
        failures.append("No final agent answer was captured")

    if acceptance_config.get("before_must_fail"):
        seeded = bool(before_acceptance and not before_acceptance["passed"])
        assertion_results["seeded_before_acceptance_failed"] = seeded
        if not seeded:
            failures.append("Seeded before acceptance unexpectedly passed")
    if acceptance_config.get("after_must_pass"):
        fixed = bool(after_acceptance and after_acceptance["passed"])
        assertion_results["independent_after_acceptance_passed"] = fixed
        if not fixed:
            failures.append("Independent after acceptance did not pass")

    no_writes = bool(case.get("no_writes"))
    if no_writes:
        unchanged = not changed
        no_write_commands = not writes_attempted
        assertion_results["no_changed_files"] = unchanged
        assertion_results["no_write_like_commands"] = no_write_commands
        if not unchanged:
            failures.append("Read-only case changed fixture files")
        if not no_write_commands:
            failures.append("Read-only case emitted a write-like command")

    allowed = case.get("allowed_changed_paths")
    if allowed is not None:
        allowed_set = set(allowed)
        changed_paths = {row["path"] for row in changed}
        within = changed_paths <= allowed_set
        assertion_results["changed_paths_within_allowed"] = within
        if not within:
            failures.append(
                "Changed files outside allowed scope: "
                + ", ".join(sorted(changed_paths - allowed_set))
            )

    expected = case.get("assertions", {})
    required_changed = set(expected.get("must_have_changed", []))
    if required_changed:
        actual_changed = {row["path"] for row in changed}
        has_required = required_changed <= actual_changed
        assertion_results["required_files_changed"] = has_required
        if not has_required:
            failures.append(
                "Required files were not changed: "
                + ", ".join(sorted(required_changed - actual_changed))
            )

    required_refs = case.get("required_actual_ref_any", [])
    if required_refs:
        ref_ok = any(
            ref_matches(actual, wanted)
            for actual in references
            for wanted in required_refs
        )
        assertion_results["required_actual_reference_read"] = ref_ok
        if not ref_ok:
            failures.append(
                "No required instruction reference was observed in tool output"
            )
    required_refs_all = case.get("required_actual_ref_all", [])
    if required_refs_all:
        missing_refs = [
            wanted
            for wanted in required_refs_all
            if not any(ref_matches(actual, wanted) for actual in references)
        ]
        all_refs_ok = not missing_refs
        assertion_results["required_actual_references_all_read"] = all_refs_ok
        if not all_refs_ok:
            failures.append(
                "Required instruction references were not all observed in tool output: "
                + ", ".join(missing_refs)
            )
    if requested_files:
        files_ok = set(files_read) >= set(requested_files)
        assertion_results["required_fixture_files_read"] = files_ok
        if not files_ok:
            failures.append(
                "Required fixture files were not observed in successful read output: "
                + ", ".join(sorted(set(requested_files) - set(files_read)))
            )
    forbidden_refs = case.get("forbidden_actual_ref_any", [])
    forbidden_seen = sorted(
        actual
        for actual in references
        if any(ref_matches(actual, wanted) for wanted in forbidden_refs)
    )
    assertion_results["forbidden_actual_references_absent"] = not forbidden_seen
    if forbidden_seen:
        failures.append("Forbidden instruction references were read: " + ", ".join(forbidden_seen))

    required_any_terms = [str(x).lower() for x in case.get("required_final_terms_any", [])]
    if required_any_terms:
        term_ok = any(term in answer.lower() for term in required_any_terms)
        assertion_results["required_final_term_any"] = term_ok
        if not term_ok:
            failures.append("Final answer lacks any required finding/plan term")
    required_all_terms = [str(x).lower() for x in case.get("required_final_terms_all", [])]
    if required_all_terms:
        missing = [term for term in required_all_terms if term not in answer.lower()]
        assertion_results["required_final_terms_all"] = not missing
        if missing:
            failures.append("Final answer lacks required terms: " + ", ".join(missing))

    term_groups = case.get("required_final_term_groups", [])
    for group in term_groups:
        name = str(group.get("name", "unnamed"))
        alternatives = [str(term).lower() for term in group.get("any", [])]
        matched = any(term in answer.lower() for term in alternatives)
        assertion_results[f"final_term_group:{name}"] = matched
        if not matched:
            failures.append(f"Final answer lacks semantic evidence for {name}")

    for adapter in case.get("required_final_adapter_evidence", []):
        name = str(adapter.get("name", "adapter"))
        alternatives = [str(term).lower() for term in adapter.get("any", [])]
        contexts = [str(term).lower() for term in adapter.get("context_any", [])]
        context_ok = has_contextual_term(answer, alternatives, contexts)
        assertion_results[f"final_adapter:{name}"] = context_ok
        if not context_ok:
            failures.append(f"Final answer lacks meaningful evidence for {name}")

    if case.get("no_tools"):
        no_tools = not tools
        assertion_results["no_tool_events"] = no_tools
        if not no_tools:
            failures.append("Negative noncoding case emitted tool events")
    if case.get("required_final_unicode_range") == "thai":
        has_thai = bool(THAI_RE.search(answer))
        assertion_results["thai_translation_present"] = has_thai
        if not has_thai:
            failures.append("Final answer contains no Thai translation")

    if expected.get("must_match_text"):
        target = workdir / "src" / "ui.py"
        text = target.read_text(encoding="utf-8") if target.exists() else ""
        text_ok = expected["must_match_text"] in text and 'BUTTON_LABEL = "Save"' not in text
        assertion_results["target_text_updated"] = text_ok
        if not text_ok:
            failures.append("Target label was not updated to the requested text")
    if expected.get("must_preserve_existing_seam"):
        seam_terms = ("protocol", "interface", "seam", "shared adapter")
        seam_ok = any(term in answer.lower() for term in seam_terms)
        assertion_results["existing_adapter_seam_addressed"] = seam_ok
        if not seam_ok:
            failures.append("Plan does not explain preserving the existing adapter seam")
    if expected.get("must_not_claim_implementation"):
        no_implementation_claim = not IMPLEMENTATION_CLAIM_RE.search(answer)
        assertion_results["no_implementation_claim"] = no_implementation_claim
        if not no_implementation_claim:
            failures.append("Review/plan answer claims implementation despite the stopping point")

    # Claims are useful context, but only command output counts as a read.
    unverified_claims = sorted(set(claims) - set(references))
    assertion_results["route_claims_without_read_evidence"] = unverified_claims
    assertion_results["writes_attempted"] = writes_attempted
    assertion_results["changed_files"] = changed

    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    events_path = case_dir / "events.jsonl"
    stderr_path = case_dir / "stderr.txt"
    prompt_path = case_dir / "prompt.txt"
    events_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    prompt_path.write_text(case["prompt"], encoding="utf-8")

    result: dict[str, Any] = {
        "case_id": case_id,
        "title": case["title"],
        "fixture": case["fixture"],
        "model": suite["model"],
        "reasoning_effort": suite["reasoning_effort"],
        "sandbox": case["sandbox"],
        "prompt": case["prompt"],
        "command": command,
        "workdir": str(workdir),
        "workdir_retained": keep_workdir,
        "started_at_epoch": started,
        "duration_seconds": round(time.monotonic() - started, 3),
        "returncode": returncode,
        "timed_out": timed_out,
        "process_error": process_error,
        "stdout_events_path": str(events_path),
        "stderr_path": str(stderr_path),
        "events_parse_errors": parse_errors,
        "tool_events": tools,
        "final_answer": answer,
        "usage": usage_from_events(events),
        "actual_references_read": references,
        "actual_reference_evidence": reference_evidence,
        "actual_fixture_files_read": files_read,
        "actual_fixture_file_evidence": file_read_evidence,
        "route_claims_in_final_answer": claims,
        "route_claims_without_read_evidence": unverified_claims,
        "write_like_commands": writes_attempted,
        "changed_files": changed,
        "before_acceptance": before_acceptance,
        "after_acceptance": after_acceptance,
        "assertions": assertion_results,
        "status": "passed" if not failures else "failed",
        "failures": failures,
    }
    (case_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if not keep_workdir:
        # Only remove the exact temporary directory created for this case.
        resolved_workdir = workdir.resolve()
        resolved_work_root = work_root.resolve()
        if (
            resolved_workdir.parent == resolved_work_root
            and resolved_workdir.name.startswith("combo-eval-")
        ):
            shutil.rmtree(resolved_workdir)
            result["workdir"] = None
            (case_dir / "result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="case_ids", help="Run one case id (repeatable)")
    parser.add_argument("--output", type=Path, help="Result directory or .json summary path")
    parser.add_argument("--cli", help="Path to installed Codex bin/codex.js")
    parser.add_argument("--timeout", type=int, default=180, help="Per-session timeout, at most 180 seconds")
    parser.add_argument("--max-parallel", type=int, default=2, help="Concurrent sessions, at most 2")
    parser.add_argument(
        "--keep-workdirs",
        dest="keep_workdirs",
        action="store_true",
        default=True,
        help="Retain copied fixture directories for behavior review (default)",
    )
    parser.add_argument(
        "--cleanup-workdirs",
        dest="keep_workdirs",
        action="store_false",
        help="Remove the exact copied fixture directories after each case",
    )
    parser.add_argument(
        "--work-root",
        type=Path,
        default=Path("D:/combo-workflow-evals"),
        help="Dedicated work-root outside the repository and user home",
    )
    parser.add_argument("--list", action="store_true", help="List cases without starting sessions")
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 180:
        parser.error("--timeout must be between 1 and 180 seconds")
    if args.max_parallel < 1 or args.max_parallel > 2:
        parser.error("--max-parallel must be between 1 and 2")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    suite = load_suite()
    all_cases = {case["id"]: case for case in suite["cases"]}
    if args.case_ids:
        unknown = sorted(set(args.case_ids) - set(all_cases))
        if unknown:
            raise SystemExit("Unknown case id(s): " + ", ".join(unknown))
        cases = [all_cases[case_id] for case_id in args.case_ids]
    else:
        cases = list(suite["cases"])
    if args.list:
        for case in cases:
            print(f"{case['id']}: {case['title']}")
        return 0

    launcher, cli = find_cli(args.cli)
    mcp_names = configured_mcp_names()
    work_root = args.work_root.resolve()
    repo_root = ROOT.resolve()
    user_home = Path.home().resolve()
    if work_root == repo_root or work_root.is_relative_to(repo_root) or repo_root.is_relative_to(work_root):
        raise SystemExit("--work-root must be outside the repository tree")
    if work_root == user_home or work_root.is_relative_to(user_home) or user_home.is_relative_to(work_root):
        raise SystemExit("--work-root must be outside the user home tree")
    work_root.mkdir(parents=True, exist_ok=True)
    if not work_root.is_dir():
        raise SystemExit(f"--work-root is not a directory: {work_root}")
    run_root = Path(tempfile.mkdtemp(prefix="combo-suite-", dir=work_root))
    if args.output:
        output_arg = args.output.resolve()
        if output_arg.suffix.lower() == ".json":
            output_dir = output_arg.parent / output_arg.stem
            summary_path = output_arg
        else:
            output_dir = output_arg
            summary_path = output_dir / "summary.json"
    else:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        output_dir = EVAL_ROOT / "results" / f"run-{stamp}"
        summary_path = output_dir / "summary.json"
    output_dir.mkdir(parents=True, exist_ok=False)

    version = subprocess.run(
        cli_prefix(launcher, cli) + ["--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    run_started = time.time()
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.max_parallel, thread_name_prefix="combo-eval") as pool:
        futures = {
            pool.submit(
                run_case,
                suite,
                case,
                launcher,
                cli,
                output_dir,
                run_root,
                mcp_names,
                args.timeout,
                args.keep_workdirs,
            ): case["id"]
            for case in cases
        }
        for future in as_completed(futures):
            results.append(future.result())
            print(f"{futures[future]}: {results[-1]['status']}", flush=True)
    results.sort(key=lambda item: [case["id"] for case in cases].index(item["case_id"]))
    passed = sum(result["status"] == "passed" for result in results)
    summary = {
        "schema_version": 2,
        "suite": suite["suite"],
        "started_at_epoch": run_started,
        "completed_at_epoch": time.time(),
        "host": "codex-cli",
        "codex_cli": str(cli),
        "codex_cli_version": version.stdout.strip() or version.stderr.strip(),
        "launcher": str(launcher) if launcher else None,
        "model": suite["model"],
        "reasoning_effort": suite["reasoning_effort"],
        "fresh_isolated_sessions": len(results),
        "max_parallel": args.max_parallel,
        "timeout_seconds": args.timeout,
        "work_root": str(work_root),
        "run_root": str(run_root) if args.keep_workdirs else None,
        "passed": passed,
        "failed": len(results) - passed,
        "coverage_note": "One six-case Luna Max sample; this is workflow coverage, not all-model reliability proof.",
        "results": results,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.keep_workdirs:
        # The suite directory is ours, freshly created above, and should be
        # removed only after every case has finished and each case directory
        # has already been cleaned individually.
        if run_root.parent == work_root and run_root.name.startswith("combo-suite-"):
            shutil.rmtree(run_root)
    print(f"Summary: {summary_path}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
