"""Offline progressive-index tests; no external services or models."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py"
spec = importlib.util.spec_from_file_location("kb", MODULE)
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)


class ProjectKbV1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for directory in kb.KINDS:
            (self.root / ".combo" / directory).mkdir(parents=True)

    def write(self, path, text):
        p = self.root / ".combo" / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def fixture(self):
        self.write("areas/commander.md", "+++\nid='area.commander'\narea='commander'\nstatus='accepted'\nsummary='Commander owns squad orders'\npaths=['src/ai/commander/**']\n+++\n# Commander")
        self.write("specs/target.md", "+++\nid='spec.target'\narea='commander'\nstatus='accepted'\nsummary='No oscillation'\n+++\n# Target")
        self.write("decisions/ownership.md", "+++\nid='adr.state'\narea='commander'\nstatus='accepted'\n[[links]]\nrelation='constrained_by'\ntarget='spec.target'\n+++\n# State")
        self.write("retro/unit/loop.md", "+++\nid='retro.loop'\narea='unit'\nstatus='tested'\nsummary='Oscillation caused by state sync'\nevidence=['docs/run.json']\n[[links]]\nrelation='related_to'\ntarget='adr.state'\n+++\n# Loop")

    def test_rebuild_deterministic(self):
        self.fixture()
        kb.rebuild(self.root)
        original = (self.root / ".combo/index.json").read_bytes()
        kb.rebuild(self.root)
        self.assertEqual(original, (self.root / ".combo/index.json").read_bytes())

    def test_progressive_route_and_hops(self):
        self.fixture()
        index = kb.rebuild(self.root)
        result = kb.route(index, paths=["src/ai/commander/a.ts"])
        self.assertIn("spec.target", [r["id"] for r in result["required"]])
        self.assertNotIn("retro.loop", [r["id"] for r in result["suggested"]])
        self.assertIn("adr.state", [r["id"] for r in kb.hop(index, "commander")["items"]])
        self.assertIn("retro.loop", [r["id"] for r in kb.hop(index, "adr.state")["items"]])

    def test_index_stale_on_edit_and_tamper(self):
        self.fixture()
        kb.rebuild(self.root)
        self.write("specs/target.md", "+++\nid='spec.target'\narea='commander'\nstatus='accepted'\nsummary='Changed'\n+++\n# Changed")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "index_stale"):
            kb.load_index(self.root)
        kb.rebuild(self.root)
        p = self.root / ".combo/index.json"
        obj = json.loads(p.read_text())
        obj["entries"][0]["status"] = "invented"
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(kb.IndexErrorInfo, "index_stale"):
            kb.load_index(self.root)

    def test_broken_link_keeps_old_cache(self):
        self.fixture()
        kb.rebuild(self.root)
        original = (self.root / ".combo/index.json").read_bytes()
        self.write("decisions/bad.md", "+++\nid='bad'\n[[links]]\nrelation='related_to'\ntarget='missing'\n+++\n# Bad")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "broken"):
            kb.rebuild(self.root)
        self.assertEqual(original, (self.root / ".combo/index.json").read_bytes())

    def test_tested_requires_evidence(self):
        self.write("retro/bad.md", "---\nid: bad\nstatus: tested\n---\n# Bad")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "lacks evidence"):
            kb.rebuild(self.root)

    def test_duplicate_rejected(self):
        self.write("specs/a.md", "---\nid: dup\n---\n# A")
        self.write("retro/b.md", "---\nid: dup\n---\n# B")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "duplicate"):
            kb.rebuild(self.root)

    def test_legacy_metadata_and_archive(self):
        self.write("retro/ai/a.md", "---\nid: a\narea: ai\ntags: one, two\n---\n# A")
        self.write("changes/archive/old.md", "# Gone")
        records = kb.collect(self.root)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tags"], ["one", "two"])

    def test_bounded_pagination(self):
        self.fixture()
        index = kb.rebuild(self.root)
        first = kb.hop(index, "commander", limit=1)
        self.assertEqual(len(first["items"]), 1)
        self.assertGreaterEqual(first["total"], 3)

    def test_inactive_history_only(self):
        self.write("retro/old.md", "---\nid: old\nstatus: superseded\n---\n# Old")
        index = kb.rebuild(self.root)
        self.assertFalse(kb.lookup(index, include_inactive=False))
        self.assertTrue(kb.lookup(index, include_inactive=True))

    def test_reject_unsafe_glob(self):
        self.write("areas/bad.md", "+++\npaths=['../secrets']\n+++\n# Bad")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "unsafe"):
            kb.collect(self.root)


if __name__ == "__main__":
    unittest.main()
