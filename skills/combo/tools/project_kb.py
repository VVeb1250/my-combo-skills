"""Opt-in .combo progressive index: local metadata, deliberate one-hop navigation.

No network, LLM, background task, mutable global state, or project code execution.
Read-only commands never scaffold .combo; explicit init and index write.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath

try:
    import tomllib
except ImportError:  # Python <3.11 can still read legacy metadata.
    tomllib = None

KINDS = {
    "areas": "area",
    "specs": "spec",
    "changes": "change",
    "decisions": "decision",
    "verification": "verification",
    "retro": "retro",
    "shortcuts": "shortcut",
    "techniques": "technique",
}
INACTIVE = frozenset({"superseded", "rejected", "archived"})
RELATIONS = frozenset({"constrained_by", "related_to", "depends_on", "verified_by", "supersedes", "informs"})
SCHEMA = 3
TECHNIQUE_STATES = frozenset({"candidate", "prototyped", "project-tested",
                              "portable-candidate", "cross-project-tested",
                              "rejected", "superseded"})
TECHNIQUE_TESTED = frozenset({"prototyped", "project-tested",
                              "portable-candidate", "cross-project-tested"})


class IndexErrorInfo(ValueError):
    """Invalid, stale or unsafe project knowledge; do not silently route."""


def _normalize_list(value, key, location):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [s.strip() for s in value.split(",") if s.strip()]
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return [x.strip() for x in value if x.strip()]
    raise IndexErrorInfo(f"{location}: '{key}' must be a list of strings or comma-separated text")


def _metadata(raw, location):
    if raw.startswith("+++\n"):
        if not tomllib:
            raise IndexErrorInfo(f"{location}: TOML frontmatter requires Python 3.11+")
        pos = raw.find("\n+++\n", 4)
        if pos < 0:
            raise IndexErrorInfo(f"{location}: unclosed TOML frontmatter")
        try:
            return tomllib.loads(raw[4:pos]), raw[pos + 5:]
        except tomllib.TOMLDecodeError as exc:
            raise IndexErrorInfo(f"{location}: invalid TOML: {exc}") from exc
    if raw.startswith("---\n"):
        pos = raw.find("\n---\n", 4)
        if pos < 0:
            raise IndexErrorInfo(f"{location}: unclosed legacy frontmatter")
        meta = {}
        for line in raw[4:pos].splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if ":" not in line or line.startswith((" ", "\t")):
                raise IndexErrorInfo(f"{location}: legacy frontmatter supports flat 'key: value' only")
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta, raw[pos + 5:]
    return {}, raw


def _inside(root, path):
    root = root.resolve()
    candidate = path.resolve()
    if not candidate.is_relative_to(root):
        raise IndexErrorInfo(f"path escapes project: {path}")
    return candidate


def _paths(root):
    base = root / ".combo"
    for subdir in KINDS:
        folder = base / subdir
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.md")):
            if path.name == "TEMPLATE.md" or path.is_symlink():
                continue
            if subdir == "changes" and "archive" in path.relative_to(folder).parts:
                continue
            _inside(root, path)
            yield subdir, path


def _global_paths(root):
    """Curated global recipe shelf. Only recipes/*.md are indexed."""
    folder = root / "recipes"
    if not folder.is_dir():
        return
    for path in sorted(folder.rglob("*.md")):
        if path.name == "TEMPLATE.md" or path.is_symlink():
            continue
        _inside(root, path)
        yield "techniques", path


def _source_paths(root, *, global_catalog=False):
    return _global_paths(root) if global_catalog else _paths(root)


def _index_path(root, *, global_catalog=False):
    return root / "index.json" if global_catalog else root / ".combo" / "index.json"


def _parse_links(value, location):
    if value is None:
        return []
    # TOML: [[links]] relation="related_to" target="...";
    # legacy: relates_to: id1, id2 (treated as related_to).
    if not isinstance(value, list):
        raise IndexErrorInfo(f"{location}: 'links' must be a list of tables")
    out = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("relation"), str) or not isinstance(item.get("target"), str):
            raise IndexErrorInfo(f"{location}: each link requires relation and target strings")
        if item["relation"] not in RELATIONS:
            raise IndexErrorInfo(f"{location}: unknown relation {item['relation']!r}")
        out.append({"relation": item["relation"], "target": item["target"]})
    return out


def collect(root, *, global_catalog=False):
    root = Path(root).resolve()
    result = []
    for folder, p in _source_paths(root, global_catalog=global_catalog):
        relative = p.relative_to(root).as_posix()
        data = p.read_bytes()
        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IndexErrorInfo(f"{relative}: expected UTF-8") from exc
        # Checked-out files may be CRLF (core.autocrlf on Windows). Parse and
        # hash the normalized text so line endings are not content drift.
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        data = raw.encode("utf-8")
        meta, body = _metadata(raw, relative)
        if not isinstance(meta, dict):
            raise IndexErrorInfo(f"{relative}: metadata must be a mapping")
        ident = meta.get("id", relative[:-3].replace("/", "."))
        if not isinstance(ident, str) or not ident or not re.fullmatch(r"[\w.:-]+", ident):
            raise IndexErrorInfo(f"{relative}: invalid stable ID {ident!r}")
        title = next((s[2:].strip() for s in body.splitlines() if s.startswith("# ")), p.stem)
        kind = KINDS[folder]
        area = meta.get("area", p.stem if folder == "areas" else p.parent.name)
        status = meta.get("status", "draft")
        summary = meta.get("summary", title)
        if not all(isinstance(x, str) and x for x in (area, status, summary)):
            raise IndexErrorInfo(f"{relative}: area/status/summary must be nonempty strings")
        links = _parse_links(meta.get("links"), relative)
        for target in _normalize_list(meta.get("relates_to"), "relates_to", relative):
            links.append({"relation": "related_to", "target": target})
        evidence = _normalize_list(meta.get("evidence"), "evidence", relative)
        paths = _normalize_list(meta.get("paths"), "paths", relative)
        for pattern in paths:
            if pattern.startswith(("/", "~")) or ".." in PurePosixPath(pattern).parts or "\\" in pattern:
                raise IndexErrorInfo(f"{relative}: unsafe project-relative path pattern: {pattern}")
        record = {
            "id": ident, "kind": kind, "path": relative,
            "area": area, "status": status, "summary": summary,
            "tags": _normalize_list(meta.get("tags"), "tags", relative),
            "paths": paths, "links": links, "evidence": evidence,
            "validated_at": str(meta.get("validated_at", "")),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        if kind == "technique":
            if "id" not in meta:
                raise IndexErrorInfo(f"{relative}: technique requires an explicit stable id")
            for field in ("problem_signals", "engine", "renderer"):
                record[field] = _normalize_list(meta.get(field), field, relative)
        result.append(record)
    return result


def _validate(root, rows, *, external_ids=()):
    errors = []
    by_id = {}
    allowed_external = set(external_ids)
    for row in rows:
        ident = row["id"]
        if ident in by_id:
            errors.append(f"duplicate id {ident!r}: {by_id[ident]['path']} and {row['path']}")
        by_id[ident] = row
    for row in rows:
        for edge in row["links"]:
            if edge["target"] not in by_id and edge["target"] not in allowed_external:
                errors.append(f"{row['path']}: broken {edge['relation']} -> {edge['target']}")
            if edge["target"] == row["id"]:
                errors.append(f"{row['path']}: self link {edge['relation']}")
        if row["kind"] == "technique":
            if row["status"] not in TECHNIQUE_STATES:
                errors.append(f"{row['path']}: unknown technique status {row['status']!r}")
            if not row["problem_signals"]:
                errors.append(f"{row['path']}: technique requires problem_signals")
            content = (root / row["path"]).read_text(encoding="utf-8").lower()
            for heading in ("problem and decision rule", "mechanism",
                            "applicability and constraints", "implementation",
                            "trade-offs and failure modes", "verification"):
                if not re.search(r"^## " + re.escape(heading) + r"\b", content, re.MULTILINE):
                    errors.append(f"{row['path']}: technique lacks section: {heading}")
            if row["status"] in TECHNIQUE_TESTED and not row["evidence"]:
                errors.append(f"{row['path']}: {row['status']} technique lacks evidence")
            local_evidence = False
            for pointer in row["evidence"]:
                if pointer in by_id:
                    local_evidence = True
                    continue
                if pointer.startswith(("https://", "http://")):
                    continue  # Remote source remains unverified.
                value = PurePosixPath(pointer)
                if (not pointer or pointer.startswith(("/", "~")) or
                        "\\" in pointer or ".." in value.parts):
                    errors.append(f"{row['path']}: unsafe technique evidence: {pointer!r}")
                    continue
                target = root / pointer
                try:
                    _inside(root, target)
                    if not target.is_file():
                        errors.append(f"{row['path']}: missing technique evidence: {pointer}")
                    else:
                        local_evidence = True
                except (OSError, IndexErrorInfo):
                    errors.append(f"{row['path']}: invalid technique evidence: {pointer}")
            if row["status"] in TECHNIQUE_TESTED and not local_evidence:
                errors.append(f"{row['path']}: {row['status']} requires local evidence or a record link")
        if row["kind"] in ("retro", "shortcut") and row["status"] == "tested":
            if not row["evidence"]:
                errors.append(f"{row['path']}: tested {row['kind']} lacks evidence")
            if row["kind"] == "shortcut":
                content = (root / row["path"]).read_text(encoding="utf-8").lower()
                for heading in ("preconditions", "validation", "fallback"):
                    if not re.search(r"^## " + heading + r"\b", content, re.MULTILINE):
                        errors.append(f"{row['path']}: tested shortcut lacks section: {heading}")
    return errors


def _index_data(rows):
    counts = Counter(row["area"] for row in rows)
    areas = {}
    for area in sorted(counts):
        area_rows = [r for r in rows if r["area"] == area]
        descriptors = [r for r in area_rows if r["kind"] == "area"]
        areas[area] = {
            "count": counts[area],
            "summary": descriptors[0]["summary"] if descriptors else f"{area} project knowledge",
            "entrypoints": sorted({p for r in area_rows if r["kind"] == "area" for p in r["paths"]}),
            "ids": [r["id"] for r in area_rows],
        }
    return {"schema": SCHEMA, "areas": areas, "entries": rows}


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=".index-", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def rebuild(root, *, global_catalog=False, external_ids=()):
    root = Path(root).resolve()
    rows = collect(root, global_catalog=global_catalog)
    errors = _validate(root, rows, external_ids=external_ids)
    if errors:
        raise IndexErrorInfo("\n".join(errors))
    data = _index_data(rows)
    _atomic_write(_index_path(root, global_catalog=global_catalog),
                  json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return data


def _stale_detail(old, current):
    old_entries = {row["path"]: row for row in old.get("entries", [])}
    new_entries = {row["path"]: row for row in current.get("entries", [])}
    lines = []
    for path in sorted(new_entries.keys() - old_entries.keys()):
        lines.append(f"added: {path}")
    for path in sorted(old_entries.keys() - new_entries.keys()):
        lines.append(f"removed: {path}")
    for path in sorted(old_entries.keys() & new_entries.keys()):
        before, after = old_entries[path], new_entries[path]
        if before.get("sha256") != after.get("sha256"):
            lines.append(f"changed: {path}")
        elif before != after:
            lines.append(f"index record differs (tampered?): {path}")
    if old.get("areas") != current.get("areas"):
        lines.append("area index differs")
    return lines


def load_index(root, *, global_catalog=False, external_ids=()):
    root = Path(root).resolve()
    path = _index_path(root, global_catalog=global_catalog)
    if not path.exists():
        raise IndexErrorInfo("missing .combo/index.json; run 'index' (does not create .combo automatically during lookup)")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise IndexErrorInfo("invalid .combo/index.json; run 'index'") from exc
    if data.get("schema") != SCHEMA:
        raise IndexErrorInfo(f"index schema {data.get('schema')} unsupported; run 'index' to migrate")
    current = collect(root, global_catalog=global_catalog)
    current_index = _index_data(current)
    # Compare the entire generated representation: the cache is untrusted and
    # must not keep stale tags, links or authority with valid file hashes.
    if data != current_index:
        details = _stale_detail(data, current_index)
        suffix = ("\n  " + "\n  ".join(details)) if details else ""
        raise IndexErrorInfo(
            "index_stale: project knowledge added/removed/modified; run 'index'" + suffix
        )
    errors = _validate(root, current, external_ids=external_ids)
    if errors:
        raise IndexErrorInfo("\n".join(errors))
    return data


def _pathmatch(query_path, pattern):
    # Pure git-style directory glob suffix. Keep matching simple and conservative.
    pat = pattern.replace("**/", "*")
    return fnmatch.fnmatchcase(query_path, pat) or (pattern.endswith("/**") and query_path.startswith(pattern[:-3] + "/"))


