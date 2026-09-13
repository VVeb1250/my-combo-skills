"""Summarize the real Combo A/B evaluation artifacts already on disk.

The evaluator writes one result directory per arm.  This script is deliberately
read-only with respect to the runs themselves: it reads the result and
discovery artifacts and writes only the requested metrics JSON and Markdown
reports.  Missing result files are represented as pending so the same command
can be run again after a harness run finishes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_ROOT = ROOT / "audit" / "ab"
DEFAULT_CASES = ROOT / "evals" / "ab" / "cases.json"
DEFAULT_JSON = DEFAULT_AUDIT_ROOT / "metrics.json"
DEFAULT_MARKDOWN = DEFAULT_AUDIT_ROOT / "metrics.md"

RUN_NAMES = ("probe-final", "matched-rest")
VARIANTS = ("A", "B")
EXPECTED_PROBE_CASE = "bug-zero"

# A command that names a skill/reference file can be a search or a directory
# listing rather than a read.  Restrict evidence to common content readers or
# file-content search tools, and require a concrete .md path under a skills
# directory.  This is intentionally conservative and does not inspect claims
# in the final answer.
READ_COMMAND_RE = re.compile(
    r"(?i)\b(?:get-content|cat|type(?:\.exe)?|more(?:\.com)?|"
    r"head|tail|sed|awk|rg|grep|findstr)\b"
)
INSTRUCTION_PATH_RE = re.compile(
    r"(?i)(?P<scope>\.agents|\.codex)/skills/"
    r"(?P<relative>[a-z0-9_.:-]+(?:/[a-z0-9_.:-]+)*/"
    r"(?:skill\.md|[a-z0-9_.:-]+\.md))"
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-root",
        type=Path,
        default=DEFAULT_AUDIT_ROOT,
        help="Directory containing probe-final and matched-rest artifacts",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="A/B case specification JSON",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DEFAULT_JSON,
        help="Metrics JSON output path",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=DEFAULT_MARKDOWN,
        help="Metrics Markdown output path",
    )
    return parser.parse_args(argv)


def read_json(path: Path) -> Any:
    """Read UTF-8 JSON, accepting a UTF-8 BOM used by some Windows tools."""

    return json.loads(path.read_text(encoding="utf-8-sig"))


def relative_path(path: Path) -> str:
    """Render a repository path without exposing machine-specific prefixes."""

    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def numeric(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def as_int(value: Any) -> int | None:
    parsed = numeric(value)
    if parsed is None:
        return None
    return int(parsed)


def normalize_doubled_windows_slashes(value: str) -> str:
    """Collapse JSON/shell doubled backslashes before path matching.

    The command strings are serialized twice in some artifacts, so a single
    path separator can appear as ``\\\\`` after JSON decoding.  Repeating the
    collapse handles both one and two serialization layers while leaving
    normal forward slashes unchanged.
    """

    normalized = value
    for _ in range(3):
        collapsed = normalized.replace("\\\\", "\\")
        if collapsed == normalized:
            break
        normalized = collapsed
    return normalized.replace("\\", "/")


def logical_instruction_path(match: re.Match[str]) -> str:
    return match.group("relative").replace("\\", "/")


def instruction_source(command: str, match: re.Match[str]) -> str:
    """Classify a path only as broadly as the command path permits."""

    before = command[: match.start()].lower()
    # Inspect the path token immediately before the matched ``.agents`` or
    # ``.codex`` segment.  The command also contains the global PowerShell
    # executable path, so looking at the whole command would misclassify a
    # relative candidate path as a global instruction.
    token_start = (
        max(
            before.rfind(" "),
            before.rfind("\t"),
            before.rfind("'"),
            before.rfind('"'),
            before.rfind(";"),
            before.rfind("|"),
            before.rfind("&"),
            before.rfind("("),
        )
        + 1
    )
    token_prefix = before[token_start:]
    absolute = re.search(r"(?i)([a-z]:/|/)[^'\";|&()]*$", token_prefix)
    path_prefix = absolute.group(0) if absolute else ""
    scope = match.group("scope").lower()
    if "/combo-ab-evals/" in path_prefix or "/staged-" in path_prefix:
        return "candidate"
    if scope == ".codex":
        return "global-codex"
    if ".agents/skills/" in path_prefix and ":/users/" in path_prefix:
        return "global-agents"
    if not absolute:
        return "relative"
    return "unknown"


def empty_tool_summary() -> dict[str, Any]:
    return {
        "completed_unique": 0,
        "completed_unique_by_type": {},
        "completed_events_without_id": 0,
        "source": None,
    }


def load_tool_events(
    arm_dir: Path, result: dict[str, Any]
) -> tuple[list[dict[str, Any]], str | None]:
    """Load the compact tool event artifact, falling back to raw JSONL."""

    candidates: list[Path] = []
    declared = result.get("tool_events_path")
    if isinstance(declared, str) and declared:
        candidates.append(Path(declared))
    candidates.append(arm_dir / "tool-events.json")
    for path in candidates:
        if not path.is_file():
            continue
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)], relative_path(path)

    raw = arm_dir / "events.jsonl"
    if raw.is_file():
        events: list[dict[str, Any]] = []
        try:
            for line in raw.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                item = event.get("item")
                if not isinstance(item, dict):
                    continue
                events.append(
                    {
                        "event_type": event.get("type"),
                        "item_id": item.get("id"),
                        "item_type": item.get("type"),
                        "command": item.get("command"),
                        "status": item.get("status"),
                        "exit_code": item.get("exit_code"),
                    }
                )
        except OSError:
            return [], None
        return events, relative_path(raw)
    return [], None


def completed_tool_calls(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Count completed calls once per item ID, ignoring started duplicates."""

    by_id: dict[str, dict[str, Any]] = {}
    without_id = 0
    for event in events:
        if event.get("event_type") != "item.completed":
            continue
        if event.get("status") not in (None, "completed"):
            continue
        item_id = event.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            without_id += 1
            continue
        # If an artifact contains duplicate completions, keep the last one.
        by_id[item_id] = event
    type_counts = Counter(
        str(event.get("item_type") or "unknown") for event in by_id.values()
    )
    return {
        "completed_unique": len(by_id),
        "completed_unique_by_type": dict(sorted(type_counts.items())),
        "completed_events_without_id": without_id,
    }


