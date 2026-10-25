"""Phase C: scoped global technique discovery without automatic traversal."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py"
spec = importlib.util.spec_from_file_location("project_kb_phase_c", MODULE)
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)

def doc(ident, *, signal="thin silhouette", status="candidate", links=""):
    return f"""+++
id = "{ident}"
area = "foliage"
status = "{status}"
summary = "Preserve stylized tree volume"
problem_signals = ["{signal}"]
engine = ["blender"]
renderer = ["eevee"]
{links}
+++
# Technique
## Problem and decision rule
Choose for flat foliage
## Mechanism
Preserve volume
## Applicability and constraints
Render-specific
## Implementation
Use masses
## Trade-offs and failure modes
Overdraw
## Verification
Compare renders
"""

class MultiScopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.project = self.root / "project"
        self.catalog = self.root / "catalog"
        (self.project / ".combo" / "techniques").mkdir(parents=True)
        (self.project / ".combo" / "specs").mkdir(parents=True)
        (self.catalog / "recipes").mkdir(parents=True)

    def add_local(self, name, content):
        (self.project / ".combo" / "techniques" / name).write_text(content, encoding="utf-8")

    def add_global(self, name, content):
        (self.catalog / "recipes" / name).write_text(content, encoding="utf-8")

    def indexes(self, *, external_ids=()):
        local = kb.rebuild(self.project, external_ids=external_ids)
        global_index = kb.rebuild(self.catalog, global_catalog=True)
        return local, global_index

    def test_global_fallback_without_local(self):
        self.add_global("hybrid.md", doc("tech.hybrid"))
        local, global_index = self.indexes()
        result = kb.scoped_route(local, global_index, query="thin silhouette",
                                 engine="blender", renderer="eevee")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["suggested"][0]["scoped_id"], "global:tech.hybrid")

    def test_local_suppresses_global(self):
        self.add_local("local.md", doc("tech.local"))
        self.add_global("global.md", doc("tech.global"))
        local, global_index = self.indexes()
        result = kb.scoped_route(local, global_index, query="thin silhouette")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["suggested"][0]["scoped_id"], "project:tech.local")

    def test_global_fallback_for_local_incompatible(self):
        self.add_local("local.md", doc("tech.local").replace('engine = ["blender"]', 'engine = ["godot"]'))
        self.add_global("global.md", doc("tech.global"))
        local, global_index = self.indexes()
        result = kb.scoped_route(local, global_index, query="thin silhouette", engine="blender")
        self.assertEqual(result["suggested"][0]["scoped_id"], "global:tech.global")

    def test_local_and_global_same_id_not_collide(self):
        self.add_local("local.md", doc("tech.hybrid", signal="local only"))
        self.add_global("global.md", doc("tech.hybrid", signal="thin silhouette"))
        local, global_index = self.indexes()
        result = kb.scoped_route(local, global_index, query="thin silhouette")
        self.assertEqual(result["suggested"][0]["scoped_id"], "global:tech.hybrid")
        self.assertEqual(kb.scoped_hop(local, global_index, "project:tech.hybrid")["total"], 0)

    def test_accepted_spec_kept(self):
        (self.project / ".combo" / "specs" / "contract.md").write_text(
            "---\nid: spec.foliage\narea: foliage\nstatus: accepted\n---\n# Requirement\n", encoding="utf-8")
        self.add_global("global.md", doc("tech.global"))
        local, global_index = self.indexes()
        result = kb.scoped_route(local, global_index, area=["foliage"], query="thin silhouette")
        self.assertEqual(result["required"][0]["scoped_id"], "project:spec.foliage")

    def test_global_index_staleness(self):
        self.add_global("global.md", doc("tech.global"))
        self.indexes()
        self.add_global("another.md", doc("tech.another"))
        with self.assertRaisesRegex(kb.IndexErrorInfo, "index_stale"):
            kb.load_index(self.catalog, global_catalog=True)

    def test_scoped_one_hop(self):
        self.add_local("local.md", doc("tech.local", links='[[links]]\nrelation = "related_to"\ntarget = "global:tech.global"'))
        self.add_global("global.md", doc("tech.global"))
        global_index = kb.rebuild(self.catalog, global_catalog=True)
        local = kb.rebuild(self.project, external_ids={"global:tech.global"})
        result = kb.scoped_hop(local, global_index, "project:tech.local")
        self.assertEqual(result["items"][0]["scoped_id"], "global:tech.global")
        self.assertEqual(result["total"], 1)

if __name__ == "__main__":
    unittest.main()
