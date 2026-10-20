"""Run paired Shortcut-First probes through Combo's native CLI A/B harness.

The default suite has eight cases and three sequential pairs per case. The
variants use the same model, effort, policy, and fixtures; no model call occurs
on import. Review raw events and visual artifacts before drawing quality
conclusions. Global host policy remains a shared confound, and the runner does
not provide filesystem isolation.
"""

import argparse
import copy
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "outcome_ab", ROOT / "scripts/run-ab-eval.py"
)
assert SPEC is not None and SPEC.loader is not None
ab: Any = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ab)

AB_CASES = json.loads(
    (ROOT / "evals/ab/cases.json").read_text(encoding="utf-8")
)["cases"]
AB_CASES_BY_ID = {case["id"]: case for case in AB_CASES}
CASES = [
    AB_CASES_BY_ID["trivial-label"],
    AB_CASES_BY_ID["bug-zero"],
    AB_CASES_BY_ID["inventory-feature"],
    AB_CASES_BY_ID["security-review"],
    {
        "id": "research-source-triage",
        "fixture": "research-source-triage",
        "sandbox": "read-only",
        "no_writes": True,
        "required_actual_files": ["api-reference.md", "migration-guide.md"],
        "prompt": "จากเอกสารใน fixture เท่านั้น ตอบว่า API version 4.2 cache image payload หรือไม่ ระบุชื่อไฟล์และวันที่ของหลักฐาน และอธิบายว่าเหตุใด migration guide จึงขัดกัน ห้ามแก้ไฟล์",
    },
    AB_CASES_BY_ID["content-repurpose"],
    {
        "id": "ui-reference",
        "fixture": "ui-reference",
        "sandbox": "workspace-write",
        "allowed_changed_paths": ["style.css", "desktop.png", "mobile.png"],
        "required_actual_files": ["index.html", "style.css", "notes.md"],
        "acceptance": {
            "before": "ui_test.py",
            "after": "ui_test.py",
            "before_must_fail": True,
            "after_must_pass": True,
        },
        "prompt": "ปรับหน้าเว็บเดิมให้ตรงกับ reference-desktop.png และ reference-mobile.png โดยรักษา design intent และการกด Save note เดิม ตรวจภาพจริงทั้งสอง viewport ก่อนส่ง แก้เฉพาะ style.css และบันทึกภาพผลได้ที่ desktop.png กับ mobile.png",
    },
    {
        "id": "anime-hair",
        "fixture": "anime-hair",
        "sandbox": "workspace-write",
        "required_actual_files": ["hair.json", "render.py", "notes.md"],
        "acceptance": {
            "before": "hair_test.py",
            "after": "hair_test.py",
            "before_must_fail": True,
            "after_must_pass": True,
        },
        "prompt": "ปรับผมของตัวละครเดิมให้ตรงกับ shape reference (reference.png มี front, side, back) โดยคง bang pattern ด้านหน้า สีม่วงลาเวนเดอร์ และ neutral pose ตามที่มีอยู่ ห้ามแก้ reference.png หรือ render.py ส่งมอบภาพ projection ที่ render จากโมเดลที่ปรับแล้ว และบอกว่าตรวจเทียบกับ reference อย่างไร",
    },
    {
        "id": "ambiguous-export",
        "fixture": "ambiguous-export",
        "sandbox": "read-only",
        "no_writes": True,
        "required_actual_files": ["exporter.py", "caller.py", "notes.md"],
        "prompt": "แก้ปุ่ม Export ให้ได้ทุกอย่าง แทนที่จะได้แค่หน้านี้ คง tenant isolation ไว้ ดูของเดิมก่อนแล้วทำต่อให้เหมาะสม",
    },
]


def pair_order(repeat_index: int, case_index: int) -> tuple[str, str]:
    return (
        ("baseline", "patched")
        if (repeat_index + case_index) % 2 == 0
        else ("patched", "baseline")
    )


def completion_gate(result, events):
    """Reject false completion without treating timeout or a proposal as success."""
    failures = list(result["environment_failures"]) + list(result["task_failures"])
    if not any(event.get("type") == "turn.completed" for event in events):
        failures.append("no completed model turn (progress text is not completion)")
    return failures


