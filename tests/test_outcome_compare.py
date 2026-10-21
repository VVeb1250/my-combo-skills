import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("outcome_compare", ROOT / "scripts" / "run-outcome-compare.py")
oc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(oc)


class CompareCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["id"]: c for c in oc.load_cases()}

    def test_ten_cases_with_fixtures_and_acceptance_on_disk(self):
        self.assertEqual(len(self.cases), 10)
        for case in self.cases.values():
            self.assertTrue((case["_root"] / "fixtures" / case["fixture"]).is_dir(), case["id"])
            for key in ("before", "after"):
                rel = case.get("acceptance", {}).get(key)
                if rel:
                    self.assertTrue((case["_root"] / rel).is_file(), case["id"])

    def test_shared_root_cause_fixture_fails_before_the_fix(self):
        case = self.cases["shared-root-cause"]
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            shutil.copytree(case["_root"] / "fixtures" / case["fixture"], work, dirs_exist_ok=True)
            result = oc.run_acceptance_script(case["_root"] / case["acceptance"]["before"], work)
            self.assertFalse(result["passed"])
            (work / "src" / "money.py").write_text(
                'def to_cents(amount):\n    return round(amount * 100)\n', encoding="utf-8")
            result = oc.run_acceptance_script(case["_root"] / case["acceptance"]["after"], work)
            self.assertTrue(result["passed"], result["tail"])

    def test_patching_only_the_cart_caller_is_not_enough(self):
        case = self.cases["shared-root-cause"]
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            shutil.copytree(case["_root"] / "fixtures" / case["fixture"], work, dirs_exist_ok=True)
            (work / "src" / "cart.py").write_text(
                "def cart_total_cents(prices):\n    return sum(round(p * 100) for p in prices)\n", encoding="utf-8")
            result = oc.run_acceptance_script(case["_root"] / case["acceptance"]["after"], work)
            self.assertFalse(result["passed"])


class CompareScoring(unittest.TestCase):
    def setUp(self):
        self.cases = {c["id"]: c for c in oc.load_cases()}

    def score(self, case_id, answer="Done.", changed=(), before=None, after=None, commands=(), tools=0):
        rows = [{"path": p} for p in changed]
        return oc.score_outcome(self.cases[case_id], answer, rows, before, after, list(commands), tools, Path("."))

    def test_scope_violation_and_failed_acceptance_are_failures(self):
        failures = self.score("bug-zero", changed=["src/quantity.py", "README.md"],
                              before={"passed": False}, after={"passed": False})
        self.assertTrue(any("acceptance did not pass" in f for f in failures))
        self.assertTrue(any("outside scope" in f for f in failures))

    def test_clean_pass(self):
        self.assertEqual(self.score("bug-zero", changed=["src/quantity.py"],
                                    before={"passed": False}, after={"passed": True}), [])

    def test_diagnosis_needs_cause_and_no_writes(self):
        good = "`value or 1` treats the falsy 0 like a missing None."
        self.assertEqual(self.score("diagnose-only", answer=good), [])
        self.assertTrue(self.score("diagnose-only", answer=good, changed=["src/quantity.py"]))
        self.assertTrue(self.score("diagnose-only", answer="It is a bug."))

    def test_no_tool_case_rejects_tools(self):
        self.assertTrue(self.score("translation-negative", answer="ใบแจ้งหนี้พร้อมสำหรับการตรวจสอบ", tools=1))
        self.assertEqual(self.score("translation-negative", answer="ใบแจ้งหนี้พร้อมสำหรับการตรวจสอบ"), [])


class ClaimDetection(unittest.TestCase):
    def test_negated_thai_and_english_edits_are_not_claims(self):
        for text in ("ผมไม่ได้แก้ไฟล์ใดครับ", "ไม่ได้แก้ไฟล์ เพิ่มหรือรันทดสอบ", "I have not changed any files.",
                     "I did not modify the code.", "I read the whole file and the README, and I changed nothing.",
                     "I changed no files."):
            self.assertFalse(oc.claims_implementation(text), text)

    def test_real_claims_are_detected(self):
        for text in ("I fixed the parser and added tests.", "ผมแก้ไฟล์ quantity.py แล้ว", "I have implemented the gateway."):
            self.assertTrue(oc.claims_implementation(text), text)


class CompareAnalysis(unittest.TestCase):
    def test_claude_events_reduce_to_cost_and_workflow_flag(self):
        events = [
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "combo-debug"}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "python -m unittest"}}]}},
            {"type": "result", "subtype": "success", "result": "fixed", "num_turns": 4, "total_cost_usd": 0.2,
             "usage": {"input_tokens": 1, "cache_creation_input_tokens": 2, "cache_read_input_tokens": 3,
                       "output_tokens": 4}},
        ]
        got = oc.analyze_claude(events)
        self.assertTrue(got["workflow_loaded"])
        self.assertEqual(got["tokens_total"], 10)
        self.assertEqual(got["commands"], ["python -m unittest"])
        self.assertEqual(got["tool_count"], 2)

    def test_arms_are_declared_per_host(self):
        self.assertEqual(oc.CLAUDE_ARMS["no-claude-md"], {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"})
        args = oc.parse_args(["--host", "codex", "--arms", "full", "home:x", "--codex-home", "x=C:/h"])
        self.assertEqual(args.codex_homes, {"x": "C:/h"})


class InlineArm(unittest.TestCase):
    def test_inline_plugin_keeps_descriptions_and_removes_the_read_steps(self):
        import re, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            plugin = oc.build_inline_plugin(Path(tmp) / "plugin", home=Path("C:/home"))
            for name in oc.INLINE_WORKFLOWS:
                stub = (ROOT / "adapters" / "claude" / "overrides" / f"combo-{name}" / "SKILL.md").read_text(encoding="utf-8")
                built = (plugin / "skills" / f"combo-{name}" / "SKILL.md").read_text(encoding="utf-8")
                desc = lambda t: re.findall(r"^description: (.*)$", t, re.M)[0]
                self.assertEqual(desc(stub), desc(built), name)
                workflow = (ROOT / "skills" / "combo" / "workflows" / f"{name}.md").read_text(encoding="utf-8")
                self.assertIn(workflow.splitlines()[0], built, name)
                self.assertIn("## Context selection and reporting (inlined)", built, name)
                self.assertNotIn("Read [context]", built, name)
                self.assertNotIn("${CLAUDE_SKILL_DIR}", built, name)
                self.assertNotIn("](../", built, name)
                self.assertIn("C:/home/.claude/skills/combo/", built, name)
            self.assertTrue((plugin / ".claude-plugin" / "plugin.json").is_file())

    def test_inline_arm_command_swaps_the_entries_and_other_arms_do_not(self):
        case = {"prompt": "p", "sandbox": "read-only"}
        inline = oc.claude_command("claude", case, "sonnet", 5, "inline", Path("X/plugin"))
        self.assertIn("--plugin-dir", inline)
        settings = inline[inline.index("--settings") + 1]
        for name in oc.INLINE_WORKFLOWS:
            self.assertIn(f'"combo-{name}":"off"', settings)
        full = oc.claude_command("claude", case, "sonnet", 5, "full")
        self.assertNotIn("--plugin-dir", full)
        self.assertNotIn("skillOverrides", full[full.index("--settings") + 1])


if __name__ == "__main__":
    unittest.main()
