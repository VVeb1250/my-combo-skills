"""Opt-in project-local .combo index: stdlib only, no hooks or AI calls."""
import argparse
import json
import re
from pathlib import Path

KINDS = {"specs": "spec", "changes": "change", "retro": "retro", "shortcuts": "shortcut"}

def collect(root):
    result = []
    for directory, kind in KINDS.items():
        for p in sorted((root / ".combo" / directory).rglob("*.md")):
            if p.name == "TEMPLATE.md":
                continue
            relative = p.relative_to(root).as_posix()
            if directory == "changes" and "archive" in p.parts:
                continue
            raw = p.read_text(encoding="utf-8")
            meta = {}
            if raw.startswith("---\n"):
                chunks = raw.split("---", 2)
                if len(chunks) == 3:
                    for line in chunks[1].splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            meta[key.strip()] = value.strip().strip('"')
            summary = next((s[2:].strip() for s in raw.splitlines() if s.startswith("# ")), p.stem)
            result.append({
                "id": meta.get("id", relative[:-3].replace("/", ".")),
                "kind": kind, "path": relative,
                "area": meta.get("area", p.parent.name),
                "tags": [s.strip() for s in meta.get("tags", "").split(",") if s.strip()],
                "status": meta.get("status", "draft"),
                "summary": meta.get("summary", summary),
                "evidence": meta.get("evidence", ""),
            })
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("init", "index", "check"):
        sub.add_parser(name)
    lookup = sub.add_parser("lookup")
    lookup.add_argument("--area")
    lookup.add_argument("--kind", choices=list(KINDS.values()))
    lookup.add_argument("--query")
    lookup.add_argument("--limit", type=int, default=3)
    lookup.add_argument("--digest", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    base = root / ".combo"
    if args.cmd == "init":
        for name in KINDS:
            (base / name).mkdir(parents=True, exist_ok=True)
    if args.cmd == "lookup":
        path = base / "index.json"
        if not path.exists():
            parser.error("No index: run index first")
        rows = json.loads(path.read_text(encoding="utf-8"))["entries"]
        query = (args.query or "").lower().split()
        candidates = []
        for row in rows:
            if row["status"] in ("superseded", "rejected", "archived"):
                continue
            if args.kind and row["kind"] != args.kind:
                continue
            if args.area and args.area not in [row["area"], *row["tags"]]:
                continue
            haystack = " ".join([row["summary"], row["area"], row["path"], *row["tags"]]).lower()
            if query and not any(word in haystack for word in query):
                continue
            candidates.append(row)
        for row in candidates[:max(0, args.limit)]:
            print(f'{row["kind"]} {row["status"]} {row["path"]}: {row["summary"]}')
            if args.digest:
                print((root / row["path"]).read_text(encoding="utf-8")[:500])
        return
    rows = collect(root)
    if args.cmd in ("index", "init"):
        base.mkdir(parents=True, exist_ok=True)
        (base / "index.json").write_text(json.dumps({"schema": 1, "entries": rows}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(f"indexed {len(rows)}")
        return
    errors = []
    seen = set()
    for row in rows:
        if row["id"] in seen:
            errors.append(f'duplicate id: {row["id"]}')
        seen.add(row["id"])
        if row["kind"] in ("retro", "shortcut") and row["status"] == "tested" and not row["evidence"]:
            errors.append(f'no evidence: {row["path"]}')
        if row["kind"] == "shortcut" and row["status"] == "tested":
            content = (root / row["path"]).read_text(encoding="utf-8").lower()
            for heading in ("preconditions", "validation", "fallback"):
                if not re.search(r"^## " + heading + r"\b", content, flags=re.M):
                    errors.append(f'missing {heading}: {row["path"]}')
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(rows)} records (structural check only)")

if __name__ == "__main__":
    main()
