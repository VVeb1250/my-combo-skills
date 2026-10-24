"""Install the self-contained Combo package with bounded, drift-aware rollback."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
REAL_HOME = Path.home()

# The manifest is the source of truth for the active package set.  Keep the
# accepted surface deliberately narrow: a package is either ``combo`` or a
# lower-case, hyphen-separated ``combo-*`` sibling, and it installs at the
# exact same path under ``skills/``.  This prevents a stale ownership index (or
# a typo in a manifest) from turning the installer into an arbitrary file
# copier.
PACKAGE_NAME_RE = re.compile(r"^combo(?:-[a-z0-9]+)*$")
PACKAGE_PREFIX = "skills/"
ADAPTER_TARGET = "agents/combo-worker.toml"
OWNERSHIP_INDEX = "skills/combo/.combo-owned.json"

# BEGIN/END are kept as compatibility aliases for callers of the v0 helper.
BEGIN = "# BEGIN COMBO SKILL OVERRIDES"
END = "# END COMBO SKILL OVERRIDES"
CONFIG_BEGIN = "# BEGIN COMBO CONFIG"
CONFIG_END = "# END COMBO CONFIG"
AGENTS_BEGIN = "<!-- BEGIN COMBO -->"
AGENTS_END = "<!-- END COMBO -->"


def digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def existing(path: Path) -> bytes | None:
    path = Path(path)
    return path.read_bytes() if path.exists() else None


def remap(path: Path, home: Path) -> Path:
    """Remap an absolute path from the real user home to a fake test home."""
    path = Path(path)
    try:
        return home / path.relative_to(REAL_HOME)
    except ValueError:
        return path


CACHE_DIRECTORY = "__pycache__"
CACHE_SUFFIXES = frozenset({".pyc", ".pyo"})


def is_installable_source(path: Path) -> bool:
    """Generated Python caches are runtime state, never package content."""

    path = Path(path)
    return (
        path.name != CACHE_DIRECTORY
        and path.suffix.lower() not in CACHE_SUFFIXES
    )


def _load_manifest() -> dict:
    path = ROOT / "install-manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _relative_manifest_path(value: object, label: str) -> str:
    """Return a canonical repository-relative POSIX path.

    Manifest paths are consumed on Windows and POSIX hosts.  Reject alternate
    spellings instead of normalising them, so source/target mappings and
    ownership rows have one unambiguous representation.
    """
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty relative path")
    if "\\" in value:
        raise ValueError(f"{label} must use POSIX separators: {value}")
    path = Path(value)
    if (
        path.is_absolute()
        or value.startswith("/")
        or ".." in path.parts
        or "." in path.parts
    ):
        raise ValueError(f"{label} escapes the repository: {value}")
    canonical = path.as_posix()
    if canonical != value:
        raise ValueError(f"{label} is not canonical: {value}")
    return canonical


def _manifest_package_roots(manifest: dict) -> dict[str, str]:
    """Validate and return ``{package_name: source/target root}``.

    ``source_roots`` intentionally has no remapping mode.  A package source
    named ``skills/combo-x`` must install at ``skills/combo-x`` exactly.  This
    keeps the ownership index bounded even when it was produced by an older or
    hand-edited manifest.
    """
    entries = manifest.get("source_roots")
    if not isinstance(entries, list) or not entries:
        raise ValueError("install manifest must declare source_roots")
    roots: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            source, target = entry, entry
        elif isinstance(entry, dict):
            source = entry.get("source")
            if "target" not in entry:
                raise ValueError(f"source_roots[{index}].target is required")
            target = entry.get("target")
        else:
            raise TypeError(f"source_roots[{index}] must be an object or path")
        source = _relative_manifest_path(source, f"source_roots[{index}].source")
        target = _relative_manifest_path(target, f"source_roots[{index}].target")
        if source != target:
            raise ValueError(
                f"source_roots[{index}] must map source and target exactly: {source} -> {target}"
            )
        if not source.startswith(PACKAGE_PREFIX):
            raise ValueError(f"source_roots[{index}] must be under skills/: {source}")
        name = source[len(PACKAGE_PREFIX) :]
        if "/" in name or not PACKAGE_NAME_RE.fullmatch(name):
            raise ValueError(f"invalid Combo package name: {name!r}")
        if name in roots:
            raise ValueError(f"duplicate Combo package root: {name}")
        roots[name] = source
    if "combo" not in roots:
        raise ValueError("source_roots must include the combo package")
    return roots


def manifest_package_names(manifest: dict | None = None) -> set[str]:
    """Return the validated package names declared by the install manifest."""
    return set(_manifest_package_roots(manifest or _load_manifest()))


def _manifest_owned_prefixes(manifest: dict) -> tuple[str, ...]:
    roots = _manifest_package_roots(manifest)
    return tuple(f"{root}/" for root in roots.values())


def _manifest_owned_relative(path: str, manifest: dict) -> bool:
    """Whether an ownership row names a package file or the worker role."""
    if path == _manifest_ownership_index(manifest):
        return False
    if path == ADAPTER_TARGET:
        return True
    return any(path.startswith(prefix) for prefix in _manifest_owned_prefixes(manifest))


def _manifest_ownership_index(manifest: dict) -> str:
    raw = manifest.get("ownership_index", OWNERSHIP_INDEX)
    value = _relative_manifest_path(raw, "ownership_index")
    if value != OWNERSHIP_INDEX:
        raise ValueError(f"ownership_index must be {OWNERSHIP_INDEX}: {value}")
    return value


def _manifest_disable_paths(manifest: dict, home: Path) -> list[Path]:
    """Return declared local skill paths, supporting the v1 manifest shape."""
    values: list[Path] = []

    def add(raw: object) -> None:
        if not isinstance(raw, str) or not raw:
            return
        path = Path(raw)
        if path.is_absolute():
            # Legacy rows recorded the real home as an absolute path.  Keep
            # that migration path, while refusing an arbitrary filesystem
            # target from a new manifest.
            try:
                path.relative_to(REAL_HOME)
            except ValueError as exc:
                raise ValueError(f"disable path escapes the user home: {raw}") from exc
            path = remap(path, home)
        else:
            canonical = _relative_manifest_path(raw, "disable_local path")
            if not (
                canonical.startswith((".agents/", ".codex/"))
            ):
                raise ValueError(
                    f"disable path must be under .agents/ or .codex/: {raw}"
                )
            path = home / canonical
        values.append(path)

    for entry in manifest.get("disable_local", []):
        raw = entry.get("path") if isinstance(entry, dict) else entry
        add(raw)

    # Read old manifests in tests and during a one-time v0 migration.
    for row in manifest.get("rows", []):
        if row.get("mechanism") != "disable-local" or not row.get("path"):
            continue
        add(row["path"])

    seen: set[str] = set()
    result: list[Path] = []
    for path in values:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def _config_markers(manifest: dict) -> tuple[str, str]:
    markers = manifest.get("config", {}).get("markers", {})
    return markers.get("begin", CONFIG_BEGIN), markers.get("end", CONFIG_END)


def _agents_markers(manifest: dict) -> tuple[str, str]:
    markers = manifest.get("agents", {}).get("markers", {})
    return markers.get("begin", AGENTS_BEGIN), markers.get("end", AGENTS_END)


def _remove_marked_block(text: str, begin: str, end: str) -> str:
    begin_count = text.count(begin)
    end_count = text.count(end)
    if begin_count != end_count:
        raise ValueError(f"Unbalanced owned marker: {begin}")
    if begin_count > 1:
        raise ValueError(f"Duplicate owned marker: {begin}")
    if not begin_count:
        return text
    start = text.index(begin)
    finish = text.index(end, start) + len(end)
    return text[:start] + text[finish:]


def _strip_config_blocks(text: str, manifest: dict) -> str:
    # The second pair is the v0 marker. It is removed only as an explicitly
    # owned block, never by searching for an unbounded section heading.
    begin, end = _config_markers(manifest)
    text = _remove_marked_block(text, begin, end)
    return _remove_marked_block(text, BEGIN, END)


def _plugin_body_pattern(plugin: str) -> re.Pattern[str]:
    quoted = rf"(?:\"{re.escape(plugin)}\"|'" + re.escape(plugin) + r"')"
    header = rf"^\[plugins\.{quoted}\][ \t]*\r?$"
    return re.compile(header + r"\n(?P<body>[\s\S]*?)(?=^\[|\Z)", re.MULTILINE)


def _disable_plugin(text: str, plugin: str, before: dict) -> str:
    if plugin not in before.get("plugins", {}):
        return text
    match = _plugin_body_pattern(plugin).search(text)
    if not match:
        raise ValueError(f"Cannot safely locate plugin table: {plugin}")
    body = match.group("body")
    replacement, count = re.subn(
        r"^(?P<prefix>[ \t]*)enabled[ \t]*=[ \t]*(?:true|false)(?P<tail>[ \t]*(?:#.*)?)(?=\r?$)",
        r"\g<prefix>enabled = false\g<tail>",
        body,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"Cannot safely edit enabled field: {plugin}")
    return text[: match.start("body")] + replacement + text[match.end("body") :]


def _set_nested(mapping: dict, section: str, key: str, value: object) -> None:
    mapping.setdefault(section, {})[key] = value


def render_config(raw: bytes, manifest: dict, home: Path) -> bytes:
    """Render only owned config blocks while preserving every other TOML value."""
    text = raw.decode("utf-8-sig")
    before = tomllib.loads(text)
    text = _strip_config_blocks(text, manifest)
    stripped = tomllib.loads(text)

    plugins = manifest.get("config", {}).get("disable_plugins")
    if plugins is None:
        plugins = manifest.get("disable_plugins", [])
    for plugin in plugins:
        text = _disable_plugin(text, plugin, before)

    stripped = tomllib.loads(text)
    unmanaged = stripped.get("skills", {}).get("config", [])
    unmanaged_paths = {
        str(Path(row["path"])).lower()
        for row in unmanaged
        if isinstance(row, dict) and row.get("path")
    }
    disabled = sorted(
        {str(path) for path in _manifest_disable_paths(manifest, home)},
        key=str.lower,
    )
    if any(path.lower() in unmanaged_paths for path in disabled):
        raise ValueError(
            "A targeted skill has an unmanaged override; reconcile it before applying."
        )

    role = _manifest_worker_role(manifest)
    if role and role["name"] in stripped.get("agents", {}):
        raise ValueError(f"An unmanaged agent role already exists: {role['name']}")

    begin, end = _config_markers(manifest)
    block = [begin]
    if role:
        block += [
            f"[agents.{role['name']}]",
            f"config_file = {json.dumps(role['config_file'])}",
            f"description = {json.dumps(role['description'])}",
            "",
        ]
    for path in disabled:
        block += [
            "[[skills.config]]",
            f"path = {json.dumps(path)}",
            "enabled = false",
            "",
        ]
    block.append(end)
    rendered = text.rstrip() + "\n\n" + "\n".join(block) + "\n"
    after = tomllib.loads(rendered)

    expected = copy.deepcopy(stripped)
    for plugin in plugins:
        if plugin in expected.get("plugins", {}):
            expected["plugins"][plugin]["enabled"] = False
    if role:
        _set_nested(
            expected,
            "agents",
            role["name"],
            {
                "config_file": role["config_file"],
                "description": role["description"],
            },
        )
    expected.pop("skills", None)
    after.pop("skills", None)
    if expected != after:
        raise ValueError("Rendering changed unrelated configuration")
    return rendered.encode("utf-8")


def _combo_global_block(manifest: dict | None = None) -> str:
    policy_path = ROOT / "POLICY.md"
    policy = (
        policy_path.read_text(encoding="utf-8").strip() if policy_path.exists() else ""
    )
    manifest = manifest or _load_manifest()
    architecture = manifest.get("architecture", {})
    pointer = manifest.get("global_pointer")
    if pointer is None and isinstance(architecture, dict):
        pointer = architecture.get("global_pointer")
    if pointer is None:
        pointer = (
            "Use discovered Combo entries for their described tasks; shared "
            "workflows and references remain in combo."
        )
    if not isinstance(pointer, str) or not pointer.strip():
        raise ValueError("manifest global_pointer must be a non-empty string")
    parts = [policy] if policy else []
    parts.append(
        (ROOT / "skills/combo/practices/project-knowledge-rule.md")
        .read_text(encoding="utf-8")
        .strip()
    )
    parts.append(pointer.strip())
    return "\n\n".join(parts)


def render_agents(raw: bytes, manifest: dict | None = None) -> bytes:
    """Replace one owned pointer block, preserving all other instructions."""
    manifest = manifest or {
        "agents": {"markers": {"begin": AGENTS_BEGIN, "end": AGENTS_END}}
    }
    begin, end = _agents_markers(manifest)
    text = raw.decode("utf-8-sig")
    block = f"{begin}\n{_combo_global_block(manifest)}\n{end}"
    begin_count, end_count = text.count(begin), text.count(end)
    if begin_count != end_count:
        raise ValueError("Unbalanced Combo AGENTS markers")
    if begin_count > 1:
        raise ValueError("Duplicate Combo AGENTS markers")
    if begin_count:
        start = text.index(begin)
        finish = text.index(end, start) + len(end)
        prefix, suffix = text[:start].rstrip(), text[finish:].lstrip("\r\n")
        rendered = prefix + "\n\n" + block
        if suffix:
            rendered += "\n\n" + suffix
    else:
        memory = text.find("## Memory:")
        if memory < 0:
            prefix, suffix = text.rstrip(), ""
        else:
            prefix, suffix = text[:memory].rstrip(), text[memory:].lstrip("\r\n")
        rendered = prefix + ("\n\n" if prefix else "") + block
        if suffix:
            rendered += "\n\n" + suffix
    return (rendered.rstrip() + "\n").encode("utf-8")


def _codex_root(home: Path) -> Path:
    return (home / ".codex").resolve()


def _is_link(path: Path) -> bool:
    junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(junction and junction())


def _assert_target(path: Path, home: Path) -> None:
    codex = Path(home) / ".codex"
    if _is_link(codex):
        raise ValueError(f"Codex directory cannot be a symlink: {codex}")
    root = codex.resolve(strict=False)
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError(f"Target escapes intended Codex directory: {path}")
    current = path
    # Walk the lexical path, bounded by its anchor. Comparing to ``root`` is
    # unsafe when the root itself is a junction or symlink.
    while True:
        if current.exists() and _is_link(current):
            raise ValueError(f"Symlink target is not owned safely: {path}")
        if current == codex or current.parent == current:
            break
        current = current.parent


def _read_owned_index(
    path: Path, home: Path, manifest: dict | None = None
) -> dict[str, str]:
    if not path.exists():
        return {}
    manifest = manifest or _load_manifest()
    _manifest_package_roots(manifest)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["files"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid Combo ownership index: {path}") from exc
    if not isinstance(rows, list):
        raise TypeError(f"Invalid Combo ownership index: {path}")
    result: dict[str, str] = {}
    root = _codex_root(home)
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise TypeError(f"Invalid owned row in index: {path}")
        raw = row["path"]
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
            raise ValueError(f"Invalid owned relative path: {relative}")
        canonical = relative.as_posix()
        if canonical != raw or not _manifest_owned_relative(canonical, manifest):
            raise ValueError(f"Owned index contains an out-of-scope path: {relative}")
        target = root / relative
        _assert_target(target, home)
        if canonical in result:
            raise ValueError(f"Duplicate owned path in index: {relative}")
        checksum = row.get("sha256")
        if not isinstance(checksum, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", checksum
        ):
            raise ValueError(f"Invalid owned checksum in index: {relative}")
        result[canonical] = checksum.lower()
    return result


def _ownership_bytes(files: dict[Path, bytes], home: Path, manifest: dict) -> bytes:
    root = _codex_root(home)
    allowed = (*_manifest_owned_prefixes(manifest), ADAPTER_TARGET)
    rows = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": digest(data),
            "bytes": len(data),
        }
        for path, data in sorted(files.items(), key=lambda item: str(item[0]).lower())
        if data is not None
        and (
            path.relative_to(root).as_posix() == ADAPTER_TARGET
            or any(
                path.relative_to(root).as_posix().startswith(prefix)
                for prefix in allowed
                if prefix.endswith("/")
            )
        )
    ]
    return (
        json.dumps(
            {"version": manifest.get("version", 2), "package": "combo", "files": rows},
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _manifest_adapters(manifest: dict) -> list[dict]:
    entries = manifest.get("adapter_files", [])
    if not isinstance(entries, list):
        raise TypeError("adapter_files must be a list")
    result = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise TypeError(f"adapter_files[{index}] must be an object")
        source = _relative_manifest_path(
            entry.get("source"), f"adapter_files[{index}].source"
        )
        target = _relative_manifest_path(
            entry.get("target"), f"adapter_files[{index}].target"
        )
        if target != ADAPTER_TARGET:
            raise ValueError(
                f"adapter_files[{index}] target must be {ADAPTER_TARGET}: {target}"
            )
        if source in {"", "."} or not source.startswith("adapters/"):
            raise ValueError(
                f"adapter_files[{index}] source must be under adapters/: {source}"
            )
        result.append({"source": source, "target": target})
    if len(result) > 1:
        raise ValueError("only the combo-worker.toml adapter role may be declared")
    return result


def _manifest_worker_role(manifest: dict) -> dict | None:
    role = manifest.get("config", {}).get("worker_role")
    if role is None:
        return None
    if not isinstance(role, dict):
        raise TypeError("config.worker_role must be an object")
    if role.get("name") != "combo_worker":
        raise ValueError("only the combo_worker role may be declared")
    if role.get("config_file") != ADAPTER_TARGET:
        raise ValueError(
            f"worker role config_file must be {ADAPTER_TARGET}: {role.get('config_file')}"
        )
    if not isinstance(role.get("description"), str) or not role["description"].strip():
        raise ValueError("worker role description must be a non-empty string")
    return role


def build_plan(home: Path, manifest: dict | None = None) -> list[dict]:
    manifest = manifest or _load_manifest()
    package_roots = _manifest_package_roots(manifest)
    home = Path(home).resolve()
    root = _codex_root(home)
    target_bytes: dict[Path, bytes | None] = {}

    for source_rel in package_roots.values():
        source = source_rel
        target_root = source_rel
        source_root = ROOT / source
        if not source_root.is_dir() or source_root.is_symlink():
            raise ValueError(f"Missing package source directory: {source_root}")
        for source_file in sorted(source_root.rglob("*")):
            relative = source_file.relative_to(source_root)
            if not source_file.is_file() or not is_installable_source(relative):
                continue
            if source_file.is_symlink() or source_file.name == ".combo-owned.json":
                if source_file.is_symlink():
                    raise ValueError(f"Symlink in package source: {source_file}")
                continue
            target = root / target_root / relative
            _assert_target(target, home)
            if target in target_bytes:
                raise ValueError(f"Duplicate package target: {target}")
            target_bytes[target] = source_file.read_bytes()

    for entry in _manifest_adapters(manifest):
        source = ROOT / entry["source"]
        if (
            not source.resolve(strict=False).is_relative_to(ROOT)
            or not source.is_file()
            or source.is_symlink()
        ):
            raise ValueError(f"Missing or unsafe adapter source: {source}")
        target = root / entry["target"]
        _assert_target(target, home)
        if target in target_bytes:
            raise ValueError(f"Duplicate package target: {target}")
        target_bytes[target] = source.read_bytes()

    config = root / "config.toml"
    config_raw = existing(config)
    if config_raw is None:
        raise ValueError(f"Missing Codex config: {config}")
    target_bytes[config] = render_config(config_raw, manifest, home)

    agents = root / "AGENTS.md"
    target_bytes[agents] = render_agents(existing(agents) or b"", manifest)

    index = root / _manifest_ownership_index(manifest)
    _assert_target(index, home)
    previous = _read_owned_index(index, home, manifest)
    desired = {
        path.relative_to(root).as_posix(): digest(data)
        for path, data in target_bytes.items()
        if data is not None
    }
    for relative, expected_hash in previous.items():
        if relative in desired:
            continue
        stale = root / relative
        current = existing(stale)
        if current is None:
            continue
        if digest(current) != expected_hash:
            raise ValueError(
                f"Owned package file drifted; refusing stale removal: {stale}"
            )
        _assert_target(stale, home)
        target_bytes[stale] = None

    target_bytes[index] = _ownership_bytes(
        {path: data for path, data in target_bytes.items() if data is not None},
        home,
        manifest,
    )

    changes: list[dict] = []
    for path, after in sorted(
        target_bytes.items(), key=lambda item: str(item[0]).lower()
    ):
        _assert_target(path, home)
        before = existing(path)
        if before != after:
            changes.append({"path": path, "before": before, "after": after})
    return changes


def summarize(changes: list[dict]) -> list[dict]:
    result = []
    for change in changes:
        before, after = change.get("before"), change.get("after")
        result.append(
            {
                "path": str(change["path"]),
                "action": "delete" if after is None else "write",
                "before_sha256": digest(before),
                "after_sha256": digest(after),
                "bytes_before": len(before) if before is not None else None,
                "bytes_after": len(after) if after is not None else None,
            }
        )
    return result


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if _is_link(path.parent) or _is_link(path):
        raise ValueError(f"Refusing symlink write: {path}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.combo-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def _safe_delete(path: Path) -> None:
    if _is_link(path):
        raise ValueError(f"Refusing symlink deletion: {path}")
    if path.exists():
        if not path.is_file():
            raise ValueError(f"Refusing non-file deletion: {path}")
        path.unlink()


def _validate_change(path: Path, target_root: Path | None) -> None:
    if target_root is not None:
        target = Path(target_root)
        if _is_link(target):
            raise ValueError(f"Target root cannot be a symlink: {target}")
        root = target.resolve(strict=False)
        if not path.resolve(strict=False).is_relative_to(root):
            raise ValueError(f"Change escapes target root: {path}")
        current = path
        while True:
            if current.exists() and _is_link(current):
                raise ValueError(f"Symlink path is not owned safely: {path}")
            if current == target or current.parent == current:
                break
            current = current.parent
    if _is_link(path):
        raise ValueError(f"Symlink path is not owned safely: {path}")


def _receipt_write(path: Path, receipt: dict) -> None:
    _atomic_write(path, (json.dumps(receipt, indent=2) + "\n").encode("utf-8"))


def apply(
    changes: list[dict], backup_root: Path, target_root: Path | None = None
) -> Path | None:
    if not changes:
        return None
    changes = [
        {
            "path": Path(change["path"]),
            "before": change.get("before"),
            "after": change.get("after"),
        }
        for change in changes
    ]
    target_root = Path(target_root).resolve() if target_root is not None else None
    for change in changes:
        _validate_change(change["path"], target_root)
        if existing(change["path"]) != change["before"]:
            raise ValueError(f"Concurrent change: {change['path']}")

    backup_root = Path(backup_root)
    backup_root.mkdir(parents=True, exist_ok=False)
    files = []
    for index, change in enumerate(changes):
        before = change["before"]
        backup = f"{index:03}.bin" if before is not None else None
        if backup:
            if before is None:
                raise ValueError("Internal backup state error")
            (backup_root / backup).write_bytes(before)
        files.append({**summarize([change])[0], "backup": backup, "done": False})
    receipt_file = backup_root / "receipt.json"
    receipt = {
        "schema": 2,
        "status": "prepared",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_root": str(target_root) if target_root is not None else None,
        "files": files,
    }
    _receipt_write(receipt_file, receipt)

    receipt["status"] = "applying"
    _receipt_write(receipt_file, receipt)
    try:
        for change, row in zip(changes, receipt["files"]):
            path = change["path"]
            _validate_change(path, target_root)
            if existing(path) != change["before"]:
                raise ValueError(f"Concurrent change: {path}")
            if change["after"] is None:
                _safe_delete(path)
            else:
                _atomic_write(path, change["after"])
            if digest(existing(path)) != row["after_sha256"]:
                raise ValueError(f"Post-write verification failed: {path}")
            row["done"] = True
            _receipt_write(receipt_file, receipt)
    except Exception:
        receipt["status"] = "apply_failed"
        _receipt_write(receipt_file, receipt)
        # Atomic writes mean a partial file is not expected. Restore only files
        # whose current bytes are still exactly the bytes this transaction wrote.
        for row in reversed(receipt["files"]):
            path = Path(row["path"])
            if digest(existing(path)) != row["after_sha256"]:
                continue
            if row["backup"]:
                _atomic_write(path, (backup_root / row["backup"]).read_bytes())
            else:
                _safe_delete(path)
        raise
    receipt["status"] = "applied"
    _receipt_write(receipt_file, receipt)
    return receipt_file


def _receipt_backup(receipt_file: Path, name: str) -> Path:
    if not isinstance(name, str):
        raise TypeError("Receipt backup name must be a string")
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Receipt backup escapes its directory: {name}")
    receipt_dir = receipt_file.parent.resolve()
    backup = (receipt_dir / relative).resolve(strict=False)
    if not backup.is_relative_to(receipt_dir):
        raise ValueError(f"Receipt backup escapes its directory: {name}")
    return backup


def rollback(receipt_file: Path, target_root: Path | None = None) -> None:
    receipt_file = Path(receipt_file).resolve()
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    if receipt.get("status") == "rolled_back":
        return
    if receipt.get("status") not in {"applied", "prepared", "applying", "apply_failed"}:
        raise ValueError("Receipt is not a recoverable Combo transaction")
    declared_root = receipt.get("target_root")
    target_root_path = Path(target_root).resolve() if target_root is not None else None
    if target_root_path is not None and declared_root:
        if Path(declared_root).resolve() != target_root_path:
            raise ValueError("Receipt target root does not match the requested home")
    elif target_root_path is None and declared_root:
        target_root_path = Path(declared_root).resolve()

    for row in receipt["files"]:
        path = Path(row["path"])
        _validate_change(path, target_root_path)
        current_hash = digest(existing(path))
        before_hash = row.get("before_sha256")
        after_hash = row.get("after_sha256")
        if receipt.get("status") == "applied":
            if current_hash != after_hash:
                raise ValueError(f"Rollback blocked by later edit: {path}")
        elif current_hash not in {before_hash, after_hash}:
            raise ValueError(f"Rollback blocked by unknown state: {path}")
        backup = row.get("backup")
        if backup:
            backup_path = _receipt_backup(receipt_file, backup)
            if digest(backup_path.read_bytes()) != before_hash:
                raise ValueError(f"Backup integrity failure: {path}")

    for row in reversed(receipt["files"]):
        path = Path(row["path"])
        if digest(existing(path)) == row.get("before_sha256"):
            continue
        if row.get("backup"):
            _atomic_write(
                path, _receipt_backup(receipt_file, row["backup"]).read_bytes()
            )
        else:
            _safe_delete(path)
    receipt["status"] = "rolled_back"
    _receipt_write(receipt_file, receipt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "verify", "rollback"])
    parser.add_argument("--home", type=Path, default=REAL_HOME)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.action == "rollback":
        if not args.receipt:
            parser.error("rollback requires --receipt")
        rollback(args.receipt, args.home.resolve() / ".codex")
        print("Rollback complete")
        return

    subprocess.run(["node", str(ROOT / "scripts/validate-curated.cjs")], check=True)
    home = args.home.resolve()
    changes = build_plan(home)
    if args.action == "plan":
        out = ROOT / "audit" / "v2" / "install-plan.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summarize(changes), indent=2), encoding="utf-8")
        print(f"{len(changes)} changed files, plan: {out}")
    elif args.action == "verify":
        if changes:
            raise SystemExit(
                f"Installed files differ from source: {len(changes)} files"
            )
        print("Installed bytes match source; all non-owned config preserved")
    else:
        stamp = (
            time.strftime("%Y%m%d-%H%M%S", time.gmtime())
            + f"-{time.time_ns() % 1_000_000:06d}"
        )
        destination = ROOT / "backups" / stamp
        receipt = apply(changes, destination, home / ".codex")
        if receipt:
            report = ROOT / "audit" / "v2" / "install-receipt.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(
                json.dumps(
                    {"receipt": str(receipt), "files": summarize(changes)},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        print(
            f"Applied {len(changes)} files. Receipt: {receipt}"
            if receipt
            else "Already installed, no changes"
        )


if __name__ == "__main__":
    main()
