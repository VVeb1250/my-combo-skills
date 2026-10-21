"""Phase 3A offline cost audit of real Claude Code transcripts. No model calls.

    py -I audit_real_sessions.py [--exclude <session-uuid> ...] [--out audit.json]

Reads ~/.claude/projects/<slug>/*.jsonl plus <uuid>/subagents/*.jsonl. Prints and stores
aggregates only (no prompt text). Reuses the method of ../phase2-20261021/cost/price_loads.py:
usage is deduped by assistant message id (a streamed message repeats on several lines; cache
fields are stable, output_tokens grows, so the max is kept) and priced at list rates.

Rates, $ per Mtok, claude-sonnet-5-5 (fitted exactly in cost-experiment/RESULTS.md):
input 2.00, cache write 1h 4.00, cache read 0.10, output 10.00. A 5-minute write is not
priced separately in that fit; it is priced at 2.50 (1.25x input). Other models are reported
in tokens only because no fitted rate exists for them in this repo.

Estimates (labelled [E]): tool-result tokens are chars/4 of the stored result text.
Carried cost of a result = tokens * (write once + re-read on every later call of the same
segment). A segment ends at a compaction, detected as cache_read falling below half the
previous call's cache_read.
"""
import argparse, json, re
from collections import defaultdict
from pathlib import Path

# $/Mtok. Sonnet 5.5 is fitted from logs (cost-experiment/RESULTS.md); the others apply the same
# structure to the list prices in the claude-api skill (Opus 5.5 $4/$20, Haiku 5.5 $0.10/$0.50, prompts
# up to 100K): 1h write = 2x input, 5m write = 1.25x, read = 0.05x. [I] -- the skill text says
# cache reads are $0.20 for Sonnet 5.5, which the fit contradicts ($0.10), so doc multipliers are not trusted.
def _r(i, o):
    return {"in": i, "cw1h": 2 * i, "cw5m": 1.25 * i, "cr": 0.05 * i, "out": o}
RATES = {"claude-sonnet-5-5": _r(2.00, 10.00), "claude-opus-5-5": _r(4.00, 20.00), "claude-haiku-5-5": _r(0.10, 0.50)}
RATE = RATES["claude-sonnet-5-5"]  # used for carried-cost estimates of the main model
BUST_TOKENS = 10_000  # unexplained cache write above this is reported as a bust


def usd(tokens, key, model="claude-sonnet-5-5"):
    return tokens * RATES.get(model, RATE)[key] / 1e6


def text_len(c):
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        n = 0
        for b in c:
            if isinstance(b, dict):
                n += len(b["text"]) if b.get("type") == "text" else len(json.dumps(b)) if b.get("type") != "image" else 6000
        return n
    return len(json.dumps(c)) if c else 0