def completed_instruction_reads(
    events: Iterable[dict[str, Any]], existing_references: Any
) -> dict[str, Any]:
    """Infer concrete instruction paths from successful completed commands."""

    by_id: dict[str, dict[str, Any]] = {}
    for event in events:
        if event.get("event_type") != "item.completed":
            continue
        if event.get("status") not in (None, "completed"):
            continue
        if event.get("item_type") != "command_execution":
            continue
        if event.get("exit_code") != 0:
            continue
        item_id = event.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            continue
        by_id[item_id] = event

    references = {
        str(value).replace("\\", "/").lower()
        for value in existing_references
        if isinstance(value, str)
    }
    evidence: list[dict[str, Any]] = []
    unique: dict[tuple[str, str], set[str]] = {}
    for item_id, event in sorted(by_id.items()):
        command = event.get("command")
        if not isinstance(command, str) or not READ_COMMAND_RE.search(
            normalize_doubled_windows_slashes(command)
        ):
            continue
        normalized = normalize_doubled_windows_slashes(command)
        matches = list(INSTRUCTION_PATH_RE.finditer(normalized))
        if not matches:
            continue
        paths: list[dict[str, str]] = []
        for match in matches:
            logical = logical_instruction_path(match)
            source = instruction_source(normalized, match)
            key = (source, logical.lower())
            unique.setdefault(key, set()).add(item_id)
            paths.append({"path": logical, "source": source})
        if paths:
            # A command can mention one file more than once.  Preserve the
            # evidence item once, with duplicate paths removed in order.
            seen: set[tuple[str, str]] = set()
            distinct_paths = []
            for path in paths:
                key = (path["source"], path["path"].lower())
                if key in seen:
                    continue
                seen.add(key)
                distinct_paths.append(path)
            evidence.append(
                {
                    "item_id": item_id,
                    "paths": distinct_paths,
                    "command_normalized": normalized,
                }
            )

    unique_rows = [
        {
            "path": path,
            "source": source,
            "evidence_item_ids": sorted(item_ids),
        }
        for (source, path), item_ids in sorted(unique.items())
    ]
    parser_gap = [
        row["path"]
        for row in unique_rows
        if not any(
            ref == row["path"].removesuffix("/skill.md")
            or row["path"].startswith(ref + "/")
            for ref in references
        )
    ]
    return {
        "unique_paths": unique_rows,
        "unique_path_count": len(unique_rows),
        "evidence_commands": evidence,
        "evidence_command_count": len(evidence),
        "existing_parser_references": sorted(references),
        "paths_not_in_existing_parser": sorted(parser_gap),
        "method": (
            "Successful item.completed command_execution events only, deduplicated "
            "by item_id; command paths normalized for doubled Windows slashes."
        ),
    }


