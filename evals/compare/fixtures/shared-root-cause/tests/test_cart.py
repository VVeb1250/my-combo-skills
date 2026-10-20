import unittest

from cart import cart_total_cents


class CartTests(unittest.TestCase):
    def test_whole_prices(self):
        self.assertEqual(cart_total_cents([2.0, 3.0]), 500)


if __name__ == "__main__":
    unittest.main()
