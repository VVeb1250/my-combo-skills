import json, tempfile, unittest
from pathlib import Path

import pilot


def rollout(events):
    d = Path(tempfile.mkdtemp()) / "r.jsonl"
    d.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
    return d


def call(i, text, out):
    return [{"type": "response_item", "payload": {"type": "custom_tool_call", "call_id": f"c{i}", "input": text}},
            {"type": "response_item", "payload": {"type": "custom_tool_call_output", "call_id": f"c{i}", "output": out}}]


class ScoreTest(unittest.TestCase):
    def test_mid_step2_cut_and_metrics(self):
        ev = []
        ev += call(1, "py -m unittest tests.test_money", "Ran 3\n\nOK\n")
        ev += call(2, "apply_patch *** Update File: shop/report.py", "ok")
        ev += call(3, "py -m unittest tests.test_report", "FAILED (failures=2)")
        ev += [{"type": "compacted", "payload": {}}]
        ev += call(4, "Get-Content STATUS.md", "x")
        ev += call(5, "apply_patch *** Update File: shop/money.py", "ok")
        ev += call(6, "apply_patch *** Update File: shop/fmt.py", "ok")
        ev += call(7, "py -m unittest tests.test_report", "Ran 2\n\nOK\n")
        r = pilot.score_rollout(*pilot.parse_rollout(rollout(ev)))
        self.assertTrue(r["cut_mid_step2"])
        self.assertTrue(r["failed_attempt_before_cut"])
        self.assertEqual(r["step1_files_edited_after_cut"], 1)
        self.assertEqual(r["readonly_calls_before_first_edit_after_cut"], 1)
        self.assertEqual(r["state_file_calls_after_cut"], 1)
        self.assertEqual(r["settings_json_edited_anywhere"], 0)

    def test_no_compaction(self):
        ev = call(1, "py -m unittest tests.test_money", "OK\n")
        r = pilot.score_rollout(*pilot.parse_rollout(rollout(ev)))
        self.assertEqual(r["compactions"], [])
        self.assertNotIn("cut_mid_step2", r)


if __name__ == "__main__":
    unittest.main()


class RegressionTest(unittest.TestCase):
    def test_json_escaped_output_is_read(self):
        c = {"text": "py -m unittest tests.test_money", "out": '{"output":"...\\r\\n---\\r\\nRan 3 tests\\r\\n\\r\\nOK\\r\\n"}'}
        self.assertEqual(pilot.test_result(c, "test_money"), "ok")
        c["out"] = '{"output":"FAILED (errors=1)\\r\\n"}'
        self.assertEqual(pilot.test_result(c, "test_money"), "fail")

    def test_second_compaction_can_be_the_critical_cut(self):
        ev = []
        ev += call(1, "Get-Content shop/money.py", "x")
        ev += [{"type": "compacted", "payload": {}}]
        ev += call(2, "py -m unittest tests.test_money", "Ran 3\n\nOK\n")
        ev += call(3, "apply_patch *** Update File: shop/fmt.py", "ok")
        ev += [{"type": "compacted", "payload": {}}]
        ev += call(4, "py -m unittest tests.test_report", "Ran 2\n\nOK\n")
        r = pilot.score_rollout(*pilot.parse_rollout(rollout(ev)))
        self.assertEqual(r["compactions"], [1, 3])
        self.assertTrue(r["cut_mid_step2"])
        self.assertEqual(r["post_cut_calls"], 1)