def usage_summary(usage: Any) -> dict[str, int | None]:
    """Keep reported usage fields separate and derive uncached input only."""

    if not isinstance(usage, dict):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "uncached_input_tokens": None,
            "cache_write_input_tokens": None,
            "output_tokens": None,
            "reasoning_output_tokens": None,
        }
    input_tokens = as_int(usage.get("input_tokens"))
    cached = as_int(usage.get("cached_input_tokens"))
    uncached = None
    if input_tokens is not None and cached is not None and input_tokens >= cached:
        uncached = input_tokens - cached
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "uncached_input_tokens": uncached,
        "cache_write_input_tokens": as_int(usage.get("cache_write_input_tokens")),
        "output_tokens": as_int(usage.get("output_tokens")),
        "reasoning_output_tokens": as_int(usage.get("reasoning_output_tokens")),
    }


def acceptance_status(value: Any) -> str:
    if value is None:
        return "not-run"
    if not isinstance(value, dict):
        return "unknown"
    passed = value.get("passed")
    if passed is True:
        return "passed"
    if passed is False:
        return "failed"
    return "unknown"


def normalize_acceptance(
    result: dict[str, Any], case: dict[str, Any]
) -> dict[str, Any]:
    observed = result.get("acceptance")
    if not isinstance(observed, dict):
        observed = {
            "before": result.get("before_acceptance"),
            "after": result.get("after_acceptance"),
        }
    before = observed.get("before")
    after = observed.get("after")
    config = case.get("acceptance")
    config = config if isinstance(config, dict) else {}
    expected_before = "failed" if config.get("before_must_fail") else None
    expected_after = "passed" if config.get("after_must_pass") else None
    checks: list[bool] = []
    if expected_before is not None:
        checks.append(acceptance_status(before) == expected_before)
    if expected_after is not None:
        checks.append(acceptance_status(after) == expected_after)
    meets = all(checks) if checks else None
    return {
        "configured": bool(config.get("before") or config.get("after")),
        "before": before,
        "before_status": acceptance_status(before),
        "after": after,
        "after_status": acceptance_status(after),
        "expected_before_status": expected_before,
        "expected_after_status": expected_after,
        "meets_config": meets,
    }


def completion_quality(result: dict[str, Any]) -> str:
    if result.get("timed_out"):
        return "deadline-incomplete"
    if result.get("process_error"):
        return "process-start-error"
    if result.get("returncode") not in (None, 0):
        return "nonzero-exit"
    if not str(result.get("final_answer") or "").strip():
        return "no-final-answer"
    return "recorded"