def parse(path, seen_ids):
    """Return list of turns for one transcript file. Turn = one deduped assistant message."""
    turns, by_id, pending_chars = [], {}, 0
    results = {}  # tool_use_id -> (turn index, chars)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        t = o.get("type")
        if t == "assistant":
            m = o.get("message") or {}
            mid = m.get("id")
            u = m.get("usage") or {}
            if mid in by_id:
                rec = by_id[mid]
                rec["out"] = max(rec["out"], u.get("output_tokens", 0) or 0)
            else:
                if mid in seen_ids:  # same message copied into a forked/resumed transcript
                    continue
                seen_ids.add(mid)
                cc = u.get("cache_creation") or {}
                cw = u.get("cache_creation_input_tokens", 0) or 0
                w1 = cc.get("ephemeral_1h_input_tokens", cw)
                rec = {"id": mid, "model": m.get("model"), "in": u.get("input_tokens", 0) or 0, "cw": cw,
                       "cw1h": w1, "cw5m": cw - w1, "cr": u.get("cache_read_input_tokens", 0) or 0,
                       "out": u.get("output_tokens", 0) or 0, "tools": [], "gap_chars": pending_chars,
                       "ts": o.get("timestamp"),
                       "iters": [i.get("type") for i in u.get("iterations") or [] if i.get("type") != "message"],
                       "adv": [(i.get("model"), i.get("input_tokens", 0) or 0, i.get("output_tokens", 0) or 0)
                               for i in u.get("iterations") or [] if i.get("type") == "advisor_message"]}
                pending_chars = 0
                by_id[mid] = rec
                turns.append(rec)
            for b in m.get("content") or []:
                if b.get("type") == "tool_use" and all(b["id"] != x["id"] for x in by_id[mid]["tools"]):
                    by_id[mid]["tools"].append({"id": b["id"], "name": b.get("name"), "input": b.get("input") or {}})
        elif t in ("user", "attachment", "system"):
            msg = o.get("message") if t == "user" else o.get("attachment")
            content = msg.get("content") if isinstance(msg, dict) and t == "user" else msg
            if t == "user" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        n = text_len(b.get("content"))
                        results[b["tool_use_id"]] = (len(turns) - 1, n)
                        pending_chars += n
                    else:
                        pending_chars += text_len([b]) if isinstance(b, dict) else len(str(b))
            else:
                pending_chars += text_len(content)
    return turns, results


def segments(turns):
    seg, cur = [], 0
    for i, t in enumerate(turns):
        if i and turns[i - 1]["cr"] > 20_000 and t["cr"] < 0.5 * turns[i - 1]["cr"]:
            cur += 1
        seg.append(cur)
    return seg