def _terms(words):
    return [w.lower() for w in re.split(r"[^\w-]+", words or "") if w]


def _technique_score(row, query):
    if row["kind"] != "technique" or not query:
        return 0
    terms = set(_terms(query))
    signals = row.get("problem_signals", [])
    phrases = sum(8 for phrase in signals if
                  (normalized := " ".join(_terms(phrase))) and
                  normalized in " ".join(_terms(query)))
    return (phrases + 4 * len(terms & set(_terms(" ".join(signals)))) +
            3 * len(terms & set(_terms(" ".join(row["tags"])))) +
            2 * len(terms & set(_terms(row["summary"]))))


def _compatibility(row, *, engine=None, renderer=None):
    if row["kind"] != "technique" or (not engine and not renderer):
        return "not-checked"
    unknown = False
    for field, requested in (("engine", engine), ("renderer", renderer)):
        if not requested:
            continue
        declared = {x.casefold() for x in row.get(field, [])}
        if not declared or "unknown" in declared:
            unknown = True
        elif requested.casefold() not in declared and "any" not in declared:
            return "incompatible"
    return "unknown" if unknown else "metadata-match"


def _match(row, areas, paths, query, ident):
    reasons = []
    if ident and row["id"] == ident:
        reasons.append("explicit_id")
    if areas and (row["area"] in areas or any(a in row["tags"] for a in areas)):
        reasons.append("area")
    if paths and any(_pathmatch(p, pat) for p in paths for pat in row["paths"]):
        reasons.append("path")
    terms = _terms(query)
    haystack = " ".join([row["summary"], row["area"], row["path"], *row["tags"]]).lower()
    if terms and any(term in haystack for term in terms):
        reasons.append("query")
    if row["kind"] == "technique" and _technique_score(row, query) and "query" not in reasons:
        reasons.append("problem_signal")
    return reasons