def arm_state(arm_dir: Path) -> str:
    if not arm_dir.exists():
        return "pending"
    artifacts = tuple(arm_dir.iterdir())
    if artifacts:
        return "in-progress-or-partial"
    return "pending"


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        raise TypeError(f"cases missing from {path}")
    result = [
        case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    ]
    if len(result) != len(cases):
        raise ValueError("cases contains a non-object or missing id")
    return result


def preferred_run(case_id: str) -> str:
    return "probe-final" if case_id == EXPECTED_PROBE_CASE else "matched-rest"


def result_record(
    run_name: str,
    variant: str,
    case: dict[str, Any],
    arm_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    result_path = arm_dir / "result.json"
    base: dict[str, Any] = {
        "run": run_name,
        "case_id": case["id"],
        "variant": variant,
        "state": "pending",
        "classification": None,
        "completion_quality": None,
        "result_path": relative_path(result_path),
        "acceptance": normalize_acceptance({}, case),
        "wall_time_seconds": None,
        "tokens": usage_summary(None),
        "tool_calls": empty_tool_summary(),
        "instructions": {
            "unique_paths": [],
            "unique_path_count": 0,
            "evidence_commands": [],
            "evidence_command_count": 0,
            "existing_parser_references": [],
            "paths_not_in_existing_parser": [],
            "method": "No completed result artifact available.",
        },
    }
    if not result_path.is_file():
        base["state"] = arm_state(arm_dir)
        return base, None
    try:
        result = read_json(result_path)
    except (OSError, json.JSONDecodeError) as exc:
        base["state"] = "in-progress-or-malformed"
        base["error"] = str(exc)
        return base, None
    if not isinstance(result, dict):
        base["state"] = "in-progress-or-malformed"
        base["error"] = "result JSON is not an object"
        return base, None

    tool_events, tool_source = load_tool_events(arm_dir, result)
    tool_summary = completed_tool_calls(tool_events)
    tool_summary["source"] = tool_source
    instructions = completed_instruction_reads(
        tool_events, result.get("actual_references", [])
    )
    base.update(
        {
            "state": "completed-artifact",
            "classification": result.get("classification"),
            "completion_quality": completion_quality(result),
            "returncode": result.get("returncode"),
            "timed_out": bool(result.get("timed_out")),
            "wall_time_seconds": numeric(result.get("duration_seconds")),
            "tokens": usage_summary(result.get("usage")),
            "tool_calls": tool_summary,
            "instructions": instructions,
            "acceptance": normalize_acceptance(result, case),
        }
    )
    # Keep the raw harness failures available without copying final answer text
    # or command output into the metrics report.
    for key in ("environment_failures", "task_failures"):
        if isinstance(result.get(key), list):
            base[key] = result[key]
    return base, result


def discover_inventory(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": relative_path(path),
            "state": "missing",
            "repo_combo_entries": [],
            "global_combo_entries": [],
            "entry_count": None,
        }
    try:
        data = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "path": relative_path(path),
            "state": "malformed",
            "error": str(exc),
            "repo_combo_entries": [],
            "global_combo_entries": [],
            "entry_count": None,
        }
    rows = []
    skills = data.get("skills") if isinstance(data, dict) else None
    records = skills.get("data") if isinstance(skills, dict) else None
    if isinstance(records, list):
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("skills"), list):
                rows.extend(item for item in record["skills"] if isinstance(item, dict))
    repo_combo = [
        entry
        for entry in rows
        if entry.get("scope") == "repo"
        and isinstance(entry.get("name"), str)
        and entry["name"].startswith("combo")
    ]
    global_combo = [
        entry
        for entry in rows
        if entry.get("scope") == "user" and entry.get("name") == "combo"
    ]
    return {
        "path": relative_path(path),
        "state": "read",
        "entry_count": len(rows),
        "repo_combo_entries": [
            {
                "name": entry.get("name"),
                "scope": entry.get("scope"),
                "enabled": entry.get("enabled"),
                "path": entry.get("path"),
            }
            for entry in repo_combo
        ],
        "global_combo_entries": [
            {
                "name": entry.get("name"),
                "scope": entry.get("scope"),
                "enabled": entry.get("enabled"),
                "path": entry.get("path"),
            }
            for entry in global_combo
        ],
        "all_entries": rows,
    }


