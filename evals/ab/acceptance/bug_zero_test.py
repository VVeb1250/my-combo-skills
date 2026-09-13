"""Independent post-task contract for the seeded quantity bug."""

import os
import sys
import unittest
from pathlib import Path


fixture_root = Path(os.environ["COMBO_EVAL_ROOT"])
sys.path.insert(0, str(fixture_root / "src"))

from quantity import normalize_quantity  # noqa: E402


class QuantityAcceptance(unittest.TestCase):
    def test_zero_is_a_real_value(self):
        self.assertEqual(normalize_quantity(0), 0)

    def test_none_uses_the_default(self):
        self.assertEqual(normalize_quantity(None), 1)

    def test_positive_values_are_unchanged(self):
        self.assertEqual(normalize_quantity(7), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
