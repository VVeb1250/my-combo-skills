import importlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
verify = importlib.import_module("verify_install")


class VerifyInstallTests(unittest.TestCase):
    def test_inventory_preserves_every_unrelated_record_and_derives_packages(self):
        before = [
            {"name": "browser", "path": "browser.md", "enabled": True, "description": "same"},
            {"name": "legacy", "path": "legacy.md", "enabled": False, "scope": "user"},
            {"name": "combo", "path": "combo.md", "enabled": False},
            {"name": "combo-deliver", "path": "deliver.md", "enabled": False},
        ]
        after = [
            {"name": "combo-deliver", "path": "deliver.md", "enabled": True},
            {"name": "browser", "path": "browser.md", "enabled": True, "description": "same"},
            {"name": "legacy", "path": "legacy.md", "enabled": False, "scope": "user"},
            {"name": "combo", "path": "combo.md", "enabled": True},
        ]
        result = verify.verify_inventory(before, after, {"combo", "combo-deliver"})
        self.assertEqual(result["live_packages"], ["combo", "combo-deliver"])
        self.assertEqual(result["active_combo"], ["combo", "combo-deliver"])

    def test_inventory_rejects_unrelated_record_change(self):
        before = [{"name": "native", "path": "native", "enabled": True, "description": "before"}]
        after = [{"name": "native", "path": "native", "enabled": True, "description": "after"}]
        with self.assertRaisesRegex(AssertionError, "Unrelated skill discovery changed"):
            verify.verify_inventory(before, after, {"combo"})


if __name__ == "__main__":
    unittest.main()
