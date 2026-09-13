"""Two sequential live probes using the existing isolated Codex smoke harness.

Run explicitly; importing this module does not launch a model. Results require
semantic review and do not establish a token saving or an all-model guarantee.
"""

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument(
        "--work-root",
        type=Path,
        default=Path(ROOT.anchor if os.name == "nt" else tempfile.gettempdir())
        / "combo-context-evals",
    )
    args = parser.parse_args()
    if not 30 <= args.timeout <= 600:
        parser.error("timeout must be 30..600 seconds")
    spec = importlib.util.spec_from_file_location(
        "combo_smoke", ROOT / "scripts/run-workflow-smoke.py"
    )
    assert spec is not None and spec.loader is not None
    harness: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    suite = harness.load_suite(ROOT / "evals/v2/cases.json")
    harness.EVAL_ROOT = HERE
    harness.FIXTURES_ROOT = HERE / "fixtures"
    launcher, cli = harness.find_cli()
    mcp_names = harness.configured_mcp_names()
    base_command = harness.build_command

    def probe_command(launcher, cli, suite, case, workdir, mcp_names):
        command = base_command(launcher, cli, suite, case, workdir, mcp_names)
        key = str(workdir.resolve())
        if os.name == "nt":
            key = key.lower()
        return command + ["-c", f'projects.{json.dumps(key)}.trust_level="trusted"']

    harness.build_command = probe_command
    args.work_root.mkdir(parents=True, exist_ok=True)
    work_root = Path(
        tempfile.mkdtemp(prefix="combo-context-probes-", dir=args.work_root)
    )
    cases = [
        {
            "id": "diagnosis",
            "title": "Diagnose using the live caller contract, without edits",
            "fixture": "empty-selection",
            "sandbox": "danger-full-access",
            "no_writes": True,
            "prompt": (
                "Diagnose why clearing all catalog checkboxes reselects every "
                "label. Inspect the current code and explain the cause and "
                "smallest repair with verification. Diagnosis only: do not "
                "modify files. Preserve the initial-load default behavior."
            ),
        },
        {
            "id": "repair",
            "title": "Repair selection while retaining callers and iterable behavior",
            "fixture": "empty-selection",
            "sandbox": "danger-full-access",
            "allowed_changed_paths": ["src/catalog.py", "tests/test_catalog.py"],
            "acceptance": {
                "before": "acceptance/selection_test.py",
                "after": "acceptance/selection_test.py",
                "before_must_fail": True,
                "after_must_pass": True,
            },
            "prompt": (
                "Fix the catalog checkbox bug: clearing all selections must "
                "stay empty, and initial-load defaults must still work. "
                "Preserve existing valid-label filtering, order, duplicates, "
                "and support for iterables. Inspect the live callers. Keep "
                "edits in src/catalog.py and tests/test_catalog.py, verify "
                "the behavior, and finish."
            ),
        },
    ]
    results = []
    for case in cases:
        result = harness.run_case(
            suite,
            case,
            launcher,
            cli,
            args.output,
            work_root,
            mcp_names,
            args.timeout,
            True,
        )
        results.append(
            {
                key: result[key]
                for key in (
                    "case_id",
                    "status",
                    "failures",
                    "duration_seconds",
                    "usage",
                    "actual_references_read",
                    "changed_files",
                    "workdir",
                )
            }
        )
        print(f"{case['id']}: {result['status']}", flush=True)
    (args.output / "summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return int(any(result["status"] != "passed" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
