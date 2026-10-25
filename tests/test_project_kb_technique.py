"""Schema-3 technique retrieval regression tests. Offline stdlib only."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py"
spec = importlib.util.spec_from_file_location("project_kb_phase_b", MODULE)
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)

def technique(id, signals=("floating canopy",), engine=("blender",), renderer=("eevee",),
              status="candidate", evidence=()):
    arr = lambda x: json.dumps(list(x))
    return (f'+++\nid = "{id}"\narea = "foliage"\nstatus = "{status}"\n'
            f'summary = "Stylized tree volume"\nproblem_signals = {arr(signals)}\n'
            f'engine = {arr(engine)}\nrenderer = {arr(renderer)}\n'
            f'evidence = {arr(evidence)}\n+++\n'
            '# Technique\n## Problem and decision rule\nCase\n## Mechanism\nReason\n'
            '## Applicability and constraints\nScope\n## Implementation\nSteps\n'
            '## Trade-offs and failure modes\nRisks\n## Verification\nCompare\n')

class TechniqueIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for sub in kb.KINDS:
            (self.root / ".combo" / sub).mkdir(parents=True, exist_ok=True)

    def write(self, name, content):
        path = self.root / ".combo" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_index_and_lookup(self):
        self.write("techniques/tree.md", technique("tech.tree"))
        index = kb.rebuild(self.root)
        self.assertEqual(index["schema"], 3)
        self.assertEqual(kb.lookup(index, kind="technique")[0]["id"], "tech.tree")

    def test_signal_query(self):
        self.write("techniques/tree.md", technique("tech.tree", signals=("thin silhouette",)))
        self.assertEqual(kb.route(kb.rebuild(self.root), query="thin silhouette")["suggested"][0]["id"], "tech.tree")

    def test_signal_ranking(self):
        self.write("techniques/a.md", technique("tech.generic", signals=("flat surface",)))
        self.write("techniques/b.md", technique("tech.specific", signals=("thin silhouette", "floating canopy")))
        ids = [r["id"] for r in kb.route(kb.rebuild(self.root), query="thin silhouette floating canopy")["suggested"]]
        self.assertEqual(ids[0], "tech.specific")

    def test_unknown_and_incompatible(self):
        self.write("techniques/godot.md", technique("tech.godot", engine=("godot",), renderer=("forward+",)))
        self.write("techniques/unknown.md", technique("tech.unknown", engine=("unknown",), renderer=("unknown",)))
        index = kb.rebuild(self.root)
        result = kb.route(index, query="floating canopy", engine="blender", renderer="eevee")
        self.assertEqual([r["id"] for r in result["suggested"]], ["tech.unknown"])
        self.assertEqual(result["suggested"][0]["compatibility"], "unknown")
        self.assertEqual(kb.lookup(index, ident="tech.godot", engine="blender")[0]["compatibility"], "incompatible")
        self.assertEqual(kb.lookup(index, ident="tech.godot", engine="godot")[0]["compatibility"], "metadata-match")

    def test_required_specs_not_truncated_or_filtered(self):
        for i in range(8):
            self.write(f"specs/r{i}.md", f'---\nid: spec.{i}\narea: foliage\nstatus: accepted\n---\n# Spec\n')
        self.write("techniques/godot.md", technique("tech.godot", engine=("godot",)))
        result = kb.route(kb.rebuild(self.root), area=["foliage"], engine="blender")
        self.assertEqual(len(result["required"]), 8)
        self.assertFalse(result["suggested"])

    def test_prototype_requires_local_evidence(self):
        self.write("techniques/tree.md", technique("tech.tree", status="project-tested", evidence=("docs/missing.json",)))
        with self.assertRaisesRegex(kb.IndexErrorInfo, "missing technique evidence"):
            kb.rebuild(self.root)
        path = self.root / "docs/missing.json"
        path.parent.mkdir()
        path.write_text('{"check": "pass"}', encoding="utf-8")
        self.assertEqual(kb.rebuild(self.root)["entries"][0]["status"], "project-tested")

    def test_remote_alone_cannot_certify(self):
        self.write("techniques/tree.md", technique("tech.tree", status="project-tested", evidence=("https://example.org",)))
        with self.assertRaisesRegex(kb.IndexErrorInfo, "requires local evidence"):
            kb.rebuild(self.root)

    def test_bad_status(self):
        self.write("techniques/tree.md", technique("tech.tree", status="impossible"))
        with self.assertRaisesRegex(kb.IndexErrorInfo, "unknown technique status"):
            kb.rebuild(self.root)

    def test_one_hop_remains_explicit(self):
        self.write("techniques/tree.md", technique("tech.tree"))
        self.write("retro/lesson.md", '+++\nid="retro.lesson"\narea="foliage"\n[[links]]\nrelation="related_to"\ntarget="tech.tree"\n+++\n# Retro\n')
        idx = kb.rebuild(self.root)
        self.assertEqual([r["id"] for r in kb.hop(idx, "tech.tree")["items"]], ["retro.lesson"])

    def test_index_migration_explicit(self):
        self.write("techniques/tree.md", technique("tech.tree"))
        idx = kb.rebuild(self.root)
        idx["schema"] = 2
        (self.root / ".combo/index.json").write_text(json.dumps(idx), encoding="utf-8")
        with self.assertRaisesRegex(kb.IndexErrorInfo, "unsupported"):
            kb.load_index(self.root)
        kb.rebuild(self.root)
        self.assertEqual(kb.load_index(self.root)["schema"], 3)

if __name__ == "__main__":
    unittest.main()
