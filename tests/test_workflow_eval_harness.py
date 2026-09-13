import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "workflow_smoke", ROOT / "scripts" / "run-workflow-smoke.py"
)
smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(smoke)


class WorkflowEvalHarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = smoke.load_suite()
        cls.cases = {case["id"]: case for case in cls.suite["cases"]}

    def test_suite_has_six_natural_cases_without_route_names_in_prompts(self):
        self.assertEqual(
            set(self.cases),
            {
                "bug-zero",
                "inventory-feature",
                "security-review",
                "plan-adapters",
                "trivial-label",
                "translation-negative",
            },
        )
        forbidden_prompt_terms = (
            "combo",
            "matt-",
            "ecc-",
            "ponytail",
            "workflows/",
            "practices/",
        )
        for case in self.suite["cases"]:
            prompt = case["prompt"].lower()
            self.assertFalse(
                any(term in prompt for term in forbidden_prompt_terms),
                case["id"],
            )
            self.assertGreater(len(prompt), 40)

    def test_substantive_cases_require_actual_combo_path_bytes(self):
        self.assertEqual(
            self.cases["bug-zero"]["required_actual_ref_any"],
            ["combo/workflows/debug"],
        )
        self.assertEqual(
            self.cases["bug-zero"]["required_actual_ref_all"],
            ["combo/workflows/debug", "combo"],
        )
        self.assertEqual(
            self.cases["inventory-feature"]["required_actual_ref_any"],
            ["combo/workflows/deliver"],
        )
        self.assertEqual(
            self.cases["inventory-feature"]["required_actual_ref_all"],
            ["combo/workflows/deliver", "combo", "combo/practices/tests"],
        )
        self.assertEqual(
            self.cases["security-review"]["required_actual_ref_any"],
            ["combo/workflows/review"],
        )
        self.assertEqual(
            self.cases["security-review"]["required_actual_ref_all"],
            ["combo/workflows/review", "combo", "combo/practices/security"],
        )
        self.assertEqual(
            self.cases["plan-adapters"]["required_actual_ref_any"],
            ["combo/workflows/plan"],
        )
        self.assertEqual(self.cases["plan-adapters"]["required_actual_file_any"], [
            "src/notification_adapters.py",
            "src/notifications.py",
        ])

    def test_actual_reference_evidence_requires_successful_nonempty_output(self):
        events = [
            {
                "type": "item.started",
                "item": {
                    "id": "started",
                    "type": "command_execution",
                    "command": "Get-Content C:/x/.codex/skills/combo/workflows/debug.md",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "failed",
                    "type": "command_execution",
                    "command": "Get-Content C:/x/.codex/skills/combo/workflows/debug.md",
                    "aggregated_output": "",
                    "exit_code": 1,
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "read",
                    "type": "command_execution",
                    "command": "Get-Content C:/x/.codex/skills/combo/workflows/debug.md",
                    "aggregated_output": "# Debug\nReproduce the failure first.",
                    "exit_code": 0,
                },
            },
        ]
        refs, evidence = smoke.actual_references(events)
        self.assertEqual(refs, ["combo/workflows/debug"])
        self.assertEqual([row["item_id"] for row in evidence], ["read"])
        self.assertGreater(evidence[0]["output_bytes"], 0)
        self.assertEqual(len(evidence[0]["output_sha256"]), 64)

    def test_actual_fixture_file_evidence_requires_successful_output_bytes(self):
        with tempfile.TemporaryDirectory(prefix="combo-harness-test-") as temporary:
            workdir = Path(temporary)
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "id": "source-read",
                        "type": "command_execution",
                        "command": f"Get-Content {workdir / 'src' / 'orders.py'}",
                        "aggregated_output": "owner_id = current_user.id",
                        "exit_code": 0,
                    },
                }
            ]
            files, evidence = smoke.actual_files_read(
                events, workdir, ["src/orders.py"]
            )
            self.assertEqual(files, ["src/orders.py"])
            self.assertGreater(evidence[0]["output_bytes"], 0)

    def test_build_command_is_native_isolated_and_caps_limits(self):
        node = Path("C:/node.exe")
        cli = Path("C:/codex.js")
        command = smoke.build_command(
            node, cli, self.suite, self.cases["security-review"], Path("D:/combo-workflow-evals/case")
        )
        self.assertIn("--ephemeral", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--json", command)
        self.assertIn("--disable", command)
        self.assertEqual(command[command.index("--model") + 1], "gpt-5.6-luna")
        self.assertIn("model_reasoning_effort=max", command)
        self.assertIn("mcp_servers={}", command)
        self.assertIn('approval_policy="never"', command)
        self.assertNotIn("-a", command)
        self.assertNotIn("--ignore-user-config", command)
        self.assertLessEqual(self.suite["max_parallel"], 2)
        self.assertLessEqual(self.suite["timeout_seconds"], 180)

    def test_installed_native_cli_is_available_and_reports_version(self):
        launcher, executable = smoke.find_cli()
        self.assertIsNone(launcher)
        self.assertTrue(executable.is_file())
        version = subprocess.run(
            smoke.cli_prefix(launcher, executable) + ["--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(version.returncode, 0)
        self.assertIn("codex-cli", version.stdout)

    def test_seeded_quantity_acceptance_really_fails_before_fix(self):
        case = self.cases["bug-zero"]
        with tempfile.TemporaryDirectory(prefix="combo-harness-test-") as temporary:
            workdir = Path(temporary)
            shutil_fixture = smoke.FIXTURES_ROOT / case["fixture"]
            import shutil

            shutil.copytree(shutil_fixture, workdir, dirs_exist_ok=True)
            result = smoke.run_acceptance(
                smoke.EVAL_ROOT / case["acceptance"]["before"], workdir
            )
            self.assertFalse(result["passed"])
            self.assertIn("Ran 3 tests", result["stderr"] + result["stdout"])

    def test_snapshot_ignores_interpreter_cache_but_detects_real_change(self):
        with tempfile.TemporaryDirectory(prefix="combo-harness-test-") as temporary:
            root = Path(temporary)
            source = root / "src.py"
            source.write_text("before", encoding="utf-8")
            cache = root / "__pycache__" / "src.cpython-313.pyc"
            cache.parent.mkdir()
            cache.write_bytes(b"cache")
            before = smoke.snapshot_tree(root)
            source.write_text("after", encoding="utf-8")
            cache.write_bytes(b"changed cache")
            after = smoke.snapshot_tree(root)
            rows = smoke.changed_files(before, after)
            self.assertEqual([row["path"] for row in rows], ["src.py"])

    def test_plan_requires_both_real_adapters_and_translation_has_no_tools(self):
        plan = self.cases["plan-adapters"]
        self.assertEqual(len(plan["required_final_adapter_evidence"]), 2)
        self.assertEqual(
            {entry["name"] for entry in plan["required_final_adapter_evidence"]},
            {"EmailAdapter", "SmsAdapter"},
        )
        negative = self.cases["translation-negative"]
        self.assertTrue(negative["no_tools"])
        self.assertTrue(negative["no_writes"])
        self.assertIn("skills/combo", negative["forbidden_actual_ref_any"])


if __name__ == "__main__":
    unittest.main()
