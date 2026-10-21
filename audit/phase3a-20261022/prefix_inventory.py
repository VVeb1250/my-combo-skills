"""Phase 3A offline: what each MCP server, plugin and skill adds to the prefix, and whether this project used it. No model calls.

    py -I prefix_inventory.py --size-from <session-uuid> [--exclude <session-uuid> ...] [--out prefix_inventory.json]

Sizes come from the attachments a session received before its first model call (deferred-tool names, skill listing,
MCP instructions, agent listing); tokens are chars/4 [E]. Usage comes from every transcript of this project
(main + subagents): `mcp__<server>__*` tool calls, `Skill` calls, `Agent` calls, and `ToolSearch` selects.
Reads ~/.claude/settings.json (enabledPlugins, skillOverrides) read-only. Writes nothing to settings.
"""
import argparse, json, re
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
ROOT = HOME / ".claude/projects/D--0-person-project-my-combo-skills"
# $ saved per 1K prefix tokens over the 7 main sessions audited: 631 turns re-read at $0.10/Mtok + 7 cache writes at $4/Mtok
SAVE_PER_1K = 1000 * (0.1e-6 * 631 + 4e-6 * 7)
TOTAL_SPEND = 44.40 + 9.06


def attachments(uuid):
    got = {}
    for line in open(ROOT / f"{uuid}.jsonl", encoding="utf8", errors="replace"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            break
        if o.get("type") == "attachment":
            a = o["attachment"]
            got.setdefault(a.get("type"), a)
    return got


def server_of(tool):
    m = re.match(r"mcp__(.+?)__", tool)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size-from", required=True)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--out", default=str(Path(__file__).with_name("prefix_inventory.json")))
    a = ap.parse_args()
    att = attachments(a.size_from)

    # sizes
    srv = defaultdict(lambda: {"tools": 0, "name_chars": 0, "instr_chars": 0})
    for line in att["deferred_tools_delta"]["addedLines"]:
        s = server_of(line)
        key = s if s else "(built-in deferred)"
        srv[key]["tools"] += 1
        srv[key]["name_chars"] += len(line) + 1
    blocks = att.get("mcp_instructions_delta", {})
    for name, block in zip(blocks.get("addedNames", []), blocks.get("addedBlocks", [])):
        srv[name]["instr_chars"] += len(block)
    needs_auth = att["deferred_tools_delta"].get("needsAuthMcpServers", [])
    pending = att["deferred_tools_delta"].get("pendingMcpServers", [])

    skills = {}
    lines = att["skill_listing"]["content"].splitlines()
    names = sorted(att["skill_listing"]["names"], key=len, reverse=True)  # longest first so "a:b" wins over "a"
    for ln in lines:
        body = ln[2:] if ln.startswith("- ") else ln
        for name in names:
            if body.startswith(name + ":"):
                skills[name] = len(ln) + 1
                break
    for name in names:
        skills.setdefault(name, 0)

    # usage
    use_srv, use_skill, use_agent = defaultdict(int), defaultdict(int), defaultdict(int)
    sess_srv, sess_skill = defaultdict(set), defaultdict(set)
    selects = defaultdict(int)
    files = []
    for p in sorted(ROOT.glob("*.jsonl")):
        if p.stem in a.exclude:
            continue
        files.append(p)
        sub = ROOT / p.stem / "subagents"
        if sub.is_dir():
            files += sorted(sub.glob("*.jsonl"))
    seen = set()
    for f in files:
        sid = f.parent.parent.name[:8] if f.parent.name == "subagents" else f.stem[:8]
        for line in open(f, encoding="utf8", errors="replace"):
            if '"tool_use"' not in line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            m = o.get("message") or {}
            if o.get("type") != "assistant":
                continue
            for b in m.get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("id") in seen:
                    continue
                seen.add(b.get("id"))
                n, inp = b.get("name", ""), b.get("input") or {}
                s = server_of(n)
                if s:
                    use_srv[s] += 1
                    sess_srv[s].add(sid)
                elif n == "Skill":
                    k = str(inp.get("skill", "?"))
                    use_skill[k] += 1
                    sess_skill[k].add(sid)
                elif n == "Agent":
                    use_agent[str(inp.get("subagent_type", "general-purpose"))] += 1
                elif n == "ToolSearch":
                    for mm in re.findall(r"mcp__(.+?)__", str(inp.get("query", ""))):
                        selects[mm] += 1

    settings = json.load(open(HOME / ".claude/settings.json", encoding="utf8"))
    plugins = settings.get("enabledPlugins", {})
    overrides = settings.get("skillOverrides", {})

    out = {"sessions": len(files), "enabled_plugins": plugins, "skill_overrides": overrides, "needs_auth_servers": needs_auth,
           "pending_servers": pending, "servers": {}, "skills": {}, "agents_used": dict(use_agent), "per_1k_tokens_saves_usd": SAVE_PER_1K}
    for s, v in srv.items():
        tok = (v["name_chars"] + v["instr_chars"]) // 4
        out["servers"][s] = {**v, "tokens": tok, "calls": use_srv.get(s, 0), "sessions_used": len(sess_srv.get(s, ())),
                             "tool_search_selects": selects.get(s, 0), "pct_of_spend": round(tok / 1000 * SAVE_PER_1K / TOTAL_SPEND * 100, 2)}
    for s in list(use_srv):
        if s not in out["servers"]:
            out["servers"][s] = {"tools": 0, "name_chars": 0, "instr_chars": 0, "tokens": 0, "calls": use_srv[s],
                                 "sessions_used": len(sess_srv[s]), "tool_search_selects": selects.get(s, 0), "pct_of_spend": 0.0,
                                 "note": "used but not in the sized first-call attachment (connected later)"}
    for s, ch in skills.items():
        out["skills"][s] = {"tokens": ch // 4, "calls": use_skill.get(s, 0), "sessions_used": len(sess_skill.get(s, ()))}
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    tot_srv = sum(v["tokens"] for v in out["servers"].values())
    tot_skill = sum(v["tokens"] for v in out["skills"].values())
    print(f"transcripts {len(files)}; deferred-tool names + MCP instructions ~{tot_srv:,d} tok; skill listing ~{tot_skill:,d} tok ({len(skills)} skills)")
    print(f"enabled plugins {len(plugins)}; skillOverrides {len(overrides)}; MCP servers needing auth {len(needs_auth)}; one 1K tokens ~ ${SAVE_PER_1K:.3f} = {SAVE_PER_1K / TOTAL_SPEND * 100:.2f}% of spend")
    print("\nMCP / deferred-tool groups by prefix tokens: server, tools, instr tok, name tok, calls, sessions, %spend")
    for s, v in sorted(out["servers"].items(), key=lambda kv: -kv[1]["tokens"]):
        print(f"  {s[:40]:40s} {v['tools']:4d} {v['instr_chars'] // 4:6d} {v['name_chars'] // 4:6d} {v['calls']:5d} {v['sessions_used']:3d} {v['pct_of_spend']:5.2f}")
    print("\nplugins enabled:", ", ".join(f"{k}={v}" for k, v in plugins.items()))
    by_plugin = defaultdict(lambda: [0, 0, 0])
    for s, v in out["skills"].items():
        key = s.split(":", 1)[0] if ":" in s else "(standalone)"
        by_plugin[key][0] += 1
        by_plugin[key][1] += v["tokens"]
        by_plugin[key][2] += v["calls"]
    print("\nskills grouped by namespace: group, skills, tokens, calls")
    for k, (n, t, c) in sorted(by_plugin.items(), key=lambda kv: -kv[1][1]):
        print(f"  {k[:34]:34s} {n:4d} {t:6d} {c:4d}")
    print("\nskill calls:", {k: v for k, v in sorted(use_skill.items(), key=lambda kv: -kv[1])})
    print("agent types used:", dict(use_agent))


if __name__ == "__main__":
    main()
