"""Phase 3A: do agents recover through a project state file after a Codex compaction? No model calls.

    py -I state_file_reads.py

Counts tool calls in the 10 calls after each compaction (post) and the next 10 (control) whose text names a
project state file (STATUS.md, HANDOFF, PROGRESS, docs/*plan|status|roadmap, NOTES.md, CHECKPOINT, TODO).
Aggregates only. The regex also matches writes and unrelated TODO mentions, so read it as an upper bound.
"""
import glob, json, re
from pathlib import Path

STATE = re.compile(r"STATUS\.md|HANDOFF|HANDOVER|\bTODO\b|PROGRESS|docs[\/]+[\w.-]*(?:plan|status|roadmap)|\bNOTES?\.md|CHECKPOINT", re.I)


def main():
    tot = {"post": [0, 0], "control": [0, 0]}
    rollouts = with_state = 0
    for f in glob.glob(str(Path.home() / ".codex/sessions/**/rollout-*.jsonl"), recursive=True):
        calls, cuts = [], []
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            p = o.get("payload") or {}
            if o.get("type") == "compacted":
                cuts.append(len(calls))
            elif o.get("type") == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
                x = p.get("input") if isinstance(p.get("input"), str) else json.dumps(p.get("arguments", ""))
                calls.append(x)
        if not cuts:
            continue
        rollouts += 1
        with_state += any(STATE.search(c) for c in calls)
        for i, st in enumerate(cuts):
            end = cuts[i + 1] if i + 1 < len(cuts) else len(calls)
            for lo, hi, key in ((0, 10, "post"), (10, 20, "control")):
                seg = calls[st + lo:min(st + hi, end)]
                tot[key][0] += len(seg)
                tot[key][1] += sum(bool(STATE.search(c)) for c in seg)
    print(f"rollouts with compaction {rollouts}; touching a state file at any point {with_state}")
    for k, (n, s) in tot.items():
        print(f"{k:8s} calls {n:4d}  state-file calls {s:3d} ({s / max(n, 1):.1%})")


if __name__ == "__main__":
    main()
