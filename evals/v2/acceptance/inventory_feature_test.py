"""Independent acceptance for the iterable inventory feature."""

import os
import sys
import unittest
from pathlib import Path


fixture_root = Path(os.environ["COMBO_EVAL_ROOT"])
sys.path.insert(0, str(fixture_root / "src"))

from inventory import Item, inventory_summary  # noqa: E402


class InventoryFeatureAcceptance(unittest.TestCase):
    def setUp(self):
        self.items = [
            Item("active", 2),
            Item("discontinued", 3, discontinued=True),
            Item("empty", 0),
            Item("negative", -4),
        ]

    def test_default_preserves_existing_available_only_behavior(self):
        self.assertEqual(inventory_summary(iter(self.items)), {"count": 1, "units": 2})

    def test_flag_includes_positive_discontinued_items(self):
        self.assertEqual(
            inventory_summary((item for item in self.items), include_discontinued=True),
            {"count": 2, "units": 5},
        )

    def test_any_iterable_and_nonpositive_stock_are_handled(self):
        self.assertEqual(
            inventory_summary(iter([Item("x", 1, discontinued=True)]), include_discontinued=True),
            {"count": 1, "units": 1},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
