"""Authoring entry, invocation policy, and ownership regressions."""

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "routing_probe", ROOT / "scripts" / "run-routing-probe.py"
)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return match.group(1) if match else ""


class AuthoringEntryTests(unittest.TestCase):
    def test_codex_entry_is_explicit_only(self):
        policy = ROOT / "skills/combo-author/agents/openai.yaml"
        self.assertIn("allow_implicit_invocation: false", policy.read_text(encoding="utf-8"))
        self.assertNotIn("combo-author", probe.entry_names())

    def test_claude_override_is_explicit_only_and_user_invocable(self):
        values = frontmatter(
            ROOT / "adapters/claude/overrides/combo-author/SKILL.md"
        )
        self.assertIn("disable-model-invocation: true", values)
        self.assertIn("user-invocable: true", values)

    def test_both_manifests_own_the_authoring_package(self):
        for relative in (
            "install-manifest.json",
            "adapters/claude/install-manifest.json",
        ):
            manifest = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            sources = {
                entry["source"] if isinstance(entry, dict) else entry
                for entry in manifest["source_roots"]
            }
            self.assertIn("skills/combo-author", sources, relative)

    def test_authoring_entry_points_at_the_shared_practice(self):
        source = (ROOT / "skills/combo-author/SKILL.md").read_text(encoding="utf-8")
        override = (
            ROOT / "adapters/claude/overrides/combo-author/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("../combo/practices/authoring.md", source)
        self.assertIn("../combo/practices/authoring.md", override)
        self.assertTrue((ROOT / "skills/combo/practices/authoring.md").is_file())

    def test_templates_exist_and_are_linked_from_the_practice(self):
        practice = (
            ROOT / "skills/combo/practices/authoring.md"
        ).read_text(encoding="utf-8")
        for name in ("workflow", "practice", "entry", "host-adapter"):
            self.assertTrue(
                (ROOT / f"skills/combo/templates/{name}.md").is_file(), name
            )
            self.assertIn(f"(../templates/{name}.md)", practice, name)

    def test_both_hosts_share_the_maintenance_contract(self):
        contract = ROOT / "skills/combo/practices/maintenance.md"
        self.assertTrue(contract.is_file())
        body = contract.read_text(encoding="utf-8")
        self.assertIn("combo-author", body)
        self.assertIn("combo-maintain", body)
        for relative in (
            "skills/combo-maintain/SKILL.md",
            "adapters/claude/overrides/combo-maintain/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("../combo/practices/maintenance.md", text, relative)
            self.assertIn("observed", text.lower(), relative)

    def test_authoring_remains_explicit_only_and_keeps_maintenance_boundary(self):
        for relative in (
            "skills/combo-author/SKILL.md",
            "adapters/claude/overrides/combo-author/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("combo-maintain", text, relative)
        for relative in ("POLICY.md", "adapters/claude/POLICY.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("Structural authoring", text, relative)
            self.assertIn("observed-failure", text, relative)

    def test_maintain_does_not_hardcode_a_source_checkout(self):
        for relative in (
            "skills/combo-maintain/SKILL.md",
            "adapters/claude/overrides/combo-maintain/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("D:/0_person-project", text, relative)
            self.assertNotIn("D:\\0_person-project", text, relative)


if __name__ == "__main__":
    unittest.main()