def hair_scope_failures(changes):
    # The prompt did not prescribe PNG names. Preserve the reference and
    # renderer, while accepting generated root-level image artifacts.
    return [
        row["path"]
        for row in changes
        if not (
            row["path"] == "hair.json"
            or (
                row["change"] == "created"
                and "/" not in row["path"]
                and Path(row["path"]).suffix == ".png"
            )
        )
    ]


def reference_reads(events):
    # Normalize a copy for the legacy detector, preserving raw CLI events.
    normalized = []
    for event in events:
        item = dict(event.get("item", {}))
        if isinstance(item.get("command"), str):
            item["command"] = re.sub(r"\\+", "/", item["command"])
        normalized.append({**event, "item": item})
    return ab.SMOKE.actual_references(normalized)


def render_references(fixtures):
    hair = fixtures / "anime-hair"
    ui = fixtures / "ui-reference"
    if hair.is_dir():
        spec = importlib.util.spec_from_file_location(
            "hair_proxy", hair / "render.py"
        )
        assert spec is not None and spec.loader is not None
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        target = json.loads((hair / "hair.json").read_text())
        target.update(back_length=148, side_width=43)
        renderer.render(target, hair / "reference.png")
    if ui.is_dir():
        from playwright.sync_api import sync_playwright

        original = (ui / "style.css").read_text()
        target_css = (
            original.replace("padding:28px 24px", "padding:28px 80px")
            .replace("padding:64px 24px", "padding:64px 80px")
            .replace("grid-row:1", "grid-row:auto")
        )
        try:
            (ui / "style.css").write_text(target_css)
            with sync_playwright() as runtime:
                browser = runtime.chromium.launch(headless=True)
                page = browser.new_page()
                for name, width, height in (
                    ("desktop", 1100, 700),
                    ("mobile", 390, 844),
                ):
                    page.set_viewport_size({"width": width, "height": height})
                    page.goto((ui / "index.html").as_uri())
                    page.screenshot(path=str(ui / f"reference-{name}.png"))
                browser.close()
        finally:
            (ui / "style.css").write_text(original)


def collect_fixtures(run_root, cases):
    fixtures = run_root / "common-fixtures"
    fixtures.mkdir()
    for name in sorted({case["fixture"] for case in cases}):
        candidates = (HERE / "fixtures" / name, ROOT / "evals/ab/fixtures" / name)
        source = next((path for path in candidates if path.is_dir()), None)
        if source is None:
            raise FileNotFoundError(f"fixture not found: {name}")
        shutil.copytree(source, fixtures / name)
    return fixtures


def stage(source, destination, fixtures, fixture_name):
    shutil.copytree(source / "skills", destination / "skills")
    (destination / "fixtures").mkdir()
    shutil.copytree(fixtures / fixture_name, destination / "fixtures" / fixture_name)
    for fixture in (destination / "fixtures").iterdir():
        shutil.copy2(source / "POLICY.md", fixture / "POLICY.md")
        (fixture / "AGENTS.md").write_text(
            "Use the local .agents/skills/combo-* entry for substantive work, "
            "and its linked workflow and context. Read local POLICY.md. "
            "Preserve supplied references and existing constraints. Do not "
            "install tools, start services, publish, or delegate. Keep generated "
            "files in this case workspace; do not inspect another arm, sibling "
            "cases, results, prior runs, or paths outside this workspace.\n",
            encoding="utf-8",
        )


def remove_owned_tree(path, allowed_root):
    target = path.resolve()
    root = allowed_root.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Refusing cleanup outside generated root: {target}")
    shutil.rmtree(target, ignore_errors=False)


def preserve_ui_artifacts(result, output, case_id, arm, repeat_index):
    workdir = result.get("workdir")
    if not workdir or case_id != "ui-reference":
        return []
    source = Path(workdir)
    destination = output / "visuals" / f"{case_id}-r{repeat_index + 1}"
    destination.mkdir(parents=True, exist_ok=True)
    saved = []
    for name in ("desktop.png", "mobile.png"):
        path = source / name
        if path.is_file():
            target = destination / f"{arm}-{name}"
            shutil.copy2(path, target)
            saved.append(str(target))
    return saved


