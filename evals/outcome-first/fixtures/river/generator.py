"""Legacy prototype: connected-looking water, poor junction and no route protection."""
import json
import math
import random
import sys
from pathlib import Path

N = 96

def generate(seed):
    rng = random.Random(seed)
    phase = rng.uniform(0, 6.28)
    water = []
    for y in range(N):
        main = 49 + 3 * math.sin(y / 14 + phase)
        for x in range(N):
            # Two disconnected, straight-ish strokes; main never widens.
            tributary = 9 + y * 0.78
            if abs(x - main) <= 2 or (y < 43 and abs(x - tributary) <= 1):
                water.append([x, y])
    return {"size": N, "seed": seed, "water": water}

if __name__ == "__main__":
    seed = int(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(generate(seed)), encoding="utf-8")
