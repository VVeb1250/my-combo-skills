"""Independent mechanical acceptance. Never grades aesthetics."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SEEDS = (17, 41, 83, 109, 151)
ROOT = Path(os.environ["COMBO_EVAL_ROOT"])
if not __debug__:
    raise RuntimeError("acceptance requires Python assertions enabled")

def check(data, seed):
    assert data["size"] == 96 and data["seed"] == seed
    raw = data["water"]
    assert all(isinstance(p, list) and len(p) == 2 and
               all(type(v) is int and 0 <= v < 96 for v in p) for p in raw)
    wet = {tuple(p) for p in raw}
    assert wet and len(wet) == len(raw), "empty or duplicate cells"
    assert all(x >= 6 for x,y in wet), "protected approach flooded"
    top = {x for x,y in wet if y == 0}
    bottom = {x for x,y in wet if y == 95}
    assert top & set(range(6,19)) and top & set(range(40,59)), "missing inlet"
    assert top <= set(range(6,19)) | set(range(40,59)), "unexpected inlet"
    assert bottom and bottom <= set(range(35,71)), "wrong outlet"
    assert not any(x == 95 for x,y in wet), "unexpected side outlet"
    seen = {next(iter(wet))}
    todo = list(seen)
    while todo:
        x,y = todo.pop()
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if p in wet and p not in seen:
                seen.add(p)
                todo.append(p)
    assert seen == wet, "disconnected water"
    def runs(row):
        xs = sorted(x for x,y in wet if y == row)
        return sum(i == 0 or x != xs[i-1] + 1 for i,x in enumerate(xs))
    assert runs(0) == 2 and runs(95) == 1, "wrong number of inlets/outlets"
    assert runs(31) == 2 and runs(64) == 1, "merge outside middle third"
    def average(rows):
        return sum(sum(y == r for x,y in wet) for r in rows) / len(rows)
    assert average(range(75,90)) >= average(range(5,20)) - 0.5, "downstream too narrow"
    # Main width above merge, measured only in its inlet neighborhood.
    upstream = sum(40 <= x <= 60 and 5 <= y < 20 for x,y in wet) / 15
    assert average(range(75,90)) >= upstream + 1, "main does not widen"
    return wet

def generate(seed, path):
    subprocess.run([sys.executable, str(ROOT/"generator.py"), str(seed), str(path)],
                   cwd=ROOT, check=True, timeout=8)
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    errors = []
    masks = []
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)/"result.json"
        for seed in SEEDS:
            try:
                first = generate(seed, path)
                mask = check(first, seed)
                assert first == generate(seed, path), "nondeterministic output"
                masks.append(mask)
            except (AssertionError, KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as exc:
                errors.append(f"seed {seed}: {exc}")
    if len(masks) == len(SEEDS) and min(len(a ^ b) for i,a in enumerate(masks) for b in masks[i+1:]) < 12:
        errors.append("seeds have insufficient distinct geometry")
    print("\n".join(errors) if errors else "PASS: topology, boundaries, route, width, determinism, minimum variation")
    return int(bool(errors))

if __name__ == "__main__":
    sys.exit(main())
