"""Phase 3A offline: how much of real spend is the fixed prefix (system prompt, tool schemas, skill list, CLAUDE.md)? No model calls.

    py -I prefix_share.py [--exclude <session-uuid> ...]

Per transcript: P = context at the first call (input + cache write + cache read). The prefix is paid once as a cache
write ($4.00/Mtok for 1h, Sonnet 5.5 rates) and re-read on every later call at $0.10/Mtok. An upper bound, because P also
holds the first user message. Sonnet turns only, so rates are exact.
"""
import argparse, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ars", HERE / "audit_real_sessions.py")
ars = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ars)

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=str(Path.home() / ".claude/projects/D--0-person-project-my-combo-skills"))
ap.add_argument("--exclude", nargs="*", default=[])
a = ap.parse_args()
root, seen = Path(a.root), set()
rows = []
for p in sorted(root.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
    if p.stem in a.exclude:
        continue
    for f, kind in [(p, "main")] + [(s, "sub") for s in sorted((root / p.stem / "subagents").glob("*.jsonl"))]:
        turns, _ = ars.parse(f, seen)
        turns = [t for t in turns if t["model"] == "claude-sonnet-5-5"]
        if not turns:
            continue
        P = turns[0]["in"] + turns[0]["cw"] + turns[0]["cr"]
        total = sum(ars.usd(t["in"], "in") + ars.usd(t["cw1h"], "cw1h") + ars.usd(t["cw5m"], "cw5m") + ars.usd(t["cr"], "cr")
                    + ars.usd(t["out"], "out") for t in turns)
        reread = sum(ars.usd(min(P, t["cr"]), "cr") for t in turns[1:])
        write = ars.usd(P, "cw1h")
        rows.append((kind, p.stem[:8], len(turns), P, total, write, reread))
print("kind session  turns  prefix_tok  total$  prefix_write$  prefix_reread$  share")
for kind, s, n, P, total, w, r in rows:
    print(f"{kind:4s} {s} {n:5d} {P:10,d} {total:7.2f} {w:8.2f} {r:10.2f} {(w + r) / total:7.0%}")
for kind in ("main", "sub"):
    sel = [x for x in rows if x[0] == kind]
    if sel:
        t = sum(x[4] for x in sel); w = sum(x[5] for x in sel); r = sum(x[6] for x in sel)
        print(f"{kind}: total ${t:.2f}; prefix write ${w:.2f} + re-read ${r:.2f} = {(w + r) / t:.0%} of {kind} Sonnet spend; mean prefix {sum(x[3] for x in sel) // len(sel):,d} tok")
