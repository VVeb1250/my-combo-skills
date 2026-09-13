"""Independent behavioral acceptance, outside the model's copied fixture."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["COMBO_EVAL_ROOT"]) / "src"))
from catalog import select_labels
from filters import after_user_selection, initial_filters


class SelectionContract(unittest.TestCase):
    def test_initial_default_is_preserved(self):
        self.assertEqual(initial_filters(), ["new", "sale", "archived"])

    def test_clear_all_stays_empty(self):
        self.assertEqual(after_user_selection([]), [])

    def test_explicit_selection_and_input_are_preserved(self):
        labels = ["sale", "unknown", "new", "sale"]
        self.assertEqual(after_user_selection(labels), ["sale", "new", "sale"])
        self.assertEqual(labels, ["sale", "unknown", "new", "sale"])

    def test_iterators_and_empty_iterators(self):
        self.assertEqual(select_labels(iter(["new", "unknown"])), ["new"])
        self.assertEqual(select_labels(iter([])), [])


if __name__ == "__main__":
    unittest.main()
