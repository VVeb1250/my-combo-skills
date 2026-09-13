"""Independent acceptance for the Thai delivery fixture."""

import os
import sys
import unittest
from pathlib import Path


fixture_root = Path(os.environ["COMBO_EVAL_ROOT"])
sys.path.insert(0, str(fixture_root / "src"))

from inventory import Item, inventory_summary  # noqa: E402


class ThaiDeliveryAcceptance(unittest.TestCase):
    def test_default_excludes_discontinued_items(self):
        self.assertEqual(
            inventory_summary([Item("active", 2), Item("old", 3, discontinued=True)]),
            {"count": 1, "units": 2},
        )

    def test_flag_includes_positive_discontinued_items(self):
        self.assertEqual(
            inventory_summary(iter([Item("active", 2), Item("old", 3, discontinued=True)]), include_discontinued=True),
            {"count": 2, "units": 5},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