def _result(row, reasons, *, engine=None, renderer=None):
    item = {"id": row["id"], "kind": row["kind"], "status": row["status"],
            "path": row["path"], "summary": row["summary"], "area": row["area"],
            "reasons": reasons}
    if row["kind"] == "technique":
        item["compatibility"] = _compatibility(row, engine=engine, renderer=renderer)
    return item


def route(index, *, area=None, paths=(), query=None, ident=None, engine=None, renderer=None):
    """Broad entrypoints only. Agent chooses subsequent hop; no forced traversal."""
    areas = set(area or [])
    possible_areas = []
    for name, metadata in index["areas"].items():
        why = []
        if name in areas:
            why.append("explicit_area")
        if any(_pathmatch(p, pattern) for p in paths for pattern in metadata["entrypoints"]):
            why.append("area_entrypoint_path")
        if why:
            possible_areas.append({"area": name, "summary": metadata["summary"], "reasons": why})
            areas.add(name)
    required = []
    suggested = []
    for row in index["entries"]:
        if row["status"] in INACTIVE:
            continue
        if _compatibility(row, engine=engine, renderer=renderer) == "incompatible" and ident != row["id"]:
            continue
        reasons = _match(row, areas, paths, query, ident)
        if not reasons:
            continue
        destination = required if row["kind"] == "spec" and row["status"] == "accepted" else suggested
        destination.append(_result(row, reasons, engine=engine, renderer=renderer))
    # No hard top-k cap on binding specs. For other results, return a small shelf;
    # agent can follow a single link or ask for deeper lookup as needed.
    scores = {row["id"]: _technique_score(row, query) for row in index["entries"]}
    suggested.sort(key=lambda x: (-int("explicit_id" in x["reasons"]), -int("path" in x["reasons"]),
                                  -int("area" in x["reasons"]), -scores[x["id"]], x["id"]))
    result = {"mode": "progressive", "areas": possible_areas, "required": required,
              "suggested": suggested[:5], "more_suggestions": max(0, len(suggested) - 5),
              "warning": None}
    if not required and not suggested:
        result["warning"] = "no_match: inspect source/code or broaden query; an index miss does not prove absence"
    return result


