"""Static guards for bounded architecture intervention guidance.

These verify instruction ownership and host-neutral references, not model
compliance or a measured improvement on real codebases.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRACTICES = ROOT / "skills/combo/practices"
WORKFLOWS = ROOT / "skills/combo/workflows"


def practice(name):
    return (PRACTICES / name).read_text(encoding="utf-8")


def workflow(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8").split(
        "<!-- BEGIN CONTEXT CORE", 1
    )[0]


class ArchitectureRecoveryGuidance(unittest.TestCase):
    def test_one_design_owner_and_three_interventions(self):
        design = practice("design.md")
        self.assertIn("## Choose the intervention from the cause", design)
        for term in ("**Repair:**", "**Refactor:**", "**Rework:**",
                     "accepted intent", "disproven domain model"):
            self.assertIn(term, design)
        self.assertIn("Repeated failed repairs alone", design)
        self.assertIn("Routine fixes need no new interview", design)

    def test_debug_uses_cause_not_failed_patch_count(self):
        debug = workflow("debug.md")
        self.assertIn("[design](../practices/design.md)", debug)
        self.assertIn("the two-repair threshold is only a fallback", debug)
        self.assertIn("not automatic", debug)
        self.assertIn("preserving **valid** caller", debug)

    def test_delivery_preserves_small_task_and_migration_paths(self):
        deliver = workflow("deliver.md")
        self.assertIn("tiny understood edit", deliver)
        self.assertIn("migrate all affected supported callers", deliver)
        self.assertIn("confirm whether", deliver)
        self.assertIn("remove obsolete duplicate APIs", deliver)

    def test_verification_uses_distinct_acceptance_oracles(self):
        tests = practice("tests.md")
        self.assertIn("**Repair:**", tests)
        self.assertIn("**Refactor:**", tests)
        self.assertIn("**Rework:**", tests)
        self.assertIn("Historical tests that encode a known defect", tests)
        self.assertIn("independently of the old implementation", tests)

    def test_review_checks_invalid_legacy_without_blind_deletion(self):
        review = workflow("review.md")
        simple = practice("simplicity.md")
        self.assertIn("selected intervention matches", review)
        self.assertIn("obsolete parallel path", review)
        self.assertIn("retirement condition", simple)
        self.assertIn("rather than deleting blindly", simple)

    def test_real_output_remains_required_for_emergent_reworks(self):
        evidence = practice("outcome-evidence.md")
        self.assertIn("real replacement route", evidence)
        self.assertIn("static validity alone cannot validate", evidence)


if __name__ == "__main__":
    unittest.main()
