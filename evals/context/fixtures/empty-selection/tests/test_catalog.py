import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from catalog import select_labels


class CatalogTests(unittest.TestCase):
    def test_initial_defaults(self):
        self.assertEqual(select_labels(), ["new", "sale", "archived"])

    def test_explicit_selection(self):
        self.assertEqual(select_labels(["sale", "unknown"]), ["sale"])


if __name__ == "__main__":
    unittest.main()