def hop(index, from_id, *, include_inactive=False, limit=10, offset=0):
    by_id = {r["id"]: r for r in index["entries"]}
    if from_id in index["areas"]:
        # area index acts as a shallow shelf; another call can hop from a record.
        records = [by_id[ident] for ident in index["areas"][from_id]["ids"]]
        items = [_result(row, ["area_shelf"]) for row in records if include_inactive or row["status"] not in INACTIVE]
        return {"from": from_id, "type": "area", "total": len(items), "offset": offset, "items": items[offset:offset + limit]}
    if from_id not in by_id:
        raise IndexErrorInfo(f"unknown id/area: {from_id}")
    out = []
    for edge in by_id[from_id]["links"]:
        item = by_id[edge["target"]]
        if include_inactive or item["status"] not in INACTIVE:
            out.append(_result(item, [edge["relation"] + " from " + from_id]))
    for row in index["entries"]:
        if row["id"] == from_id:
            continue
        for edge in row["links"]:
            if edge["target"] == from_id and (include_inactive or row["status"] not in INACTIVE):
                out.append(_result(row, ["incoming " + edge["relation"]]))
    unique = {item["id"]: item for item in out}
    items = list(unique.values())
    return {"from": from_id, "type": "record", "total": len(items), "offset": offset, "items": items[offset:offset + limit]}