def inventory_projection(entry: dict[str, Any]) -> tuple[Any, ...]:
    """Compare unrelated inventory without depending on descriptions or cwd."""

    path = entry.get("path")
    if isinstance(path, str):
        path = normalize_doubled_windows_slashes(path).lower()
    return (entry.get("name"), entry.get("scope"), entry.get("enabled"), path)


def compare_discoveries(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "expected_repo_combo_entries": {"A": 1, "B": 13},
        "observed_repo_combo_entries": {
            "A": len(a.get("repo_combo_entries", [])),
            "B": len(b.get("repo_combo_entries", [])),
        },
        "repo_combo_count_verified": (
            len(a.get("repo_combo_entries", [])) == 1
            and len(b.get("repo_combo_entries", [])) == 13
        ),
        "global_combo_disabled": {
            "A": bool(a.get("global_combo_entries"))
            and all(
                entry.get("enabled") is False for entry in a["global_combo_entries"]
            ),
            "B": bool(b.get("global_combo_entries"))
            and all(
                entry.get("enabled") is False for entry in b["global_combo_entries"]
            ),
        },
        "repo_combo_names": {
            "A": [entry.get("name") for entry in a.get("repo_combo_entries", [])],
            "B": [entry.get("name") for entry in b.get("repo_combo_entries", [])],
        },
    }
    a_entries = [
        entry
        for entry in a.get("all_entries", [])
        if not (
            entry.get("scope") == "repo"
            and isinstance(entry.get("name"), str)
            and entry["name"].startswith("combo")
        )
    ]
    b_entries = [
        entry
        for entry in b.get("all_entries", [])
        if not (
            entry.get("scope") == "repo"
            and isinstance(entry.get("name"), str)
            and entry["name"].startswith("combo")
        )
    ]
    a_counter = Counter(inventory_projection(entry) for entry in a_entries)
    b_counter = Counter(inventory_projection(entry) for entry in b_entries)
    missing = list((a_counter - b_counter).elements())
    extra = list((b_counter - a_counter).elements())
    result["unrelated_inventory"] = {
        "comparable": a.get("state") == "read" and b.get("state") == "read",
        "A_count": len(a_entries),
        "B_count": len(b_entries),
        "preserved": not missing and not extra,
        "missing_in_B": [list(row) for row in missing],
        "extra_in_B": [list(row) for row in extra],
        "method": "Compare name, scope, enabled, and normalized path after excluding repo-scoped combo entries.",
    }
    result["verified"] = bool(
        result["repo_combo_count_verified"]
        and all(result["global_combo_disabled"].values())
        and result["unrelated_inventory"]["comparable"]
        and result["unrelated_inventory"]["preserved"]
    )
    return result


