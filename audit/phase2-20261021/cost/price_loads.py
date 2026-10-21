"""Price Combo workflow loads from stored Phase 1 Claude event logs. No model calls.

    py price_loads.py [results_dir ...]      # default: evals/compare/results/claude-run1

Facts the script relies on (checked on the data, see the check lines it prints):
  * cache_creation and cache_read from deduped assistant messages sum exactly to the run's
    final `result` usage; per-message output_tokens are streaming partials and are not used.
  * `modelUsage` splits the run's cost by model. Nine runs also billed claude-opus-5: the
    advisor tool from the owner's global config was active inside the harness sessions. That
    spend is reported as its own bucket and excluded from the Sonnet rate fit and the load
    attribution. costBasis is "list", so Sonnet cost is a deterministic function of its
    four token counts; rates are fitted from the runs, not assumed.

Counterfactual attribution of a load (what a run without the load would not have paid):
  for each message that calls Skill or Reads a file under skills/combo
    extra API call:  cache_read_i * r_read                       (re-reads the whole prefix)
    text added:      added_i * r_write                           (written once, next call)
                   + added_i * r_read * (calls after that)       (re-read on every later call)
  where added_i = cache_creation of the next message minus this message's streamed output
  (a lower bound: it also contains other new tokens, so it can slightly overstate).
Output tokens of the load messages are ignored (a lower bound; the Skill call is ~100 tokens).
"""
import json, re, statistics, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
dirs = [Path(a) for a in sys.argv[1:]] or [ROOT / "evals/compare/results/claude-run1"]
COMBO = re.compile(r"[\\/]+skills[\\/]+combo[\\/]+", re.I)  # tool inputs are JSON-escaped, so a path has doubled backslashes


def kind_of(name, inp):
    if name == "Skill":
        return "entry-stub (Skill call)"
    if re.search(r"[\\/]+workflows[\\/]+", inp):
        return "workflow file"
    if re.search(r"[\\/]+practices[\\/]+context\.md", inp):
        return "practices/context.md"
    if re.search(r"[\\/]+practices[\\/]+", inp):
        return "other practice"
    return "specialist/reference"


def load_run(meta_path: Path):
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    ev_path = Path(str(meta_path)[:-5] + ".events.jsonl")
    msgs, order, result = {}, [], None
    for line in ev_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("type") == "result":
            result = e
        if e.get("type") != "assistant":
            continue
        m = e["message"]
        mid = m.get("id")
        rec = msgs.setdefault(mid, {"usage": {}, "tools": []})
        if mid not in order:
            order.append(mid)
        rec["usage"] = m.get("usage", rec["usage"])
        for b in m.get("content", []):
            if b.get("type") == "tool_use":
                rec["tools"].append((b.get("name"), json.dumps(b.get("input", {}))))
    turns = []
    for mid in order:
        u, t = msgs[mid]["usage"], msgs[mid]["tools"]
        loads = [kind_of(n, i) for n, i in t if n == "Skill" or (n == "Read" and COMBO.search(i))]
        turns.append({"in": u.get("input_tokens", 0) or 0, "cw": u.get("cache_creation_input_tokens", 0) or 0,
                      "cr": u.get("cache_read_input_tokens", 0) or 0, "out": u.get("output_tokens", 0) or 0,
                      "loads": loads})
    return meta, turns, result


runs = []
for d in dirs:
    for p in sorted(d.glob("claude.*.json")):
        if p.name.endswith(".events.json"):
            continue
        try:
            meta, turns, result = load_run(p)
        except FileNotFoundError:
            continue
        if turns and result and result.get("usage"):
            runs.append((meta, turns, result))

# the Sonnet entry of modelUsage (its id changed between runs: claude-sonnet-5, then claude-sonnet-5-5)
SONNET = next(k for k in runs[0][2]["modelUsage"] if "sonnet" in k)
assert all(SONNET in r[2]["modelUsage"] for r in runs), "mixed Sonnet versions in one results directory"
sm = lambda r: r[2]["modelUsage"][SONNET]
bad = sum(1 for r in runs if sum(t["cw"] for t in r[1]) != sm(r)["cacheCreationInputTokens"]
          or sum(t["cr"] for t in r[1]) != sm(r)["cacheReadInputTokens"])