def lookup(index, *, area=None, kind=None, query=None, limit=3, include_inactive=False, ident=None, engine=None, renderer=None):
    records = []
    for row in index["entries"]:
        if not include_inactive and row["status"] in INACTIVE:
            continue
        if ident and ident != row["id"]:
            continue
        if area and area != row["area"] and area not in row["tags"]:
            continue
        if kind and kind != row["kind"]:
            continue
        if _compatibility(row, engine=engine, renderer=renderer) == "incompatible" and ident != row["id"]:
            continue
        if query and not _match(row, set(), [], query, None):
            continue
        records.append((row, _result(row, ["lookup"], engine=engine, renderer=renderer)))
    if query and any(row["kind"] == "technique" for row, _ in records):
        records.sort(key=lambda pair: (-_technique_score(pair[0], query), pair[0]["id"]))
    return [item for _, item in records[:max(0, limit)]]


def _scoped_result(row, scope, reasons, *, engine=None, renderer=None):
    item = _result(row, reasons, engine=engine, renderer=renderer)
    item["scope"] = scope
    item["scoped_id"] = scope + ":" + row["id"]
    return item


def _resolve_scoped(index, global_index, identifier, *, default_scope="project"):
    if identifier.startswith("global:"):
        return "global", identifier[7:], global_index
    if identifier.startswith("project:"):
        return "project", identifier[8:], index
    if default_scope == "global":
        return "global", identifier, global_index
    return "project", identifier, index