def result_summary(result):
    return {
        key: result.get(key)
        for key in (
            "case_family",
            "case_id",
            "pair_repeat",
            "variant",
            "mechanical_verdict",
            "duration_seconds",
            "usage",
            "tool_count",
            "workflow_reference_count",
            "completion_gate_failures",
            "result_path",
            "workdir",
        )
    }


def expected_result_ids(selected_cases, repeat):
    return {
        (f"{case['id']}-r{index}", arm)
        for case in selected_cases
        for index in range(1, repeat + 1)
        for arm in ("baseline", "patched")
    }


def load_result_payloads(output, selected_cases, repeat):
    valid_ids = expected_result_ids(selected_cases, repeat)
    results = {}
    for path in (output / "arms").glob("*/*/result.json"):
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        key = (result.get("case_id"), result.get("variant"))
        if key not in valid_ids:
            continue
        if not all(
            field in result
            for field in (
                "case_family",
                "pair_repeat",
                "mechanical_verdict",
                "usage",
                "tool_count",
                "completion_gate_failures",
            )
        ):
            continue
        results[key] = result
    return results


def environmental_retry_pairs(payloads):
    return {
        (result["case_family"], result["pair_repeat"])
        for result in payloads.values()
        if result.get("environment_failures")
    }


def preserve_environmental_retry_pairs(output, payloads):
    """Archive both arms of interrupted pairs before retrying their outputs."""
    retry_pairs = environmental_retry_pairs(payloads)
    if not retry_pairs:
        raise ValueError("no environmental failures found to retry")
    attempt = 1
    while (output / "attempts" / f"pre-retry-{attempt}").exists():
        attempt += 1
    archive_root = output / "attempts" / f"pre-retry-{attempt}"
    archived = []
    for result in payloads.values():
        pair = (result["case_family"], result["pair_repeat"])
        if pair not in retry_pairs:
            continue
        source = Path(result["result_path"]).parent
        destination = archive_root / result["case_id"] / result["variant"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
        archived.append(
            {
                "case_id": result["case_id"],
                "variant": result["variant"],
                "environment_failures": result.get("environment_failures", []),
                "archived_result_path": str(destination / "result.json"),
            }
        )
    manifest = {
        "reason": "retry paired comparison after environmental interruption",
        "pairs": [
            {"case_family": case_family, "pair_repeat": repeat_index}
            for case_family, repeat_index in sorted(retry_pairs)
        ],
        "archived_arms": archived,
    }
    archive_root.mkdir(parents=True, exist_ok=True)
    (archive_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_completed_results(
    output, selected_cases, repeat, retry_environmental_pairs=False
):
    """Recover completed arms, optionally reopening both arms of failed pairs."""
    payloads = load_result_payloads(output, selected_cases, repeat)
    retry_pairs = (
        environmental_retry_pairs(payloads) if retry_environmental_pairs else set()
    )
    results = {}
    for key, result in payloads.items():
        pair = (result.get("case_family"), result.get("pair_repeat"))
        if pair in retry_pairs:
            continue
        results[key] = result_summary(result)
    return list(results.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--work-root", type=Path, default=Path("D:/combo-outcome-evals")
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="continue a prior output directory without repeating completed arms",
    )
    parser.add_argument(
        "--retry-environmental-pairs",
        action="store_true",
        help="on resume, archive and rerun both arms of each environmentally failed pair",
    )
    parser.add_argument(
        "--case", choices=[case["id"] for case in CASES], action="append"
    )
    args = parser.parse_args()
    if not 1 <= args.repeat <= 5:
        parser.error("repeat must be 1..5")
    if not 60 <= args.timeout <= 600:
        parser.error("timeout must be 60..600 seconds")
    requested_cases = set(args.case or [])
    selected_cases = [
        case for case in CASES if not requested_cases or case["id"] in requested_cases
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    args.work_root.mkdir(parents=True, exist_ok=True)
    if args.retry_environmental_pairs and not args.resume:
        parser.error("--retry-environmental-pairs requires --resume")
    metadata_path = args.output / "run.json"
    if args.resume:
        if args.stage_only or not metadata_path.is_file():
            parser.error("--resume requires a previous non-stage-only run.json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if (
            metadata.get("case_ids") != [case["id"] for case in selected_cases]
            or metadata.get("pairs_per_case") != args.repeat
            or Path(metadata.get("baseline", "")).resolve()
            != args.baseline.resolve()
        ):
            parser.error("resume settings must match the original cases, repeat, and baseline")
        run_root = Path(metadata["run_root"]).resolve()
        if run_root.parent != args.work_root.resolve() or not run_root.is_dir():
            parser.error("original run root must exist directly inside --work-root")
        active_root = Path(
            tempfile.mkdtemp(prefix="continuation-", dir=run_root)
        )
        metadata.setdefault("continuation_roots", []).append(str(active_root))
        if args.retry_environmental_pairs:
            payloads = load_result_payloads(args.output, selected_cases, args.repeat)
            retry_manifest = preserve_environmental_retry_pairs(args.output, payloads)
            metadata.setdefault("retry_history", []).append(retry_manifest)
        results = load_completed_results(
            args.output,
            selected_cases,
            args.repeat,
            retry_environmental_pairs=args.retry_environmental_pairs,
        )
    else:
        run_root = Path(tempfile.mkdtemp(prefix="paired-", dir=args.work_root))
        active_root = run_root
        metadata = {
            "model": "gpt-5.6-luna",
            "reasoning_effort": "max",
            "pairs_per_case": args.repeat,
            "case_ids": [case["id"] for case in selected_cases],
            "expected_arms": len(selected_cases) * args.repeat * 2,
            "baseline": str(args.baseline.resolve()),
            "patched": str(ROOT),
            "run_root": str(run_root),
            "continuation_roots": [],
            "timeout_seconds": args.timeout,
            "stage_only": args.stage_only,
            "limits": "shared global host policy; synthetic fixtures; selected cases and repetitions are a bounded sample, not a multi-model or domain-wide claim; no multi-turn rework measurement",
        }
        results = []
    staging_root = active_root / "staging"
    variants_root = active_root / "variants"
    metadata["status"] = "in_progress"
    (args.output / "run.json").write_text(json.dumps(metadata, indent=2))
    if args.stage_only:
        for case in selected_cases:
            fixture_root = staging_root / case["id"]
            fixture_root.mkdir(parents=True)
            fixtures = collect_fixtures(fixture_root, [case])
            render_references(fixtures)
            for name, source in (("baseline", args.baseline), ("patched", ROOT)):
                stage(
                    source,
                    variants_root / case["id"] / name,
                    fixtures,
                    case["fixture"],
                )
        print(json.dumps(metadata))
        return 0
    original_acceptance = ab.acceptance

    def local_acceptance(name, cwd):
        if Path(name).name != name:
            raise ValueError(f"invalid acceptance name: {name}")
        roots = (HERE / "acceptance", ROOT / "evals/ab/acceptance")
        root = next((path for path in roots if (path / name).is_file()), None)
        if root is None:
            raise FileNotFoundError(f"acceptance not found: {name}")
        previous = ab.ACCEPTANCE
        ab.ACCEPTANCE = root
        try:
            return original_acceptance(name, cwd)
        finally:
            ab.ACCEPTANCE = previous

    ab.acceptance = local_acceptance
    original_rows = ab.rows_for

    def local_rows(variant_root, global_combo):
        rows = original_rows(variant_root, global_combo)
        for parent in (Path.home() / ".codex/skills", Path.home() / ".agents/skills"):
            for entry in parent.glob("combo*/SKILL.md"):
                rows.append({"path": str(entry.resolve()), "enabled": False})
        return rows

    ab.rows_for = local_rows
    _, cli = ab.SMOKE.find_cli()
    mcp = ab.SMOKE.configured_mcp_names()
    expected_arms = len(selected_cases) * args.repeat * 2
    for repeat_index in range(args.repeat):
        for index, base_case in enumerate(selected_cases):
            case = copy.deepcopy(base_case)
            case["id"] = f"{base_case['id']}-r{repeat_index + 1}"
            order = pair_order(repeat_index, index)
            pair_index = repeat_index * len(selected_cases) + index + 1
            completed_keys = {
                (row["case_id"], row["variant"]) for row in results
            }
            if all((case["id"], arm) in completed_keys for arm in order):
                continue
            fixture_root = staging_root / case["id"]
            fixture_root.mkdir(parents=True)
            fixtures = collect_fixtures(fixture_root, [base_case])
            render_references(fixtures)
            case_variants = variants_root / case["id"]
            if base_case["id"] == "ui-reference":
                visual_root = args.output / "visuals" / case["id"]
                visual_root.mkdir(parents=True, exist_ok=True)
                for name in ("reference-desktop.png", "reference-mobile.png"):
                    shutil.copy2(
                        fixtures / base_case["fixture"] / name,
                        visual_root / name,
                    )
            for arm in order:
                if (case["id"], arm) in completed_keys:
                    print(f"SKIP {case['id']} {arm}: completed result exists", flush=True)
                    continue
                print(f"START {case['id']} {arm}", flush=True)
                variant_root = case_variants / arm
                variant_root.parent.mkdir(parents=True, exist_ok=True)
                source = args.baseline if arm == "baseline" else ROOT
                stage(source, variant_root, fixtures, base_case["fixture"])
                execution_root = active_root / "executions" / arm / case["id"]
                execution_root.mkdir(parents=True, exist_ok=True)
                result = ab.run_arm(
                    cli,
                    metadata,
                    case,
                    arm,
                    variant_root,
                    ab.global_combo_path(),
                    mcp,
                    args.output,
                    execution_root,
                    args.timeout,
                    pair_index,
                    order[0],
                    True,
                )
                result["saved_visual_artifacts"] = preserve_ui_artifacts(
                    result, args.output, base_case["id"], arm, repeat_index
                )
                if base_case["id"] == "anime-hair":
                    result["task_failures"] = list(result["task_failures"]) + [
                        f"changed protected path: {path}"
                        for path in hair_scope_failures(result["changed_files"])
                    ]
                workdir = result.get("workdir")
                if workdir:
                    remove_owned_tree(Path(workdir), execution_root)
                    result["workdir"] = None
                    result["workdir_removed_after_capture"] = True
                remove_owned_tree(variant_root, case_variants)
                events, _ = ab.SMOKE.parse_events(
                    Path(result["events_path"]).read_text(encoding="utf-8")
                )
                result["completion_gate_failures"] = completion_gate(result, events)
                references, evidence = reference_reads(events)
                result["normalized_actual_references"] = references
                result["normalized_reference_evidence"] = [
                    {key: value for key, value in row.items() if key != "output"}
                    for row in evidence
                ]
                result["case_family"] = base_case["id"]
                result["pair_repeat"] = repeat_index + 1
                result["workflow_reference_count"] = sum(
                    "workflows/" in ref.lower() or "practices/" in ref.lower()
                    for ref in references
                )
                result["mechanical_verdict"] = (
                    "fail" if result["completion_gate_failures"] else "pass"
                )
                Path(result["result_path"]).write_text(
                    json.dumps(result, ensure_ascii=False, indent=2)
                )
                results.append(result_summary(result))
                summary = {
                    "metadata": metadata,
                    "completed_arms": len(results),
                    "expected_arms": expected_arms,
                    "arms": results,
                }
                (args.output / "summary.json").write_text(
                    json.dumps(summary, ensure_ascii=False, indent=2)
                )
                print(
                    f"END {case['id']} {arm}: {result['mechanical_verdict']}",
                    flush=True,
                )
            remove_owned_tree(case_variants, variants_root)
            remove_owned_tree(fixture_root, staging_root)
    metadata["status"] = "complete"
    (args.output / "run.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2)
    )
    return int(any(result["mechanical_verdict"] == "fail" for result in results))


if __name__ == "__main__":
    sys.exit(main())
