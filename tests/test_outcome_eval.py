"""Acceptance/gate regressions; importing the harness never launches a model."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "outcome_eval", ROOT / "evals/outcome/run.py"
)
assert SPEC is not None and SPEC.loader is not None
outcome = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(outcome)


class OutcomeChecks(unittest.TestCase):
    def test_shortcut_suite_stages_nine_selected_cases(self):
        expected = {
            "trivial-label",
            "bug-zero",
            "inventory-feature",
            "security-review",
            "research-source-triage",
            "content-repurpose",
            "ui-reference",
            "anime-hair",
            "ambiguous-export",
        }
        self.assertEqual({case["id"] for case in outcome.CASES}, expected)
        with tempfile.TemporaryDirectory() as directory:
            fixtures = outcome.collect_fixtures(Path(directory), outcome.CASES)
            self.assertEqual(
                {path.name for path in fixtures.iterdir()},
                {case["fixture"] for case in outcome.CASES},
            )

    def test_first_arm_alternates_by_case_and_repeat(self):
        for repeat_index in range(3):
            for case_index in range(len(outcome.CASES)):
                first, second = outcome.pair_order(repeat_index, case_index)
                self.assertIn((first, second), [("baseline", "patched"), ("patched", "baseline")])
                self.assertNotEqual(
                    first,
                    outcome.pair_order(repeat_index + 1, case_index)[0],
                )

    def test_resume_loads_only_complete_results_for_selected_arms(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result_path = output / "arms/patched/bug-zero-r1/result.json"
            result_path.parent.mkdir(parents=True)
            result_path.write_text(
                json.dumps(
                    {
                        "case_family": "bug-zero",
                        "case_id": "bug-zero-r1",
                        "pair_repeat": 1,
                        "variant": "patched",
                        "mechanical_verdict": "pass",
                        "duration_seconds": 10,
                        "usage": {"input_tokens": 100},
                        "tool_count": 2,
                        "workflow_reference_count": 1,
                        "completion_gate_failures": [],
                        "result_path": str(result_path),
                        "workdir": None,
                    }
                )
            )
            self.assertEqual(
                outcome.load_completed_results(
                    output, [{"id": "bug-zero"}], repeat=1
                )[0]["variant"],
                "patched",
            )
            self.assertEqual(
                outcome.load_completed_results(
                    output, [{"id": "trivial-label"}], repeat=1
                ),
                [],
            )

    def test_environmental_retry_archives_and_reopens_both_pair_arms(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for variant, failures in (
                ("baseline", []),
                ("patched", ["usage limit"]),
            ):
                result_path = output / f"arms/{variant}/bug-zero-r1/result.json"
                result_path.parent.mkdir(parents=True)
                result_path.write_text(
                    json.dumps(
                        {
                            "case_family": "bug-zero",
                            "case_id": "bug-zero-r1",
                            "pair_repeat": 1,
                            "variant": variant,
                            "mechanical_verdict": "fail" if failures else "pass",
                            "duration_seconds": 10,
                            "usage": {"input_tokens": 100},
                            "tool_count": 2,
                            "workflow_reference_count": 1,
                            "completion_gate_failures": failures,
                            "environment_failures": failures,
                            "result_path": str(result_path),
                            "workdir": None,
                        }
                    )
                )
            selected = [{"id": "bug-zero"}]
            self.assertEqual(
                len(outcome.load_completed_results(output, selected, repeat=1)), 2
            )
            self.assertEqual(
                outcome.load_completed_results(
                    output,
                    selected,
                    repeat=1,
                    retry_environmental_pairs=True,
                ),
                [],
            )
            manifest = outcome.preserve_environmental_retry_pairs(
                output, outcome.load_result_payloads(output, selected, repeat=1)
            )
            self.assertEqual(
                manifest["pairs"],
                [{"case_family": "bug-zero", "pair_repeat": 1}],
            )
            archived = output / "attempts/pre-retry-1/bug-zero-r1"
            self.assertTrue((archived / "baseline/result.json").is_file())
            self.assertTrue((archived / "patched/result.json").is_file())

    def test_progress_and_zero_exit_are_insufficient(self):
        result = {"environment_failures": [], "task_failures": []}
        self.assertTrue(outcome.completion_gate(result, [{"type": "item.completed"}]))
        self.assertFalse(outcome.completion_gate(result, [{"type": "turn.completed"}]))
        result["task_failures"] = ["independent acceptance failed"]
        self.assertTrue(outcome.completion_gate(result, [{"type": "turn.completed"}]))
        result["task_failures"] = []
        result["environment_failures"] = ["usage limit"]
        self.assertTrue(outcome.completion_gate(result, [{"type": "turn.completed"}]))

    def run_acceptance(self, name, fixture):
        environment = {**os.environ, "COMBO_EVAL_ROOT": str(fixture)}
        return subprocess.run(
            [sys.executable, str(ROOT / "evals/outcome/acceptance" / name)],
            env=environment,
            capture_output=True,
            timeout=60,
            check=False,
        )

    def test_hair_rejects_unfixed_and_style_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            shutil.copytree(
                ROOT / "evals/outcome/fixtures/anime-hair", fixture, dirs_exist_ok=True
            )
            self.assertNotEqual(
                self.run_acceptance("hair_test.py", fixture).returncode, 0
            )
            model = json.loads((fixture / "hair.json").read_text())
            model.update(back_length=148, side_width=43)
            (fixture / "hair.json").write_text(json.dumps(model))
            render = subprocess.run(
                [sys.executable, "render.py"],
                cwd=fixture,
                capture_output=True,
                check=False,
            )
            self.assertEqual(render.returncode, 0, render.stderr)
            shutil.copy2(fixture / "preview.png", fixture / "reference.png")
            (fixture / "preview.png").rename(fixture / "arbitrary-output-name.png")
            self.assertEqual(self.run_acceptance("hair_test.py", fixture).returncode, 0)
            model["bangs"][0] = 99
            (fixture / "hair.json").write_text(json.dumps(model))
            self.assertNotEqual(
                self.run_acceptance("hair_test.py", fixture).returncode, 0
            )

    def test_scope_accepts_unspecified_output_names_but_protects_reference(self):
        self.assertFalse(
            outcome.hair_scope_failures(
                [
                    {"path": "final.png", "change": "created"},
                    {"path": "hair.json", "change": "modified"},
                ]
            )
        )
        for path in ["reference.png", "render.py", "notes.md"]:
            self.assertTrue(
                outcome.hair_scope_failures([{"path": path, "change": "modified"}])
            )

    def test_current_cli_escaped_paths_still_prove_reads(self):
        refs, _ = outcome.reference_reads(
            [
                {
                    "type": "item.completed",
                    "item": {
                        "id": "read",
                        "type": "command_execution",
                        "exit_code": 0,
                        "command": r"Get-Content .agents\\skills\\combo\\practices\\context.md",
                        "aggregated_output": "# Context selection and reporting",
                    },
                }
            ]
        )
        self.assertIn("combo/practices/context", refs)

    def test_ui_rejects_seed_then_checks_actual_browser_journey(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            shutil.copytree(
                ROOT / "evals/outcome/fixtures/ui-reference",
                fixture,
                dirs_exist_ok=True,
            )
            self.assertNotEqual(
                self.run_acceptance("ui_test.py", fixture).returncode, 0
            )
            style = fixture / "style.css"
            style.write_text(
                style.read_text()
                .replace("padding:64px 24px", "padding:64px 80px")
                .replace("grid-row:1", "grid-row:auto")
            )
            result = self.run_acceptance("ui_test.py", fixture)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_direct_workflows_reach_shared_context(self):
        for entry in (ROOT / "skills").glob("combo-*/SKILL.md"):
            if entry.parent.name == "combo-maintain":
                continue
            name = entry.parent.name.removeprefix("combo-")
            workflow = ROOT / "skills/combo/workflows" / f"{name}.md"
            self.assertIn(f"workflows/{name}.md", entry.read_text())
            self.assertIn("practices/context.md", workflow.read_text())
        self.assertTrue((ROOT / "skills/combo/practices/outcome-evidence.md").is_file())


if __name__ == "__main__":
    unittest.main()
