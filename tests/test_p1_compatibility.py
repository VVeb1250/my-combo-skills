"""Static regression guards for P1 compatibility (not a model-behavior test)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class P1Compatibility(unittest.TestCase):
    def test_host_routers_avoid_duplicate_context_read(self):
        for path in (
            "skills/combo/SKILL.md",
            "adapters/claude/overrides/combo/SKILL.md",
        ):
            with self.subTest(path=path):
                body = source(path)
                self.assertIn("already embeds the shared context core", body)
                self.assertIn("do not load it a second time", body)
                self.assertNotIn("Read the chosen workflow and its [context practice]", body)
        self.assertIn("embeds the shared context core", source("POLICY.md"))
        self.assertIn("embeds the shared context core", source("adapters/claude/POLICY.md"))

    def test_stuck_recovery_requires_new_evidence(self):
        deliver = source("skills/combo/workflows/deliver.md")
        debug = source("skills/combo/workflows/debug.md")
        self.assertIn("two meaningful repairs", deliver)
        self.assertIn("stop speculative retries", deliver)
        self.assertIn("discriminating observation", deliver)
        self.assertIn("[debug](debug.md)", deliver)
        self.assertIn("not a mandatory new log file", deliver)
        self.assertIn("what new evidence will distinguish", debug)
        self.assertIn("structured logs over broad verbose logs", debug)

    def test_project_ecosystem_is_opt_in_across_workflows(self):
        for path in (
            "skills/combo/workflows/media.md",
            "skills/combo/workflows/verify.md",
            "skills/combo/workflows/investigate.md",
        ):
            with self.subTest(path=path):
                body = source(path)
                self.assertIn("Where `.combo/` already exists", body)
                self.assertIn("project-ecosystem.md", body)
        self.assertIn("not as proof", source("skills/combo/workflows/verify.md").replace("not proof", "not as proof"))
        self.assertIn("Do not scaffold", source("skills/combo/workflows/media.md"))

    def test_positive_retro_needs_evidence_and_verified_transfer(self):
        practice = source("skills/combo/practices/project-ecosystem.md")
        template = source(".combo/retro/TEMPLATE.md")
        self.assertIn("verified unusually effective approaches", practice)
        self.assertIn("Routine completion does not", practice)
        self.assertIn("Cross-model transfer remains candidate", practice)
        self.assertIn("comparable baseline", template)
        self.assertIn("Cross-model reuse stays candidate", template)


if __name__ == "__main__":
    unittest.main()
