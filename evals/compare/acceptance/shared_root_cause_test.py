"""Independent contract: the cent conversion is right for every caller."""

import os
import sys
import unittest
from pathlib import Path

fixture_root = Path(os.environ["COMBO_EVAL_ROOT"])
sys.path.insert(0, str(fixture_root / "src"))

from cart import cart_total_cents  # noqa: E402
from invoice import line_total_cents  # noqa: E402


class SharedRootCause(unittest.TestCase):
    def test_cart_counts_19_99_as_1999_cents(self):
        self.assertEqual(cart_total_cents([19.99]), 1999)

    def test_invoice_line_for_the_same_price_is_also_correct(self):
        self.assertEqual(line_total_cents(19.99, 2), 3998)

    def test_other_awkward_prices(self):
        self.assertEqual(cart_total_cents([0.29, 1.15]), 144)
        self.assertEqual(line_total_cents(4.35, 3), 1305)


if __name__ == "__main__":
    unittest.main(verbosity=2)