adv = sum(1 for r in runs if len(r[2]["modelUsage"]) > 1)
print(f"runs={len(runs)}  runs whose deduped cache sums differ from the Sonnet modelUsage: {bad}  runs that also billed another model (advisor): {adv}")

# fit rates on Sonnet-level totals
X = np.array([[sm(r)["inputTokens"], sm(r)["cacheCreationInputTokens"],
               sm(r)["cacheReadInputTokens"], sm(r)["outputTokens"]] for r in runs], float)
y = np.array([sm(r)["costUSD"] for r in runs], float)
rates, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ rates
r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
ri, rw, rr, ro = rates
print(f"fitted $/Mtok: input={ri*1e6:.2f} cache_write={rw*1e6:.2f} cache_read={rr*1e6:.2f} output={ro*1e6:.2f}  "
      f"R2={r2:.6f}  max|err|=${np.abs(y-pred).max():.5f}")

rows, events = [], defaultdict(list)
for meta, turns, result in runs:
    n = len(turns)
    u = sm((meta, turns, result))
    cost = u["costUSD"]
    advisor_cost = result["total_cost_usd"] - cost
    first = turns[0]
    base = first["cw"] * rw + first["cr"] * rr + first["in"] * ri
    out_cost = u["outputTokens"] * ro
    load = 0.0
    carry_tokens = 0
    per_event = []
    for i, t in enumerate(turns):
        if not t["loads"]:
            continue
        call = t["cr"] * rr + t["in"] * ri
        added = max(turns[i + 1]["cw"] - t["out"], 0) if i + 1 < n else 0
        later = max(n - (i + 2), 0)
        text = added * rw + added * rr * later
        load += call + text
        carry_tokens += added
        for k in t["loads"]:
            per_event.append((k, (call + text) / len(t["loads"]), added / len(t["loads"])))
    for k, c, a in per_event:
        events[k].append((c, a))
    rows.append({"arm": meta["arm"], "case": meta["case"], "rep": meta["rep"], "skills": meta.get("skills") or [],
                 "calls": n, "load_calls": sum(1 for t in turns if t["loads"]), "cost": cost, "base": base,
                 "output": out_cost, "advisor": advisor_cost, "load": load, "loaded_tokens": carry_tokens,
                 "loaded": bool(meta.get("workflow_loaded")), "passed": meta.get("passed")})


def agg(sel, label):
    if not sel:
        return
    f = lambda k: statistics.mean(r[k] for r in sel)
    print(f"{label:34} n={len(sel):2}  sonnet=${f('cost'):.3f}  advisor=${f('advisor'):.3f}  prefix(turn 1)=${f('base'):.3f} ({100*f('base')/f('cost'):.0f}%)  "
          f"output=${f('output'):.3f} ({100*f('output')/f('cost'):.0f}%)  load=${f('load'):.4f} ({100*f('load')/f('cost'):.1f}%)  "
          f"load calls={f('load_calls'):.1f}/{f('calls'):.1f}  loaded tok={f('loaded_tokens'):.0f}")


print("\n== by arm")
for arm in sorted({r["arm"] for r in rows}):
    agg([r for r in rows if r["arm"] == arm], arm)
print("\n== runs that loaded a workflow (load = counterfactual cost of the load)")
for arm in sorted({r["arm"] for r in rows}):
    agg([r for r in rows if r["arm"] == arm and r["loaded"]], f"{arm} loaded")
    agg([r for r in rows if r["arm"] == arm and not r["loaded"]], f"{arm} not loaded")
print("\n== by workflow loaded (all arms)")
by = defaultdict(list)
for r in rows:
    if r["loaded"] and r["skills"]:
        by[r["skills"][0]].append(r)
for k in sorted(by):
    agg(by[k], k)
print("\n== cost per load event type (mean over events)")
for k in sorted(events, key=lambda k: -sum(c for c, _ in events[k])):
    c = statistics.mean(c for c, _ in events[k]); a = statistics.mean(a for _, a in events[k])
    print(f"{k:28} events={len(events[k]):3}  mean cost=${c:.4f}  mean tokens added={a:.0f}")
print("\n== by case x arm")
for case in sorted({r["case"] for r in rows}):
    for arm in sorted({r["arm"] for r in rows}):
        agg([r for r in rows if r["case"] == case and r["arm"] == arm], f"{case}/{arm}")

