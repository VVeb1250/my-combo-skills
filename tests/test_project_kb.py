"""No-network tests for the optional project-local indexing helper."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py"
spec = importlib.util.spec_from_file_location("project_kb", MODULE)
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)


class ProjectKbTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in kb.KINDS:
            (self.root / ".combo" / name).mkdir(parents=True)

    def put(self, name, content):
        path = self.root / ".combo" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_index_metadata_and_excludes_archive(self):
        self.put("retro/ai/R001.md", "---\nid: R001\narea: commander\ntags: target, ai-unit\nstatus: tested\nevidence: docs/run.json\n---\n# Aim loop")
        self.put("changes/archive/old/proposal.md", "# Archived")
        rows = kb.collect(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "R001")
        self.assertEqual(rows[0]["tags"], ["target", "ai-unit"])

    def test_index_is_deterministic(self):
        self.put("specs/unit.md", "# Unit")
        self.assertEqual(kb.collect(self.root), kb.collect(self.root))

    def test_candidate_is_not_tested(self):
        self.put("shortcuts/quick.md", "---\nid: quick\nstatus: candidate\n---\n# Shortcut")
        self.assertEqual(kb.collect(self.root)[0]["status"], "candidate")


    def test_changed_source_path_routes_to_candidate_area_and_spec(self):
        self.put(
            "areas/combat.md",
            "+++\nid = \"area.combat\"\narea = \"combat\"\nstatus = \"accepted\"\n"
            "summary = \"Combat navigation\"\npaths = [\"src/combat/**\"]\n+++\n"
            "# Combat navigation\n",
        )
        self.put(
            "specs/ammo.md",
            "+++\nid = \"spec.ammo\"\narea = \"combat\"\nstatus = \"accepted\"\n"
            "summary = \"Ammo contract\"\npaths = [\"src/combat/weapon/**\"]\n+++\n"
            "# Ammo contract\n",
        )
        rows = kb.collect(self.root)
        index = kb._index_data(rows)
        match = kb.route(index, paths=["src/combat/weapon/state.js"])
        self.assertEqual(
            {item["id"] for item in match["required"]}, {"spec.ammo"}
        )
        self.assertIn("combat", {item["area"] for item in match["areas"]})
        self.assertFalse(kb.route(index, paths=["src/unrelated.js"])["required"])
        # A missing path match only warns; it does not certify doc freshness.
        self.assertIsNotNone(kb.route(index, paths=["src/unrelated.js"])["warning"])

    def test_index_staleness_is_only_markdown_freshness(self):
        self.put(
            "areas/combat.md",
            "+++\nid = \"area.combat\"\narea = \"combat\"\nstatus = \"accepted\"\n"
            "paths = [\"src/combat/**\"]\n+++\n# Combat\n",
        )
        kb.rebuild(self.root)
        # Editing arbitrary source outside .combo is not captured by index hashes.
        (self.root / "src").mkdir()
        (self.root / "src" / "combat.js").write_text("changed", encoding="utf-8")
        self.assertEqual(len(kb.load_index(self.root)["entries"]), 1)
        self.put(
            "areas/combat.md",
            "+++\nid = \"area.combat\"\narea = \"combat\"\nstatus = \"accepted\"\n"
            "paths = [\"src/combat/**\"]\n+++\n# Changed navigation\n",
        )
        with self.assertRaises(kb.IndexErrorInfo):
            kb.load_index(self.root)

if __name__ == "__main__":
    unittest.main()
