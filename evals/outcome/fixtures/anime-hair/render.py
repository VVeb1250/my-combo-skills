"""A 2D projection proxy for reference reasoning, NOT a Blender/3D renderer.

Parameters are pixels: back_length is distance below crown, side_width is the
side mass width. The front is intentionally already correct. Pillow is present
in the evaluation environment. Run python render.py [model.json] [output.png].
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def render(model, output):
    image = Image.new("RGB", (720, 300), "#f3f0f6")
    draw = ImageDraw.Draw(image)
    hair = model["color"]
    ink = "#342d43"
    for offset, label in ((0, "FRONT"), (240, "SIDE"), (480, "BACK")):
        x = offset + 120
        draw.text((offset + 95, 15), label, fill=ink)
        draw.ellipse((x - 46, 80, x + 46, 205), fill="#f1d3c0", outline=ink, width=2)
        draw.rectangle((x - 14, 190, x + 14, 240), fill="#f1d3c0")
        if label == "FRONT":
            points = [
                (x - 57, 163),
                (x - 61, 110),
                (x - 48, 65),
                (x, 48),
                (x + 48, 65),
                (x + 61, 110),
                (x + 57, 163),
            ]
            for i, length in reversed(list(enumerate(model["bangs"]))):
                points.extend([(x - 45 + i * 22, 78 + length), (x - 54 + i * 22, 88)])
            draw.polygon(points, fill=hair, outline=ink, width=3)
            draw.line((x - 29, 161, x - 15, 161), fill=ink, width=2)
            draw.line((x + 15, 161, x + 29, 161), fill=ink, width=2)
        elif label == "SIDE":
            width = model["side_width"]
            draw.polygon(
                [
                    (x - 38, 86),
                    (x - 16, 49),
                    (x + width, 75),
                    (x + width, 60 + model["back_length"]),
                    (x + 12, 78 + model["back_length"]),
                    (x + 8, 116),
                ],
                fill=hair,
                outline=ink,
                width=3,
            )
        else:
            length = model["back_length"]
            draw.polygon(
                [
                    (x - 58, 96),
                    (x - 35, 55),
                    (x, 47),
                    (x + 35, 55),
                    (x + 58, 96),
                    (x + 52, 60 + length),
                    (x + 20, 71 + length),
                    (x, 64 + length),
                    (x - 24, 74 + length),
                    (x - 52, 60 + length),
                ],
                fill=hair,
                outline=ink,
                width=3,
            )
    image.save(output)
    print(f"Saved projection proxy: {output}")


if __name__ == "__main__":
    render(
        json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "hair.json").read_text()),
        sys.argv[2] if len(sys.argv) > 2 else "preview.png",
    )
