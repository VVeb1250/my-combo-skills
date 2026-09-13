import unittest

from inventory import Item, inventory_summary


class InventoryTests(unittest.TestCase):
    def test_default_summary_excludes_discontinued(self):
        items = [Item("A", 2), Item("B", 3, discontinued=True)]
        self.assertEqual(inventory_summary(items), {"count": 1, "units": 2})


if __name__ == "__main__":
    unittest.main()
