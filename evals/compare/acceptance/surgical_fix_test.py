"""Independent contract: the bug is fixed and nothing else in the module moved."""

import ast
import os
import sys
import unittest
from pathlib import Path

root = Path(os.environ["COMBO_EVAL_ROOT"])
sys.path.insert(0, str(root / "src"))

from timefmt import format_duration  # noqa: E402

UNTOUCHED = {
    "format_size": '''def format_size(n):
    """Human readable size."""
    if n < 1024:
        return str(n) + " B"
    elif n < 1024 * 1024:
        return str(round(n / 1024, 1)) + " KB"
    else:
        return str(round(n / 1024 / 1024, 1)) + " MB"''',
    "clamp": '''def clamp(x, lo, hi):
    if x < lo: return lo
    elif x > hi: return hi
    else: return x''',
    "pad": '''def pad(s, width):
    return s + " " * (width - len(s)) if len(s) < width else s''',
}


class SurgicalFix(unittest.TestCase):
    def test_durations(self):
        for seconds, text in ((0, "0:00"), (59, "0:59"), (60, "1:00"), (119, "1:59"),
                              (3599, "59:59"), (3600, "60:00")):
            self.assertEqual(format_duration(seconds), text, seconds)

    def test_other_functions_are_untouched(self):
        source = (root / "src" / "timefmt.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = {n.name: ast.get_source_segment(source, n) for n in tree.body if isinstance(n, ast.FunctionDef)}
        for name, expected in UNTOUCHED.items():
            self.assertEqual(found.get(name), expected, f"{name} was modified")

    def test_unrelated_import_is_left_alone(self):
        self.assertIn("import math", (root / "src" / "timefmt.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
