import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("routing_probe", ROOT / "scripts" / "run-routing-probe.py")
probe = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(probe)


def assistant(*blocks):
    return {"type": "assistant", "message": {"content": list(blocks)}}


def tool(name, **inp):
    return {"type": "tool_use", "name": name, "input": inp}


class RoutingCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = probe.load_cases()
        cls.cases = cls.suite["cases"]
        cls.entries = probe.entry_names()

    def test_ids_unique_and_expected_routes_exist(self):
        ids = [c["id"] for c in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        valid = self.entries | {probe.NONE}
        for case in self.cases:
            self.assertIn(case["expected"], case["acceptable"], case["id"])
            self.assertLessEqual(set(case["acceptable"]), valid, case["id"])
            self.assertLessEqual(set(case.get("confusable_with", [])), valid, case["id"])

    def test_prompts_do_not_name_the_route(self):
        for case in self.cases:
            if case.get("names_product"):
                continue
            prompt = case["prompt"].lower()
            self.assertNotIn("combo", prompt, case["id"])
            self.assertNotIn("skill", prompt, case["id"])

    def test_every_direct_entry_has_a_positive_case_and_negatives_exist(self):
        positives = {c["expected"] for c in self.cases if c["kind"] == "positive"}
        direct = self.entries - {"combo"}
        self.assertEqual(direct - positives, set())
        negatives = [c for c in self.cases if c["kind"] == "negative"]
        self.assertGreaterEqual(len(negatives), 5)
        self.assertTrue(all(probe.NONE in c["acceptable"] for c in negatives))

    def test_audit_confusable_pairs_are_covered(self):
        pairs = {(c["expected"], other) for c in self.cases for other in c.get("confusable_with", [])}
        for pair in (("combo-investigate", "combo-research"), ("combo-review", "combo-verify"),
                     ("combo-deliver", "combo-plan")):
            self.assertIn(pair, pairs)

    def test_thai_and_english_both_present(self):
        thai = [c for c in self.cases if any("฀" <= ch <= "๿" for ch in c["prompt"])]
        self.assertGreaterEqual(len(thai), 4)
        self.assertLess(len(thai), len(self.cases))


class RoutingAnalysis(unittest.TestCase):
    def test_first_skill_wins_and_earlier_tools_are_recorded(self):
        events = [
            assistant(tool("Glob", pattern="*")),
            assistant(tool("Skill", skill="combo-review"), tool("Skill", skill="combo-verify")),
            {"type": "result", "subtype": "success", "result": "done", "total_cost_usd": 0.5},
        ]
        got = probe.analyze_events(events)
        self.assertEqual(got["routed"], "combo-review")
        self.assertEqual(got["tools_before_skill"], ["Glob"])
        self.assertEqual(got["cost_usd"], 0.5)

    def test_no_skill_call_routes_to_none(self):
        events = [assistant({"type": "text", "text": "409 means conflict."}),
                  {"type": "result", "subtype": "success", "result": "409 means conflict."}]
        got = probe.analyze_events(events)
        self.assertEqual(got["routed"], probe.NONE)
        self.assertTrue(probe.score({"acceptable": ["none"]}, got))

    def test_score_uses_acceptable_list(self):
        case = {"acceptable": ["combo-investigate", "combo-research"]}
        self.assertTrue(probe.score(case, {"routed": "combo-research"}))
        self.assertFalse(probe.score(case, {"routed": "combo-review"}))
        self.assertFalse(probe.score(case, {"routed": "none"}))

    def test_non_combo_skill_counts_as_that_skill(self):
        events = [assistant(tool("Skill", skill="anthropic-skills:docx"))]
        self.assertEqual(probe.analyze_events(events)["routed"], "anthropic-skills:docx")

    def test_description_only_arm_disables_claude_md_and_policy_arm_does_not(self):
        self.assertEqual(probe.ARMS["description-only"], {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"})
        self.assertEqual(probe.ARMS["policy"], {})


if __name__ == "__main__":
    unittest.main()