print("\n== where the Sonnet cost goes, mean $ per run (buckets are exact sums)")
bk = defaultdict(lambda: defaultdict(list))
for (meta, turns, result), r in zip(runs, rows):
    arm = meta["arm"]
    bk[arm]["turn 1 (prefix write+read)"].append(r["base"])
    bk[arm]["later calls: context re-read"].append(sum(t["cr"] for t in turns[1:]) * rr)
    bk[arm]["later calls: new content written"].append(sum(t["cw"] for t in turns[1:]) * rw)
    bk[arm]["output"].append(r["output"])
    bk[arm]["(of which) load, counterfactual"].append(r["load"])
arms = sorted(bk)
print(f"{'bucket':40}" + "".join(f"{a:>16}" for a in arms) + f"{'difference':>14}")
for k in bk[arms[0]]:
    vals = [statistics.mean(bk[a][k]) for a in arms]
    print(f"{k:40}" + "".join(f"{v:16.4f}" for v in vals) + f"{vals[0]-vals[-1]:14.4f}")
print(f"{'total sonnet':40}" + "".join(f"{statistics.mean(r['cost'] for r in rows if r['arm']==a):16.4f}" for a in arms))
print("\n== per-call re-read cost: mean cache_read tokens per later call, by arm")
for a in arms:
    xs = [t["cr"] for (m, ts, _) in runs if m["arm"] == a for t in ts[1:]]
    print(f"{a:16} {statistics.mean(xs):8.0f} tokens -> ${statistics.mean(xs)*rr:.4f} per call")

print("\n== CLAUDE.md prefix: first-call context size and what it costs per run")
ft = {a: statistics.mean(t[0]["cw"] + t[0]["cr"] for (m, t, _) in runs if m["arm"] == a) for a in arms}
calls = {a: statistics.mean(len(t) for (m, t, _) in runs if m["arm"] == a) for a in arms}
for a in arms:
    print(f"{a:16} first-call context = {ft[a]:.0f} tokens, mean calls/run = {calls[a]:.1f}")
dtok = ft[arms[0]] - ft[arms[-1]]
for label, n in (("1-call run (negative case)", 1), ("mean run", calls[arms[0]]), ("20-call run", 20)):
    c = dtok * (rw + (n - 1) * rr)
    print(f"CLAUDE.md ({dtok:.0f} tokens) costs ${c:.4f} for a {label}")
policy = (ROOT / "adapters/claude/POLICY.md").read_text(encoding="utf-8")
ptok = len(policy) / 4
print(f"Combo policy block ~{len(policy)} chars ~{ptok:.0f} tokens (chars/4): ${ptok*(rw+(calls[arms[0]]-1)*rr):.4f} per mean run")

print("\n== per-run mean saving if one load step never happened (all runs of the arm)")
for a in arms:
    n_runs = sum(1 for r in rows if r["arm"] == a)
    parts = []
    for k, v in events.items():
        pass
    print(a, "runs:", n_runs)
per_arm_events = defaultdict(lambda: defaultdict(list))
for (meta, turns, result), r in zip(runs, rows):
    n = len(turns)
    for i, t in enumerate(turns):
        if not t["loads"]:
            continue
        call = t["cr"] * rr + t["in"] * ri
        added = max(turns[i + 1]["cw"] - t["out"], 0) if i + 1 < n else 0
        text = added * rw + added * rr * max(n - (i + 2), 0)
        for k in t["loads"]:
            per_arm_events[meta["arm"]][k].append((call + text) / len(t["loads"]))
for a in arms:
    n_runs = sum(1 for r in rows if r["arm"] == a)
    for k in sorted(per_arm_events[a]):
        tot = sum(per_arm_events[a][k])
        print(f"{a:14} {k:26} events={len(per_arm_events[a][k]):3}  per-run saving=${tot/n_runs:.4f}")

out = Path(__file__).parent / ("price_loads.json" if dirs[0].name == "claude-run1" else f"price_loads.{dirs[0].name}.json")
out.write_text(json.dumps({"rates_per_token": {"input": ri, "cache_write": rw, "cache_read": rr, "output": ro},
                           "r2": r2, "rows": rows}, indent=1), encoding="utf-8")