def aggregate_tokens(records: list[dict[str, Any]]) -> dict[str, Any]:
    fields = (
        "input_tokens",
        "cached_input_tokens",
        "uncached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    )
    totals: dict[str, int | None] = {}
    for field in fields:
        values = [record["tokens"].get(field) for record in records]
        totals[field] = sum(value for value in values if isinstance(value, int))
        if not any(isinstance(value, int) for value in values):
            totals[field] = None
    usage_records = [
        record
        for record in records
        if any(isinstance(record["tokens"].get(field), int) for field in fields)
    ]
    return {
        "completed_artifact_count": len(records),
        "artifacts_with_usage": len(usage_records),
        "artifacts_missing_usage": len(records) - len(usage_records),
        "by_arm_sum": totals,
        "note": (
            "input_tokens is the reported input field; cached_input_tokens and "
            "uncached_input_tokens are separate. uncached_input_tokens is derived "
            "as input_tokens minus cached_input_tokens. No total-input cost is inferred."
        ),
    }


def aggregate_tools(records: list[dict[str, Any]]) -> dict[str, Any]:
    type_counts: Counter[str] = Counter()
    total = 0
    for record in records:
        summary = record.get("tool_calls", {})
        total += int(summary.get("completed_unique") or 0)
        type_counts.update(summary.get("completed_unique_by_type", {}))
    return {
        "completed_unique_calls": total,
        "completed_unique_calls_by_type": dict(sorted(type_counts.items())),
        "method": "One item.completed event per unique item_id within each arm; arm-local IDs are not merged across arms.",
    }


def build_metrics(cases_path: Path, audit_root: Path) -> dict[str, Any]:
    cases = load_cases(cases_path)
    records: list[dict[str, Any]] = []
    malformed: list[dict[str, Any]] = []

    for case in cases:
        for variant in VARIANTS:
            run_name = preferred_run(case["id"])
            arm_dir = audit_root / run_name / "arms" / variant / case["id"]
            record, _ = result_record(run_name, variant, case, arm_dir)
            records.append(record)
            if record["state"] == "in-progress-or-malformed":
                malformed.append(
                    {
                        "run": run_name,
                        "case_id": case["id"],
                        "variant": variant,
                        "path": record["result_path"],
                        "error": record.get("error"),
                    }
                )

    completed = [
        record for record in records if record["state"] == "completed-artifact"
    ]
    result_counts = Counter(
        str(record["classification"])
        for record in completed
        if record.get("classification") is not None
    )
    state_counts = Counter(record["state"] for record in records)

    pairs: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        arms = [
            next(
                record
                for record in records
                if record["case_id"] == case["id"] and record["variant"] == variant
            )
            for variant in VARIANTS
        ]
        durations = [
            record["wall_time_seconds"]
            for record in arms
            if isinstance(record.get("wall_time_seconds"), (int, float))
        ]
        pairs.append(
            {
                "case_id": case["id"],
                "title": case.get("title"),
                "domain": case.get("domain"),
                "pair_index": index,
                "first_arm": "A" if index % 2 == 0 else "B",
                "arm_states": {record["variant"]: record["state"] for record in arms},
                "arm_classifications": {
                    record["variant"]: record.get("classification") for record in arms
                },
                "wall_time_seconds": max(durations) if durations else None,
                "sum_arm_wall_time_seconds": sum(durations) if durations else None,
            }
        )

    discovery = {
        "probe-final": {
            variant: discover_inventory(
                audit_root / "probe-final" / "discovery" / f"{variant}.json"
            )
            for variant in VARIANTS
        },
        "matched-rest": {
            variant: discover_inventory(
                audit_root / "matched-rest" / "discovery" / f"{variant}.json"
            )
            for variant in VARIANTS
        },
    }
    # The two runs should have the same staged inventory shape. Prefer the
    # complete probe/final pair when both are available, otherwise use the
    # latest run with readable inventories.
    discovery_a = discovery["probe-final"]["A"]
    discovery_b = discovery["probe-final"]["B"]
    discovery_source = "probe-final"
    if discovery_a.get("state") != "read" or discovery_b.get("state") != "read":
        discovery_a = discovery["matched-rest"]["A"]
        discovery_b = discovery["matched-rest"]["B"]
        discovery_source = "matched-rest"
    discovery_comparison = compare_discoveries(discovery_a, discovery_b)
    discovery_comparison["source_run"] = discovery_source

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": {
            "cases": relative_path(cases_path),
            "audit_root": relative_path(audit_root),
            "runs": list(RUN_NAMES),
            "preferred_run": {
                "bug-zero": "probe-final",
                "other_cases": "matched-rest",
            },
        },
        "suite": {
            "suite": read_json(cases_path).get("suite"),
            "model": read_json(cases_path).get("model"),
            "reasoning_effort": read_json(cases_path).get("reasoning_effort"),
            "expected_cases": len(cases),
            "expected_arms": len(cases) * len(VARIANTS),
        },
        "coverage": {
            "expected_case_count": len(cases),
            "expected_arm_count": len(records),
            "completed_result_artifacts": len(completed),
            "pending_or_partial_arm_count": len(records) - len(completed),
            "state_counts": dict(sorted(state_counts.items())),
            "classification_counts": dict(sorted(result_counts.items())),
            "malformed_result_files": malformed,
        },
        "discovery": {
            "probe-final": {
                variant: {
                    key: value
                    for key, value in discovery["probe-final"][variant].items()
                    if key != "all_entries"
                }
                for variant in VARIANTS
            },
            "matched-rest": {
                variant: {
                    key: value
                    for key, value in discovery["matched-rest"][variant].items()
                    if key != "all_entries"
                }
                for variant in VARIANTS
            },
            "comparison": discovery_comparison,
        },
        "tokens": aggregate_tokens(completed),
        "tool_calls": aggregate_tools(completed),
        "results": records,
        "pairs": pairs,
        "limits": [
            "Only result.json artifacts present when this report ran are counted; absent arms remain pending or partial.",
            "Harness classification and failure strings are copied metadata derived from exit, timeout, answer, acceptance, and scope checks. A heuristic task flag, including write-like command detection, is not by itself proof of a real fixture write; changed_files and acceptance remain separate evidence.",
            "Acceptance and semantic evidence in the harness use keyword or metadata checks. They do not prove that a human would accept every answer.",
            "Instruction reads are inferred from successful completed command strings with a concrete skills Markdown path. Path evidence cannot prove that every command returned the intended bytes, and output is not re-read here.",
            "uncached_input_tokens is derived from reported input_tokens minus cached_input_tokens. Token fields are reported separately and are not converted into a total-input cost.",
            "Discovery verification compares inventory metadata and expected combo counts. It does not establish runtime routing quality or choose an architecture.",
        ],
    }


