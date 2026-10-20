"""Immutable parameter/projection acceptance, not a 3D fidelity score."""

import json
import os
import unittest
from pathlib import Path

from PIL import Image, ImageChops


class HairAcceptance(unittest.TestCase):
    def test_reference_shape_and_locked_properties(self):
        root = Path(os.environ["COMBO_EVAL_ROOT"])
        model = json.loads((root / "hair.json").read_text())
        self.assertEqual(model["bangs"], [36, 58, 42, 65, 40])
        self.assertEqual(model["color"], "#ad94cf")
        self.assertEqual(model["pose"], "neutral")
        self.assertTrue(138 <= model["back_length"] <= 158)
        self.assertTrue(36 <= model["side_width"] <= 50)
        reference = Image.open(root / "reference.png").convert("RGB")
        matching = []
        for path in root.glob("*.png"):
            if path.name == "reference.png":
                continue
            with Image.open(path) as output:
                if (
                    output.size == reference.size
                    and ImageChops.difference(
                        output.convert("RGB"), reference
                    ).getbbox()
                    is None
                ):
                    matching.append(path)
        self.assertTrue(matching, "no delivered projection matches the reference")


if __name__ == "__main__":
    unittest.main()
