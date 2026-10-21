"""Build blind labelling windows from Codex rollouts. Output goes to the scratchpad, never into the repo.

    py -I extract_windows.py <out_dir> [--seed 1]

For every compaction: a POST window (the 10 tool calls after it) and a CONTROL window (10 calls taken at
the midpoint of the same segment, at least 30 calls after the compaction and before the next one; skipped
if the segment is too short). Each window file holds the same shape: the user's last messages and the
assistant's last messages before the cut, then what happened in the 10 calls. Window ids are shuffled and
the key (id -> rollout/post|control) is written to key.json, which labellers never see.
"""
import glob, json, random, re, sys
from pathlib import Path

CMD = re.compile(r'cmd\s*:\s*"((?:[^"\\]|\\.)*)"')
W = 10
SKIP_USER = re.compile(r"^\s*(<environment_context>|# AGENTS\.md|<user_instructions>|<INSTRUCTIONS>|<permissions)", re.I)


def clip(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n] + " ..."


def events(path):
    out = []  # (kind, text) in order; kind in user|assistant|call|compact
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        t, p = o.get("type"), o.get("payload") or {}
        if t == "compacted":
            out.append(("compact", ""))
        elif t == "response_item" and p.get("type") == "message" and p.get("role") in ("user", "assistant"):
            txt = " ".join(c.get("text", "") for c in p.get("content") or [] if isinstance(c, dict))
            if p["role"] == "user" and (SKIP_USER.match(txt) or len(txt) > 4000):
                continue
            if txt.strip():
                out.append((p["role"], txt))
        elif t == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
            text = p.get("input") if isinstance(p.get("input"), str) else p.get("arguments", "")
            text = text if isinstance(text, str) else json.dumps(text)
            cmds = CMD.findall(text)
            out.append(("call", " | ".join(clip(c, 160) for c in cmds) if cmds else clip(text, 200)))
    return out


def render(ev, cut, ncalls):
    """cut = index in ev where the window starts; the 'before' part is what preceded it."""
    before = [e for e in ev[:cut] if e[0] in ("user", "assistant")]
    users = [e for e in before if e[0] == "user"][-6:]
    assist = [e for e in before if e[0] == "assistant"][-4:]
    lines = ["## BEFORE THE CUT (most recent user messages, then assistant messages)"]
    lines += [f"USER: {clip(t, 700)}" for _, t in users]
    lines += [f"ASSISTANT: {clip(t, 500)}" for _, t in assist]
    lines.append("## AFTER THE CUT (in order)")
    n = 0
    for k, t in ev[cut:]:
        if k == "compact":
            break
        if k == "call":
            if n >= ncalls:
                break
            n += 1
            lines.append(f"CALL {n}: {t}")
        elif k == "user":
            lines.append(f"USER: {clip(t, 700)}")
        elif k == "assistant":
            lines.append(f"ASSISTANT: {clip(t, 500)}")
    return "\n".join(lines)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    items = []
    for f in sorted(glob.glob(str(Path.home() / ".codex/sessions/**/rollout-*.jsonl"), recursive=True)):
        ev = events(f)
        cuts = [i for i, e in enumerate(ev) if e[0] == "compact"]
        for ci, c in enumerate(cuts):
            end = cuts[ci + 1] if ci + 1 < len(cuts) else len(ev)
            calls_idx = [i for i in range(c + 1, end) if ev[i][0] == "call"]
            rid = Path(f).stem.split("rollout-")[1][:19]
            items.append((rid, "post", render(ev, c + 1, W)))
            if len(calls_idx) >= 30 + W + 5:
                mid = calls_idx[30 + (len(calls_idx) - 30 - W) // 2]
                items.append((rid, "control", render(ev, mid, W)))
    random.Random(seed).shuffle(items)
    key = {}
    for n, (rid, kind, body) in enumerate(items, 1):
        wid = f"w{n:02d}"
        (out / f"{wid}.txt").write_text(body, encoding="utf-8")
        key[wid] = {"rollout": rid, "kind": kind, "chars": len(body)}
    (out / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    kinds = [v["kind"] for v in key.values()]
    print(f"windows {len(key)} (post {kinds.count('post')}, control {kinds.count('control')}); mean chars {sum(v['chars'] for v in key.values()) // len(key)}")


if __name__ == "__main__":
    main()
