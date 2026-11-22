import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js is required")
class CuratedValidatorTests(unittest.TestCase):
    def validate(self, adapters):
        with tempfile.TemporaryDirectory(prefix="combo-curated-") as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/validate-curated.cjs", root / "scripts")
            skill = root / "skills/combo"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                '---\n{"name":"combo","description":"test"}\n---\nBody\n', encoding="utf-8"
            )
            (skill / "agents/openai.yaml").write_text(
                '{"policy":{"allow_implicit_invocation":true}}', encoding="utf-8"
            )
            (root / "POLICY.md").write_text("Policy\n", encoding="utf-8")
            (root / "install-manifest.json").write_text(json.dumps({
                "version": 2, "source_roots": ["skills/combo"], "adapter_files": adapters,
            }), encoding="utf-8")
            appdata = root / "appdata"
            yaml = appdata / "npm/node_modules/promptfoo/node_modules/js-yaml"
            yaml.mkdir(parents=True)
            (yaml / "index.js").write_text("exports.load = JSON.parse;\n", encoding="utf-8")
            result = subprocess.run(
                ["node", str(root / "scripts/validate-curated.cjs")],
                env={**os.environ, "APPDATA": str(appdata)}, capture_output=True, text=True,
                check=False,
            )
            return result.returncode, json.loads(result.stdout)["errors"]

    def test_current_subcombo_targets_are_accepted(self):
        adapters = [{"source": f"adapters/codex/subcombo-{role}.toml",
                     "target": f"agents/subcombo-{role}.toml"}
                    for role in ("research", "implement", "verify")]
        self.assertEqual(self.validate(adapters), (0, []))

    def test_legacy_target_is_accepted(self):
        self.assertEqual(self.validate([{"source": "adapters/codex/combo-worker.toml",
                                         "target": "agents/combo-worker.toml"}]), (0, []))

    def test_unknown_duplicate_and_unsafe_adapters_are_rejected(self):
        valid = {"source": "adapters/codex/subcombo-verify.toml", "target": "agents/subcombo-verify.toml"}
        for adapters in ([valid, valid], [{**valid, "target": "agents/other.toml"}],
                         [{**valid, "source": "../secret"}]):
            with self.subTest(adapters=adapters):
                code, errors = self.validate(adapters)
                self.assertNotEqual(code, 0)
                self.assertTrue(errors)
