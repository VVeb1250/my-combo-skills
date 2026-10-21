"""Phase 3A offline: which tool results cost the most to carry, and are they bounded? No model calls.

    py -I tool_output_offenders.py [--exclude <session-uuid> ...]

Reuses the transcript parser of audit_real_sessions.py. For every Bash/PowerShell call it takes the result size
(chars/4 [E]) and the carried cost (written once, re-read on every later call of the same transcript, Sonnet 5.5
rates), groups by command class, and reports the share of large results and whether the command looked bounded
(head/tail/-n/-First/-Last/-TotalCount/limit/--stat/-Tail/-Skip). Aggregates only; no command text is stored beyond
a coarse class label.
"""
import argparse, importlib.util, re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ars", HERE / "audit_real_sessions.py")
ars = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ars)

BOUND = re.compile(r"\b(head|tail)\b|\s-n\s*\d|\s-\d+\b|-First\s|-Last\s|-TotalCount|-Tail\s|--stat|--oneline|--max-count|\|\s*Select-Object\s+-(First|Last)|\blimit\b|--short|-short", re.I)
WRAP = re.compile(r"^(cd\s+\S+\s*(&&|;)\s*|rtk\s+|\$ErrorActionPreference\s*=\s*'?\w+'?;\s*)+", re.I)


def klass(cmd):
    c = WRAP.sub("", cmd.strip())
    parts = re.split(r"\s+", c)
    head = parts[0].lower() if parts else "?"
    if head in ("git", "npm", "npx", "cargo", "uv", "pip", "gh", "codex", "claude", "docker", "rtk") and len(parts) > 1:
        return f"{head} {parts[1].lower()}"
    return head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / ".claude/projects/D--0-person-project-my-combo-skills"))
    ap.add_argument("--exclude", nargs="*", default=[])
    a = ap.parse_args()
    root, seen = Path(a.root), set()
    files = []
    for p in sorted(root.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        if p.stem in a.exclude:
            continue
        files.append(p)
        sub = root / p.stem / "subagents"
        if sub.is_dir():
            files += sorted(sub.glob("*.jsonl"))
    rows = []  # (class, tokens, carried, bounded)
    for f in files:
        turns, results = ars.parse(f, seen)
        n = len(turns)
        for i, t in enumerate(turns):
            for u in t["tools"]:
                if u["name"] not in ("Bash", "PowerShell") or u["id"] not in results:
                    continue
                cmd = str(u["input"].get("command", ""))
                tok = results[u["id"]][1] / 4
                k = n - 1 - i
                carried = tok * (ars.RATE["cw1h"] + ars.RATE["cr"] * max(k - 1, 0)) / 1e6 if k > 0 else 0.0
                rows.append((klass(cmd), tok, carried, bool(BOUND.search(cmd))))
    tot_tok = sum(r[1] for r in rows)
    tot_car = sum(r[2] for r in rows)
    print(f"shell calls {len(rows)}; result tokens {tot_tok:,.0f} (mean {tot_tok / len(rows):,.0f}); carried ${tot_car:.2f}")
    for lo, hi in ((0, 500), (500, 2000), (2000, 5000), (5000, 10**9)):
        sel = [r for r in rows if lo <= r[1] < hi]
        print(f"  results {lo}-{hi if hi < 10**9 else 'inf'} tok: {len(sel):4d} calls ({len(sel) / len(rows):.0%}), carried ${sum(r[2] for r in sel):.2f} ({sum(r[2] for r in sel) / tot_car:.0%})")
    big = [r for r in rows if r[1] >= 2000]
    print(f"results >= 2000 tok: {len(big)} calls, carried ${sum(r[2] for r in big):.2f}; of those, command looked bounded: {sum(r[3] for r in big)}")
    agg = defaultdict(lambda: [0, 0.0, 0.0, 0])
    for c, tok, car, b in rows:
        x = agg[c]
        x[0] += 1; x[1] += tok; x[2] += car; x[3] += b
    print("\ntop command classes by carried cost: class, calls, mean tok, carried $, share, bounded calls")
    for c, (n, tok, car, b) in sorted(agg.items(), key=lambda kv: -kv[1][2])[:12]:
        print(f"  {c[:22]:22s} {n:4d} {tok / n:7.0f} {car:6.2f} {car / tot_car:5.0%} {b:4d}")


if __name__ == "__main__":
    main()