def scoped_hop(index, global_index, identifier, *, limit=10, offset=0, include_inactive=False):
    """One edge per call, including explicit cross-scope links."""
    scope, ident, selected = _resolve_scoped(index, global_index, identifier)
    if selected is None:
        raise IndexErrorInfo("global catalog is not configured")
    by_id = {row["id"]: row for row in selected["entries"]}
    if ident not in by_id and ident not in selected["areas"]:
        raise IndexErrorInfo(f"unknown scoped id: {identifier}")
    if ident in selected["areas"]:
        result = hop(selected, ident, limit=limit, offset=offset, include_inactive=include_inactive)
        result["items"] = [{**item, "scope": scope, "scoped_id": scope + ":" + item["id"]}
                           for item in result["items"]]
        return result
    edges = []
    origin = by_id[ident]
    for edge in origin["links"]:
        target_scope, target_id, target_index = _resolve_scoped(index, global_index, edge["target"], default_scope=scope)
        if target_index is None:
            raise IndexErrorInfo("global catalog is not configured")
        target = next((row for row in target_index["entries"] if row["id"] == target_id), None)
        if target is None:
            raise IndexErrorInfo(f"broken scoped link: {edge['target']}")
        if include_inactive or target["status"] not in INACTIVE:
            edges.append(_scoped_result(target, target_scope, [edge["relation"] + " from " + identifier]))
    # Also include local records linking to a global record. Each returned record
    # is an immediate neighbor only; no automatic second hop is performed.
    sources = [(scope, selected)]
    if scope == "global":
        sources.append(("project", index))
    for source_scope, source_index in sources:
        for row in source_index["entries"]:
            if source_scope == scope and row["id"] == ident:
                continue
            for edge in row["links"]:
                target_scope, target_id, _ = _resolve_scoped(
                    index, global_index, edge["target"], default_scope=source_scope)
                if target_scope == scope and target_id == ident:
                    if include_inactive or row["status"] not in INACTIVE:
                        edges.append(_scoped_result(
                            row, source_scope, ["incoming " + edge["relation"]]))
    unique = {item["scoped_id"]: item for item in edges}
    items = list(unique.values())
    return {"from": identifier, "type": "record", "total": len(items),
            "offset": offset, "items": items[offset:offset + limit]}


