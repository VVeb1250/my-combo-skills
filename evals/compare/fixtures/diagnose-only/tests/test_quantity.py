import unittest

from quantity import normalize_quantity


class QuantityTests(unittest.TestCase):
    def test_missing_quantity_uses_default(self):
        self.assertEqual(normalize_quantity(None), 1)

    def test_positive_quantity_is_preserved(self):
        self.assertEqual(normalize_quantity(4), 4)


if __name__ == "__main__":
    unittest.main()