def acceptance_text(acceptance: dict[str, Any]) -> str:
    before = acceptance.get("before_status", "not-run")
    after = acceptance.get("after_status", "not-run")
    if not acceptance.get("configured"):
        return "not configured"
    return f"before {before}; after {after}"


def fmt_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return f"{value:,}"


def markdown_report(metrics: dict[str, Any]) -> str:
    coverage = metrics["coverage"]
    discovery = metrics["discovery"]
    comparison = discovery["comparison"]
    lines = [
        "# A/B evaluation metrics",
        "",
        f"Generated `{metrics['generated_at_utc']}` from the existing real Codex artifacts.",
        "",
        f"Cases are defined by `{metrics['source']['cases']}`. The report reads `probe-final` for `bug-zero` and `matched-rest` for the other cases. Re-run `python scripts/summarize-ab.py` after more arm result files appear.",
        "",
        "## Coverage",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Expected cases | {coverage['expected_case_count']} |",
        f"| Expected arms | {coverage['expected_arm_count']} |",
        f"| Result artifacts read | {coverage['completed_result_artifacts']} |",
        f"| Pending or partial arms | {coverage['pending_or_partial_arm_count']} |",
        f"| Classifications | {json.dumps(coverage['classification_counts'], ensure_ascii=False, sort_keys=True)} |",
        "",
        "## Discovery inventories",
        "",
        "| Run | Arm | Repo-scoped combo entries | Global user combo disabled | Total entries |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for run_name in RUN_NAMES:
        for variant in VARIANTS:
            row = discovery[run_name][variant]
            global_rows = row.get("global_combo_entries", [])
            disabled = bool(global_rows) and all(
                item.get("enabled") is False for item in global_rows
            )
            lines.append(
                f"| {run_name} | {variant} | {len(row.get('repo_combo_entries', []))} | {str(disabled).lower()} | {row.get('entry_count', '') or ''} |"
            )
    lines.extend(
        [
            "",
            f"The selected discovery comparison is `{comparison['source_run']}`. Expected repo-scoped combo counts A=1 and B=13 verified: `{str(comparison['repo_combo_count_verified']).lower()}`. Global `combo` is disabled in both arms: `{str(all(comparison['global_combo_disabled'].values())).lower()}`. Unrelated inventory preserved by the comparison: `{str(comparison['unrelated_inventory']['preserved']).lower()}`.",
            "",
            f"Repo entries A: `{', '.join(comparison['repo_combo_names']['A'])}`.",
            f"Repo entries B: `{', '.join(comparison['repo_combo_names']['B'])}`.",
            "",
            "## Arm-level results",
            "",
            "Token columns retain reported input, cached input, derived uncached input, and output separately.",
            "",
            "| Run | Case | Arm | State | Classification | Completion quality | Acceptance | Wall seconds | Input | Cached | Uncached | Output | Calls | Instructions |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for record in metrics["results"]:
        tokens = record["tokens"]
        lines.append(
            "| {run} | {case} | {variant} | {state} | {classification} | {quality} | {acceptance} | {wall} | {input} | {cached} | {uncached} | {output} | {calls} | {instructions} |".format(
                run=record["run"],
                case=record["case_id"],
                variant=record["variant"],
                state=record["state"],
                classification=record.get("classification") or "",
                quality=record.get("completion_quality") or "",
                acceptance=acceptance_text(record["acceptance"]),
                wall=fmt_number(record.get("wall_time_seconds")),
                input=fmt_number(tokens.get("input_tokens")),
                cached=fmt_number(tokens.get("cached_input_tokens")),
                uncached=fmt_number(tokens.get("uncached_input_tokens")),
                output=fmt_number(tokens.get("output_tokens")),
                calls=record["tool_calls"].get("completed_unique", 0),
                instructions=record["instructions"].get("unique_path_count", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Pair view",
            "",
            "Pair wall time is the maximum recorded arm duration, reflecting the harness pair's concurrent shape. A missing arm leaves it blank.",
            "",
            "| Pair | Case | First arm | A classification | B classification | Pair wall seconds | Sum arm seconds |",
            "| ---: | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for pair in metrics["pairs"]:
        lines.append(
            f"| {pair['pair_index']} | {pair['case_id']} | {pair['first_arm']} | {pair['arm_classifications']['A'] or ''} | {pair['arm_classifications']['B'] or ''} | {fmt_number(pair['wall_time_seconds'])} | {fmt_number(pair['sum_arm_wall_time_seconds'])} |"
        )
    tokens = metrics["tokens"]
    tools = metrics["tool_calls"]
    lines.extend(
        [
            "",
            "## Aggregates",
            "",
            f"Completed result artifacts: `{tokens['completed_artifact_count']}`, with usage: `{tokens['artifacts_with_usage']}`, missing usage: `{tokens['artifacts_missing_usage']}`. Summed fields: `{json.dumps(tokens['by_arm_sum'], ensure_ascii=False, sort_keys=True)}`.",
            f"Completed unique tool calls: `{tools['completed_unique_calls']}`, by item type `{json.dumps(tools['completed_unique_calls_by_type'], ensure_ascii=False, sort_keys=True)}`.",
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {limit}" for limit in metrics["limits"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        metrics = build_metrics(args.cases.resolve(), args.audit_root.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"summarize-ab: {exc}", file=sys.stderr)
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_md.write_text(markdown_report(metrics), encoding="utf-8")
    print(
        f"Wrote {relative_path(args.output_json)} and {relative_path(args.output_md)} "
        f"({metrics['coverage']['completed_result_artifacts']}/{metrics['coverage']['expected_arm_count']} arm artifacts)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
