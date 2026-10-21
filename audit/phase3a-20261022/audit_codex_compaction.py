"""Phase 3A offline audit: what Codex does after a compaction. No model calls, aggregates only.

    py -I audit_codex_compaction.py [--root ~/.codex/sessions] [--window 10] [--out codex_compaction.json]

Streams every rollout-*.jsonl and, per rollout, finds `compacted` events (the host replacing history with
`replacement_history`). For the first WINDOW tool calls after each compaction it counts commands that were
already run before it (same normalised text) -- work re-done because the compaction dropped its result from
context -- plus reloads of project instructions. Command text and file names are never written out.

Codex tool calls are JavaScript snippets (`exec`), so a "command" is every `cmd:"..."` string inside one.
Two repeat counts are reported: `repeat_any` ignores edits (upper bound, a re-read after your own edit is
legitimate) and `repeat_no_edit` counts only repeats with no apply_patch/edit since the first run (lower
bound). Token fields come from `token_count` events; no price is attached because no rate for this host's
model exists in the repo.
"""
import argparse, glob, json, re
from collections import defaultdict
from pathlib import Path

CMD = re.compile(r'cmd\s*:\s*"((?:[^"\\]|\\.)*)"')
INSTR = re.compile(r"skills[\\/]+combo|CLAUDE\.md|AGENTS\.md|SKILL\.md", re.I)
EDIT = re.compile(r"apply_patch|Set-Content|Add-Content|Out-File|\*\*\* (?:Update|Add) File", re.I)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


PATH = re.compile(r"[\w./\:~-]+\.(?:md|py|json|tsx?|js|cs|html|css|txt|ps1|toml|ya?ml|gd|rs|cjs|mjs|csv)\b", re.I)
READ = re.compile(r"Get-Content|\bcat\b|\btype\b|\bsed\b|\bhead\b|\btail\b|\brg\b|Select-String|\bgrep\b", re.I)


def pnorm(x):
    return x.replace("\\", "/").lower().split("/")[-1]  # file name only: cwd differs per command


def analyse(path, window):
    """One pass collects calls and compactions; windows are computed afterwards.
    post window = calls 1..W after a compaction; control window = calls W+1..2W after the same compaction."""
    calls, comp_at, kept = [], [], []
    last_ctx, after_marker = 0, False
    for line in open(path, encoding="utf-8", errors="replace"):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        t, p = o.get("type"), o.get("payload") or {}
        if t == "compacted":
            comp_at.append(len(calls))
            rh = p.get("replacement_history") or []
            roles = [x.get("role") for x in rh if x.get("type") == "message"]
            kept.append({"user_msgs": roles.count("user"), "assistant_msgs": roles.count("assistant"),
                         "summary_msg_empty": not p.get("message"), "ctx_before": last_ctx})
            after_marker = True
        elif t == "event_msg" and p.get("type") == "token_count":
            lt = (p.get("info") or {}).get("last_token_usage") or {}
            last_ctx = lt.get("input_tokens", last_ctx)
            if after_marker and kept and lt.get("input_tokens"):
                kept[-1]["ctx_after_first_call"] = lt["input_tokens"]
                after_marker = False
        elif t == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
            text = p.get("input") if isinstance(p.get("input"), str) else p.get("arguments", "")
            text = text if isinstance(text, str) else json.dumps(text)
            cmds = [norm(c) for c in CMD.findall(text)] or [norm(text)[:400]]
            is_edit = bool(EDIT.search(text))
            paths = {pnorm(x) for x in PATH.findall(text)}
            calls.append({"cmds": cmds, "edit": is_edit, "paths": paths, "instr": bool(INSTR.search(text)),
                          "read": bool(READ.search(text)) and not is_edit})
    return calls, comp_at, kept


def window_stats(calls, comp_at, lo, hi):
    """Metrics over calls lo+1..hi after each compaction (stopping at the next compaction)."""
    n = rep_cmd = rep_path = instr = ro_before_edit_total = ro_n = 0
    for ci, start in enumerate(comp_at):
        end = comp_at[ci + 1] if ci + 1 < len(comp_at) else len(calls)
        seen_cmd, edited_since, read_before = {}, {}, {}
        for i, c in enumerate(calls[:start]):
            for x in c["cmds"]:
                seen_cmd[x] = i
            if c["edit"]:
                for q in c["paths"]:
                    edited_since[q] = i
            elif c["read"]:
                for q in c["paths"]:
                    read_before[q] = i
        for j in range(start + lo, min(start + hi, end)):
            c = calls[j]
            n += 1
            instr += c["instr"]
            rep_cmd += any(x in seen_cmd for x in c["cmds"])
            if c["read"] and any(q in read_before and edited_since.get(q, -1) < read_before[q] for q in c["paths"]):
                rep_path += 1
        # read-only calls before the first edit after this compaction (capped at 40)
        k = 0
        for j in range(start, min(end, start + 40)):
            if calls[j]["edit"]:
                break
            k += 1
        ro_before_edit_total += k
        ro_n += 1
    return {"calls": n, "repeat_cmd": rep_cmd, "reread_path_no_edit": rep_path, "instr": instr,
            "readonly_before_first_edit_mean": round(ro_before_edit_total / max(ro_n, 1), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / ".codex/sessions"))
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--out", default=str(Path(__file__).with_name("codex_compaction.json")))
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(str(Path(a.root) / "**/rollout-*.jsonl"), recursive=True)):
        calls, comp_at, kept = analyse(f, a.window)
        if not comp_at:
            continue
        W = a.window
        rows.append({"id": Path(f).stem.split("rollout-")[1][:19], "calls": len(calls), "compactions": len(comp_at),
                     "post": window_stats(calls, comp_at, 0, W), "control": window_stats(calls, comp_at, W, 2 * W),
                     "kept": kept, "edit_gap_mean": round(len(calls) / max(sum(c["edit"] for c in calls), 1), 1)})
    Path(a.out).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    agg = lambda w: {k: sum(r[w][k] for r in rows) for k in ("calls", "repeat_cmd", "reread_path_no_edit", "instr")}
    print(f"rollouts with compaction {len(rows)}; compactions {sum(r['compactions'] for r in rows)}; window={a.window}")
    for w in ("post", "control"):
        g = agg(w)
        print(f"{w:8s} calls {g['calls']:4d}  repeat_cmd {g['repeat_cmd']:3d}  reread_path_no_edit {g['reread_path_no_edit']:3d}  instr_reload {g['instr']:3d}"
              f"  ({g['instr'] / max(g['calls'], 1):.0%} instr, {g['reread_path_no_edit'] / max(g['calls'], 1):.0%} path re-reads)")
    ro = [r["post"]["readonly_before_first_edit_mean"] for r in rows]
    print("read-only calls before first edit after compaction, mean per rollout:", round(sum(ro) / len(ro), 1),
          "| mean calls per edit across the rollout:", round(sum(r["edit_gap_mean"] for r in rows) / len(rows), 1))
    k = [x for r in rows for x in r["kept"]]
    print(f"summary message empty in {sum(x['summary_msg_empty'] for x in k)}/{len(k)} compactions; "
          f"user msgs kept mean {sum(x['user_msgs'] for x in k) / len(k):.1f}; "
          f"context {sum(x['ctx_before'] for x in k) // len(k)} -> {sum(x.get('ctx_after_first_call') or 0 for x in k) // len(k)} tokens (mean)")


if __name__ == "__main__":
    main()
