"""Navigation-first acceptance at the compiler boundary."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

spec = importlib.util.spec_from_file_location("kb", Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py")
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)


class NavigationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.base = self.root / ".combo"
        self.base.mkdir()

    def put(self, path, content):
        target = self.base / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_navigation_and_legacy_cross_domain(self):
        self.put("areas/terrain.md", '+++\nid="area.terrain"\narea="terrain"\nsummary="Rivers and terrain"\n+++\n# Terrain')
        self.put("knowledge/junction.md", '+++\nid="knowledge.junction"\ndomains=["terrain","simulation"]\nsummary="Connect river branches"\nstatus="candidate"\n+++\n# Junction')
        self.put("knowledge/junction/details.md", "# Deep details")
        self.put("specs/river.md", '---\nid: spec.river\narea: terrain\nstatus: accepted\n---\n# River')
        self.put("retro/old.md", '---\nid: old\narea: terrain\nstatus: candidate\n---\n# Old lesson')
        data = kb.rebuild(self.root)
        self.assertEqual(data["schema"], 4)
        self.assertEqual(len(data["entries"]), 4)
        top = (self.base/"INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Rivers and terrain", top)
        for domain in ("terrain", "simulation"):
            shelf = (self.base/"areas"/domain/"INDEX.md").read_text(encoding="utf-8")
            self.assertIn("../../knowledge/junction.md", shelf)
            self.assertIn("Connect river branches", shelf)
            self.assertIn("candidate", shelf)
        shelf = (self.base/"areas/terrain/INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Accepted specs", shelf)
        self.assertIn("../../retro/old.md", shelf)
        self.assertNotIn("Deep details", shelf)
        self.assertEqual(data, kb.rebuild(self.root))
        self.assertEqual(data, kb.load_index(self.root))
        self.assertEqual(kb.lookup(data, area="simulation")[0]["id"], "knowledge.junction")
        self.assertEqual(len(kb.route(data)["areas"]), 2)

    def test_generated_drift_and_handwritten_protection(self):
        self.put("specs/river.md", "# River")
        kb.rebuild(self.root)
        top = self.base/"INDEX.md"
        top.write_text(kb.GENERATED+"\nmodified", encoding="utf-8")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "generated view differs"):
            kb.load_index(self.root)
        kb.rebuild(self.root)
        top.write_text("# Handwritten", encoding="utf-8")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "handwritten"):
            kb.rebuild(self.root)
        self.assertEqual(top.read_text(encoding="utf-8"), "# Handwritten")

    def test_detail_marker_and_missing_evidence(self):
        self.put("specs/detail.md", "+++\nrecord=false\n+++\n# Not a record")
        self.put("knowledge/a.md", '+++\nid="a"\ndomains=["terrain"]\nsummary="A"\nstatus="tested"\n+++\n# A')
        with self.assertRaisesRegex(kb.IndexErrorInfo, "requires local evidence"):
            kb.rebuild(self.root)
        self.assertEqual(len(kb.collect(self.root)), 1)

    def test_remove_obsolete_generated_view(self):
        p = self.put("knowledge/a.md", '+++\nid="a"\ndomains=["terrain"]\nsummary="A"\n+++\n# A')
        kb.rebuild(self.root)
        p.unlink()
        kb.rebuild(self.root)
        self.assertFalse((self.base/"areas/terrain/INDEX.md").exists())

    def test_project_contract_and_direct_verification_link(self):
        tool = self.root / "verify.py"
        tool.write_text("print('actual output')\n", encoding="utf-8")
        self.put("specs/project.md", '+++\nid="spec.global"\ndomains=["project"]\nsummary="Preserve data"\nstatus="accepted"\n+++\n# Global')
        self.put("areas/terrain.md", '+++\nid="area.terrain"\narea="terrain"\nsummary="Terrain"\nverify=["verify.py"]\n+++\n# Terrain')
        data = kb.rebuild(self.root)
        self.assertIn("Project-wide contracts", (self.base/"INDEX.md").read_text(encoding="utf-8"))
        self.assertEqual(kb.route(data, area=["terrain"])["required"][0]["id"], "spec.global")
        shelf = (self.base/"areas/terrain/INDEX.md").read_text(encoding="utf-8")
        self.assertIn("../../../verify.py", shelf)
        tool.unlink()
        with self.assertRaisesRegex(kb.IndexErrorInfo, "missing verification entrypoint"):
            kb.rebuild(self.root)

    def test_legacy_domain_labels_portable_and_distinct(self):
        self.put("retro/a.md", '+++\nid="a"\narea="Terrain Generation"\n+++\n# A')
        self.put("retro/b.md", '+++\nid="b"\narea="terrain-generation"\n+++\n# B')
        self.put("retro/c.md", '+++\nid="c"\narea="CON"\n+++\n# C')
        self.put("retro/d.md", '+++\nid="d"\narea="../outside"\n+++\n# D')
        data = kb.rebuild(self.root)
        self.assertEqual(len(data["areas"]), 4)
        import re
        for link in re.findall(r'\]\(([^)]+)\)', (self.base/"INDEX.md").read_text(encoding="utf-8")):
            target = (self.base/unquote(link)).resolve()
            self.assertTrue(target.is_relative_to(self.base))
            self.assertTrue(target.is_file())
        self.assertEqual(len(list((self.base/"areas").glob("*/INDEX.md"))), 4)

    def test_migrate_one_record_without_duplicate_id(self):
        legacy = self.put("retro/lesson.md", '---\nid: old.lesson\narea: terrain\nstatus: candidate\n---\n# Lesson')
        kb.rebuild(self.root)
        self.put("knowledge/lesson.md", '+++\nid="old.lesson"\ndomains=["terrain"]\nsummary="A reusable lesson"\nstatus="candidate"\n+++\n# Lesson')
        with self.assertRaisesRegex(kb.IndexErrorInfo, "duplicate id"):
            kb.rebuild(self.root)
        legacy.unlink()
        self.assertEqual(kb.rebuild(self.root)["entries"][0]["id"], "old.lesson")


if __name__ == "__main__":
    unittest.main()
