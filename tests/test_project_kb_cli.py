"""CLI-level tests: documented commands must be invocable and produce correct output."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "skills/combo/tools/project_kb.py"


class ProjectKbCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOL), "--root", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def write(self, rel, text, newline="\n"):
        path = self.root / ".combo" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline=newline) as handle:
            handle.write(text)

    def fixture(self, newline="\n"):
        self.write("areas/commander.md", """+++
id = "area.commander"
area = "commander"
status = "accepted"
summary = "Commander owns squad orders"
paths = ["src/ai/**"]
+++
# Commander
""", newline)
        self.write("specs/target.md", """+++
id = "spec.target"
area = "commander"
status = "accepted"
summary = "No target oscillation"
+++
# Target
""", newline)
        self.write("retro/loop.md", """+++
id = "retro.loop"
area = "unit"
status = "tested"
summary = "Oscillation caused by state sync"
evidence = ["docs/run.json"]
[[links]]
relation = "related_to"
target = "spec.target"
+++
# Loop
""", newline)
        self.write("specs/old.md", """+++
id = "spec.old"
area = "commander"
status = "superseded"
summary = "Old targeting rules"
+++
# Old
""", newline)
        self.write("changes/archive/old.md", "# Archived\n", newline)

    def build(self, newline="\n"):
        self.assertEqual(self.cli("init").returncode, 0)
        self.fixture(newline)
        result = self.cli("index")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_init_writes_dirs_and_index_writes_cache(self):
        init = self.cli("init")
        self.assertEqual(init.returncode, 0, init.stderr)
        dirs = [p.name for p in (self.root / ".combo").iterdir() if p.is_dir()]
        self.assertEqual(len(dirs), 7)
        self.fixture()
        indexed = self.cli("index")
        self.assertEqual(indexed.returncode, 0, indexed.stderr)
        cache = self.root / ".combo" / "index.json"
        self.assertTrue(cache.is_file())
        data = json.loads(cache.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 2)
        self.assertEqual(len(data["entries"]), 4)
        checked = self.cli("check")
        self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_route_accepts_flag_and_positional_query_identically(self):
        self.build()
        flag = self.cli("route", "--path", "src/ai/commander/a.ts",
                        "--query", "target oscillation")
        positional = self.cli("route", "--path", "src/ai/commander/a.ts",
                              "target", "oscillation")
        self.assertEqual(flag.returncode, 0, flag.stderr)
        self.assertEqual(positional.returncode, 0, positional.stderr)
        self.assertEqual(json.loads(flag.stdout), json.loads(positional.stdout))
        result = json.loads(positional.stdout)
        self.assertIn("spec.target", [row["id"] for row in result["required"]])
        self.assertIn("retro.loop", [row["id"] for row in result["suggested"]])

    def test_route_rejects_both_query_forms(self):
        self.build()
        result = self.cli("route", "--query", "target", "oscillation")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not both", result.stderr)

    def test_lookup_by_flag_and_positional_id(self):
        self.build()
        flag = self.cli("lookup", "--id", "spec.target")
        positional = self.cli("lookup", "spec.target")
        self.assertEqual(flag.returncode, 0, flag.stderr)
        self.assertEqual(positional.returncode, 0, positional.stderr)
        self.assertEqual([row["id"] for row in json.loads(flag.stdout)], ["spec.target"])
        self.assertEqual(json.loads(flag.stdout), json.loads(positional.stdout))
        missing = self.cli("lookup", "spec.missing")
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertEqual(json.loads(missing.stdout), [])

    def test_lookup_rejects_both_id_forms(self):
        self.build()
        result = self.cli("lookup", "--id", "spec.target", "spec.target")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not both", result.stderr)

    def test_stale_error_names_the_changed_file(self):
        self.build()
        spec = self.root / ".combo" / "specs" / "target.md"
        spec.write_text(spec.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        result = self.cli("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("index_stale", result.stderr)
        self.assertIn("changed: .combo/specs/target.md", result.stderr)

    def test_stale_error_names_added_and_tampered_entries(self):
        self.build()
        write_added = self.root / ".combo" / "verification" / "new.md"
        write_added.write_text("---\nid: check.new\n---\n# New\n", encoding="utf-8")
        added = self.cli("check")
        self.assertEqual(added.returncode, 1)
        self.assertIn("added: .combo/verification/new.md", added.stderr)

        self.assertEqual(self.cli("index").returncode, 0)
        cache = self.root / ".combo" / "index.json"
        data = json.loads(cache.read_text(encoding="utf-8"))
        data["entries"][0]["status"] = "invented"
        cache.write_text(json.dumps(data), encoding="utf-8")
        tampered = self.cli("check")
        self.assertEqual(tampered.returncode, 1)
        self.assertIn("index record differs (tampered?)", tampered.stderr)

    def test_stale_error_names_removed_file(self):
        self.build()
        (self.root / ".combo" / "retro" / "loop.md").unlink()
        result = self.cli("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("removed: .combo/retro/loop.md", result.stderr)

    def test_crlf_records_work_through_the_cli(self):
        self.build(newline="\r\n")
        raw = (self.root / ".combo" / "specs" / "target.md").read_bytes()
        self.assertIn(b"\r\n", raw)
        checked = self.cli("check")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        routed = self.cli("route", "--path", "src/ai/commander/a.ts", "target oscillation")
        self.assertEqual(routed.returncode, 0, routed.stderr)
        self.assertIn("spec.target", [row["id"] for row in json.loads(routed.stdout)["required"]])

    def test_read_commands_do_not_scaffold_missing_combo(self):
        result = self.cli("route", "--query", "target")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing .combo/index.json", result.stderr)
        self.assertFalse((self.root / ".combo").exists())


if __name__ == "__main__":
    unittest.main()