def analyse(label, path, seen_ids, kind, agent_type=None):
    turns, results = parse(path, seen_ids)
    if not turns:
        return None
    seg = segments(turns)
    last_in_seg = {}
    for i, s in enumerate(seg):
        last_in_seg[s] = i
    cost = defaultdict(float)
    tok = defaultdict(int)
    models = defaultdict(int)
    for t in turns:
        models[t["model"]] += 1
        tok["in"] += t["in"]; tok["cw"] += t["cw"]; tok["cr"] += t["cr"]; tok["out"] += t["out"]
        m = t["model"]
        cost["in"] += usd(t["in"], "in", m); cost["cw"] += usd(t["cw1h"], "cw1h", m) + usd(t["cw5m"], "cw5m", m)
        cost["cr"] += usd(t["cr"], "cr", m); cost["out"] += usd(t["out"], "out", m)
        cost["m:" + str(m)] += usd(t["in"], "in", m) + usd(t["cw1h"], "cw1h", m) + usd(t["cw5m"], "cw5m", m) + usd(t["cr"], "cr", m) + usd(t["out"], "out", m)
    # advisor calls: billed inside the executor's usage as `advisor_message` iterations, uncached
    adv = [a for t in turns for a in t["adv"]]
    cost["advisor"] = sum(usd(i, "in", m) + usd(o, "out", m) for m, i, o in adv)
    dup_adv = {"calls": len(adv), "input_tok": sum(i for _, i, _ in adv), "output_tok": sum(o for _, _, o in adv)}
    # tool accounting
    tool = defaultdict(lambda: {"calls": 0, "result_tok": 0, "carried": 0.0})
    owner = {}
    for i, t in enumerate(turns):
        for u in t["tools"]:
            owner[u["id"]] = (i, u)
            tool[u["name"]]["calls"] += 1
    for tid, (_, chars) in results.items():
        if tid not in owner:
            continue
        i, u = owner[tid]
        n = chars / 4
        k = last_in_seg[seg[i]] - i  # calls after the one that issued the tool
        carried = n * (RATE["cw1h"] + RATE["cr"] * max(k - 1, 0)) / 1e6 if k > 0 else 0.0
        tool[u["name"]]["result_tok"] += n
        tool[u["name"]]["carried"] += carried
    # duplicate work: a Read of the same path/range, or an identical shell command, already done earlier
    # with no Edit/Write of that path since. "within" = same segment; "after_compaction" = first done in
    # an earlier segment, i.e. work re-done because a compaction dropped it from context.
    dup = dict.fromkeys(("read_within", "read_after_compaction", "cmd_within", "cmd_after_compaction",
                         "carried_within", "carried_after_compaction", "rebuild_turns_after_compaction"), 0.0)
    read_at, cmd_at, edit_at = {}, {}, {}
    for i, t in enumerate(turns):
        for u in t["tools"]:
            inp, name = u["input"], u["name"]
            r = results.get(u["id"])
            if name in ("Edit", "Write", "NotebookEdit"):
                edit_at[inp.get("file_path")] = i
                continue
            if name == "Read":
                key, path = ("R", inp.get("file_path"), inp.get("offset"), inp.get("limit")), inp.get("file_path")
            elif name in ("Bash", "PowerShell"):
                key, path = ("C", name, re.sub(r"\s+", " ", str(inp.get("command", ""))).strip()), None
            else:
                continue
            prev = (read_at if key[0] == "R" else cmd_at).get(key)
            if prev is not None and (path is None or edit_at.get(path, -1) < prev):
                kind = "within" if seg[prev] == seg[i] else "after_compaction"
                dup[("read_" if key[0] == "R" else "cmd_") + kind] += 1
                if r:
                    k = last_in_seg[seg[i]] - i
                    dup["carried_" + kind] += r[1] / 4 * (RATE["cw1h"] + RATE["cr"] * max(k - 1, 0)) / 1e6 if k > 0 else 0
            (read_at if key[0] == "R" else cmd_at)[key] = i
    # rebuild cost: the cache write on the first call after each compaction (the new summary + re-read prefix)
    rebuilds = [turns[i]["cw"] for i in range(1, len(turns)) if seg[i] != seg[i - 1]]
    dup["rebuild_turns_after_compaction"] = len(rebuilds)
    # cache busts: cache write not explained by new content
    busts = []
    for i in range(1, len(turns)):
        t, p = turns[i], turns[i - 1]
        if seg[i] != seg[i - 1]:
            continue
        explained = p["out"] + t["gap_chars"] / 4
        extra = t["cw"] - explained
        lost = max(p["cr"] + p["cw"] - t["cr"], 0)  # prefix not read back
        if extra > BUST_TOKENS:
            busts.append({"turn": i, "unexplained_write_tok": int(extra), "prefix_lost_tok": int(lost),
                          "cost": usd(extra, "cw1h", t["model"]) - usd(extra, "cr", t["model"])})
    total = sum(v for k, v in cost.items() if not k.startswith("m:") and k != "advisor")
    cost = {k: cost[k] for k in ("in", "cw", "cr", "out", "advisor")} | {k: v for k, v in cost.items() if k.startswith("m:")}
    return {"label": label, "kind": kind, "agent_type": agent_type, "turns": len(turns), "segments": seg[-1] + 1,
            "models": dict(models), "tokens": dict(tok), "cost": {**cost, "total": total},
            "tools": {k: {**v, "result_tok": int(v["result_tok"])} for k, v in tool.items()},
            "advisor": dup_adv, "dup": dup, "busts": busts, "non_message_iterations": sorted({x for t in turns for x in t["iters"]}),
            "first_ts": turns[0]["ts"], "last_ts": turns[-1]["ts"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / ".claude/projects/D--0-person-project-my-combo-skills"))
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--out", default=str(Path(__file__).with_name("audit.json")))
    a = ap.parse_args()
    root = Path(a.root)
    seen, out = set(), []
    for p in sorted(root.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        if p.stem in a.exclude:
            continue
        r = analyse(p.stem[:8], p, seen, "main")
        if r:
            out.append(r)
        sub = root / p.stem / "subagents"
        for sp in sorted(sub.glob("*.jsonl")) if sub.is_dir() else []:
            meta = {}
            mp = sp.with_suffix(".meta.json")
            if mp.exists():
                meta = json.loads(mp.read_text(encoding="utf-8"))
            r = analyse(p.stem[:8], sp, seen, "subagent", meta.get("agentType") or meta.get("subagent_type") or "?")
            if r:
                out.append(r)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


def report(out):
    mains = [r for r in out if r["kind"] == "main"]
    subs = [r for r in out if r["kind"] == "subagent"]
    allm = defaultdict(int)
    for r in out:
        for m, n in r["models"].items():
            allm[m] += n
    print("models (turns):", dict(allm))
    print("non-message iteration types seen:", sorted({x for r in out for x in r["non_message_iterations"]}) or "none")
    tot = defaultdict(float)
    for r in out:
        for k, v in r["cost"].items():
            tot[k] += v
    T = tot["total"] or 1
    print("by model $:", {k[2:]: round(v, 2) for k, v in tot.items() if k.startswith("m:")})
    print(f"\nTOTAL ${T:.2f}  main ${sum(r['cost']['total'] for r in mains):.2f}  subagents ${sum(r['cost']['total'] for r in subs):.2f}")
    for k in ("cw", "cr", "out", "in"):
        print(f"  {k:3s} ${tot[k]:.2f} ({tot[k]/T:.0%})")
    print("\nper session (main): turns segments total$ cw% cr% out% | subagent$")
    for r in mains:
        c = r["cost"]; s = c["total"] or 1
        sub = sum(x["cost"]["total"] for x in subs if x["label"] == r["label"])
        print(f"  {r['label']} {r['turns']:4d}t {r['segments']}seg ${c['total']:.2f}  cw {c['cw']/s:.0%} cr {c['cr']/s:.0%} out {c['out']/s:.0%} | sub ${sub:.2f}")
    agg = defaultdict(lambda: {"calls": 0, "result_tok": 0, "carried": 0.0})
    for r in out:
        for k, v in r["tools"].items():
            for f in agg[k]:
                agg[k][f] += v[f]
    print("\ntool ranking by carried cost [E]  (calls, result tok, carried $, % of priced total)")
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["carried"])[:15]:
        print(f"  {k[:46]:46s} {v['calls']:5d} {v['result_tok']:9.0f} ${v['carried']:6.2f} {v['carried']/T:5.1%}")
    d = defaultdict(float)
    for r in out:
        for k, v in r["dup"].items():
            d[k] += v
    print(f"\ncompactions: {sum(r['segments'] - 1 for r in out)} across {sum(1 for r in out if r['segments'] > 1)} transcripts")
    print(f"duplicate work within a segment: Read {d['read_within']:.0f}, cmd {d['cmd_within']:.0f}, carried ${d['carried_within']:.2f}")
    print(f"duplicate work AFTER a compaction (done before it, no edit since): Read {d['read_after_compaction']:.0f}, "
          f"cmd {d['cmd_after_compaction']:.0f}, carried ${d['carried_after_compaction']:.2f}")
    busts = [(b, r["label"]) for r in out for b in r["busts"]]
    print(f"cache-write spikes >{BUST_TOKENS} tok unexplained by new content: {len(busts)}, extra write cost ${sum(b['cost'] for b, _ in busts):.2f}")
    bt = defaultdict(lambda: [0, 0.0])
    for r in subs:
        bt[r["agent_type"]][0] += 1; bt[r["agent_type"]][1] += r["cost"]["total"]
    print("subagents by type (n, priced $):", {k: (v[0], round(v[1], 2)) for k, v in bt.items()})
    ac = sum(r["advisor"]["calls"] for r in out); ai = sum(r["advisor"]["input_tok"] for r in out)
    print(f"advisor (Opus, uncached, on top of the total above): {ac} calls, {ai} input tok (mean {ai // max(ac, 1)} per call), "
          f"${sum(r['cost']['advisor'] for r in out):.2f}")


if __name__ == "__main__":
    main()
