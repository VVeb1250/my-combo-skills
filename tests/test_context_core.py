import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_core", ROOT / "scripts" / "sync-context-core.py")
assert SPEC is not None and SPEC.loader is not None
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


class ContextCore(unittest.TestCase):
    def test_every_workflow_carries_the_current_core_block_and_a_context_pointer(self):
        block = core.core_block()
        for path in sorted(core.WORKFLOWS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count(core.BEGIN), 1, path.name)
            self.assertTrue(text.endswith(block), path.name)
            self.assertIn("practices/context.md", text, path.name)
            self.assertNotRegex(text, r"Read \[context\]\(\.\./practices/context\.md\) once", path.name)

    def test_links_inside_the_block_resolve_from_the_workflows_folder(self):
        for target in re.findall(r"\]\(([^)#]+)\)", core.core_block()):
            if target.startswith(("http", "mailto")):
                continue
            self.assertTrue((core.WORKFLOWS / target).resolve().is_file(), target)

    def test_core_block_holds_the_three_invariant_sections_only(self):
        block = core.core_block()
        for name in core.CORE:
            self.assertIn(f"### {name}", block)
        self.assertNotIn("### Select evidence", block)
        self.assertNotIn("### Output and continuation", block)

    def test_render_is_idempotent_and_replaces_a_stale_block(self):
        block = core.core_block()
        sample = ("# W\n\nIntro. Read [context](../practices/context.md) once for\nevidence selection and reporting.\n\n1. step\n")
        once = core.render(sample, block)
        self.assertEqual(core.render(once, block), once)
        stale = once.replace("Own the outcome", "Own the OLD outcome", 1)
        self.assertEqual(core.render(stale, block), once)
        self.assertEqual(len(re.findall(re.escape(core.BEGIN), once)), 1)

    def test_check_mode_reports_a_stale_workflow(self):
        original = core.WORKFLOWS
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            (fake / "x.md").write_text("# X\n\nRead [context](../practices/context.md) once for evidence selection and reporting.\n", encoding="utf-8")
            setattr(core, "WORKFLOWS", fake)
            try:
                self.assertEqual(core.main(["--check"]), 1)
                self.assertEqual(core.main([]), 0)
                self.assertEqual(core.main(["--check"]), 0)
            finally:
                setattr(core, "WORKFLOWS", original)


if __name__ == "__main__":
    unittest.main()
