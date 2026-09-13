import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("full_library", ROOT / "scripts/build-full-library.py")
assert SPEC is not None and SPEC.loader is not None
library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(library)


class LibraryChecks(unittest.TestCase):
    def test_skill_filename_does_not_classify_everything_as_agents(self):
        self.assertEqual(library.engineering_group({"source": "skills/accessibility/SKILL.md"}), "architecture-quality")
        self.assertEqual(library.engineering_group({"source": "skills/agent-eval/SKILL.md"}), "agents-integration")
        self.assertEqual(library.engineering_group({"source": "skills/clickhouse-io/SKILL.md"}), "data-ml")

    def test_build_cannot_delete_an_arbitrary_output(self):
        with tempfile.TemporaryDirectory(prefix="combo-library-boundary-") as directory:
            target = Path(directory)
            sentinel = target / "user.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            with patch.object(library, "OUTPUT", target), self.assertRaises(ValueError):
                library.clean_generated_output()
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")

    def test_check_detects_modified_reference_bytes(self):
        with tempfile.TemporaryDirectory(prefix="combo-library-drift-") as directory:
            target = Path(directory)
            (target / "REFERENCE.md").write_text("changed", encoding="utf-8")
            manifest = target / "manifest.json"
            manifest.write_text(json.dumps({"counts": {"stable_entrypoints": 330}, "entries": [],
                "file_hashes": {"REFERENCE.md": "0" * 64}}), encoding="utf-8")
            output = io.StringIO()
            with patch.object(library, "OUTPUT", target), patch.object(library, "MANIFEST_PATH", manifest), \
                    patch.object(library, "git_head", return_value="pinned"), contextlib.redirect_stdout(output):
                self.assertEqual(library.check(), 1)
            self.assertIn("contents drifted", output.getvalue())


if __name__ == "__main__":
    unittest.main()