def scoped_route(index, global_index, *, area=None, paths=(), query=None, ident=None,
                 engine=None, renderer=None):
    """Project-first results; globally sourced techniques only fill a local gap."""
    local = route(index, area=area, paths=paths, query=query, ident=ident,
                  engine=engine, renderer=renderer)
    local["suggested"] = [{**item, "scope": "project", "scoped_id": "project:" + item["id"]}
                          for item in local["suggested"]]
    local["required"] = [{**item, "scope": "project", "scoped_id": "project:" + item["id"]}
                         for item in local["required"]]
    local["fallback_used"] = False
    if global_index is None or (not query and not ident):
        return local
    # Area-only shelves do not establish relevance to the user problem.
    suitable = any(
        item["kind"] == "technique" and
        (not query or "query" in item["reasons"] or "problem_signal" in item["reasons"]
         or "explicit_id" in item["reasons"]) and
        item.get("compatibility") != "incompatible"
        for item in local["suggested"])
    if suitable:
        return local
    shelf = lookup(global_index, kind="technique", query=query,
                   engine=engine, renderer=renderer, limit=5)
    local["suggested"].extend({**item, "scope": "global",
                                "scoped_id": "global:" + item["id"]} for item in shelf)
    local["fallback_used"] = bool(shelf)
    if shelf and local["warning"]:
        local["warning"] = None
    return local


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--global-catalog", type=Path, help="Explicit catalog root with index.json and recipes/")
    commands = parser.add_subparsers(dest="cmd", required=True)
    for name in ("init", "index", "check", "areas", "global-index", "global-check"):
        commands.add_parser(name)
    browse = commands.add_parser("route")
    browse.add_argument("--area", action="append")
    browse.add_argument("--path", action="append", default=[])
    browse.add_argument("--query")
    browse.add_argument("--id")
    browse.add_argument("--engine")
    browse.add_argument("--renderer")
    browse.add_argument("query_words", nargs="*", metavar="QUERY",
                        help="Query text; equivalent to --query")
    browse.add_argument("--why", action="store_true", help="Reasons are always included in JSON output")
    follow = commands.add_parser("hop")
    follow.add_argument("--from", dest="from_id", required=True)
    follow.add_argument("--include-inactive", action="store_true")
    follow.add_argument("--limit", type=int, default=10)
    follow.add_argument("--offset", type=int, default=0)
    look = commands.add_parser("lookup")
    look.add_argument("--area")
    look.add_argument("--kind", choices=list(KINDS.values()))
    look.add_argument("--query")
    look.add_argument("--engine")
    look.add_argument("--renderer")
    look.add_argument("--id", dest="ident")
    look.add_argument("id_positional", nargs="?", metavar="ID",
                      help="Record id; equivalent to --id")
    look.add_argument("--limit", type=int, default=3)
    look.add_argument("--digest", action="store_true")
    look.add_argument("--include-superseded", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.cmd == "init":
            if (root / ".combo").exists() and (root / ".combo" / "index.json").exists():
                raise IndexErrorInfo(".combo already exists; run index for an explicit migration")
            for directory in KINDS:
                (root / ".combo" / directory).mkdir(parents=True, exist_ok=True)
            print("initialized .combo (run 'index' to generate metadata)")
            return 0
        if args.cmd == "index":
            if not (root / ".combo").exists():
                raise IndexErrorInfo(".combo does not exist; run 'init' explicitly")
            external_ids = ()
            if args.global_catalog is not None:
                catalog = load_index(args.global_catalog, global_catalog=True)
                external_ids = {"global:" + row["id"] for row in catalog["entries"]}
            data = rebuild(root, external_ids=external_ids)
            print(f"indexed {len(data['entries'])} entries in {len(data['areas'])} areas")
            return 0
        if args.cmd in ("global-index", "global-check"):
            if args.global_catalog is None:
                raise IndexErrorInfo("--global-catalog is required")
            if args.cmd == "global-index":
                result = rebuild(args.global_catalog, global_catalog=True)
                print(f"indexed {len(result['entries'])} global techniques")
            else:
                result = load_index(args.global_catalog, global_catalog=True)
                print(f"OK: global catalog has {len(result['entries'])} techniques")
            return 0
        global_index = None
        if args.global_catalog is not None:
            global_index = load_index(args.global_catalog, global_catalog=True)
            external_ids = {"global:" + row["id"] for row in global_index["entries"]}
            index = load_index(root, external_ids=external_ids)
        else:
            index = load_index(root)
        if args.cmd == "check":
            print(f"OK: index schema {SCHEMA}, {len(index['entries'])} entries, {len(index['areas'])} areas")
            return 0
        if args.cmd == "areas":
            output = index["areas"]
        elif args.cmd == "route":
            if args.query and args.query_words:
                parser.error("route accepts either --query or positional query words, not both")
            query = args.query or (" ".join(args.query_words) or None)
            output = (scoped_route(index, global_index, area=args.area, paths=args.path,
                                   query=query, ident=args.id, engine=args.engine,
                                   renderer=args.renderer) if global_index is not None else
                      route(index, area=args.area, paths=args.path, query=query, ident=args.id,
                            engine=args.engine, renderer=args.renderer))
        elif args.cmd == "hop":
            output = (scoped_hop(index, global_index, args.from_id,
                                 include_inactive=args.include_inactive,
                                 limit=max(0, args.limit), offset=max(0, args.offset))
                      if global_index is not None else
                      hop(index, args.from_id, include_inactive=args.include_inactive,
                          limit=max(0, args.limit), offset=max(0, args.offset)))
        elif args.cmd == "lookup":
            if args.ident and args.id_positional:
                parser.error("lookup accepts either --id or a positional ID, not both")
            output = lookup(index, area=args.area, kind=args.kind, query=args.query,
                            limit=args.limit, include_inactive=args.include_superseded,
                            ident=args.ident or args.id_positional, engine=args.engine,
                            renderer=args.renderer)
            if args.digest:
                output = [{**item, "digest": next((x["summary"] for x in index["entries"] if x["id"] == item["id"]), "")} for item in output]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (IndexErrorInfo, OSError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
