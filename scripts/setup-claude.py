"""Install the bounded Combo package into a Claude Code home.

The source package is copied as bytes and Claude-specific files are supplied by
``adapters/claude``.  Transactional writes and rollback deliberately stay in
``scripts/setup.py`` so both host installers use the same receipt semantics.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import posixpath
import re
import time
from collections.abc import Iterable
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REAL_HOME = Path.home().resolve()
CLAUDE_DIR = ".claude"
OWNERSHIP_INDEX = "skills/combo/.combo-owned.json"
AGENT_TARGET = "agents/combo-worker.md"
OVERRIDE_ROOT = "adapters/claude/overrides"
POLICY_SOURCE = "adapters/claude/POLICY.md"
AGENT_SOURCE = "adapters/claude/agents/combo-worker.md"
CLAUDE_FILE = "CLAUDE.md"
SETTINGS_FILE = "settings.json"
CLAUDE_BEGIN = "<!-- BEGIN COMBO -->"
CLAUDE_END = "<!-- END COMBO -->"
PACKAGE_PREFIX = "skills/"
PACKAGE_NAME_RE = re.compile(r"^combo(?:-[a-z0-9]+)*$")
EXPECTED_PACKAGES = (
    "combo",
    "combo-business",
    "combo-content",
    "combo-debug",
    "combo-deliver",
    "combo-investigate",
    "combo-learning",
    "combo-maintain",
    "combo-media",
    "combo-plan",
    "combo-productivity",
    "combo-research",
    "combo-review",
    "combo-verify",
)
DISABLE_PLUGINS = (
    "ecc-hubs@bundle",
    "ecc@ecc",
    "mattpocock-skills@mattpocock",
)
SKILL_OVERRIDES = {"multi-model-orchestrator": "off"}

# This is the exact five-line legacy section owned by this adapter.  Keep the
# value public: preservation tests and a future migration can identify the
# old section without broad text replacement.
LEGACY_OWNED_SECTION = (
    "## Skill discipline\n"
    "Scan available skills before any non-trivial task; read every plausibly relevant\n"
    "SKILL.md before writing code or creating files. Multiple skills may apply.\n"
    "Reading is cheap, skipping is not. Never use recalled knowledge over a skill's contents."
)
legacyownedsection = LEGACY_OWNED_SECTION


def _load_setup_helpers():
    path = Path(__file__).with_name("setup.py")
    spec = importlib.util.spec_from_file_location("combo_setup_helpers", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import transaction helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_helpers = _load_setup_helpers()
digest = _helpers.digest
existing = _helpers.existing


def apply(changes: list[dict], backup_root: Path, target_root: Path | None = None):
    """Use the shared transactional apply implementation."""

    return _helpers.apply(changes, backup_root, target_root)


def rollback(receipt_file: Path, target_root: Path | None = None) -> None:
    """Use the shared transactional rollback implementation."""

    return _helpers.rollback(receipt_file, target_root)


def _relative(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty relative path")
    if "\\" in value or value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"{label} must use a safe POSIX relative path: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or "." in path.parts or ".." in path.parts:
        raise ValueError(f"{label} escapes its allowed root: {value}")
    canonical = path.as_posix()
    if canonical != value:
        raise ValueError(f"{label} is not canonical: {value}")
    return canonical


def _manifest_path(manifest: dict, key: str, default: str) -> str:
    value = manifest.get(key, default)
    value = _relative(value, key)
    if value != default:
        raise ValueError(f"{key} must be {default}: {value}")
    return value


def load_manifest(path: Path | None = None) -> dict:
    path = (
        Path(path)
        if path is not None
        else ROOT / "adapters/claude/install-manifest.json"
    )
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read Claude install manifest: {path}") from exc
    if not isinstance(data, dict):
        raise TypeError("Claude install manifest must be an object")
    return data


def _manifest_package_roots(manifest: dict) -> dict[str, str]:
    entries = manifest.get("source_roots")
    if not isinstance(entries, list):
        raise TypeError("Claude install manifest must declare source_roots")
    roots: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            source = target = entry
        elif isinstance(entry, dict):
            source = entry.get("source")
            target = entry.get("target", source)
        else:
            raise TypeError(f"source_roots[{index}] must be an object or path")
        source = _relative(source, f"source_roots[{index}].source")
        target = _relative(target, f"source_roots[{index}].target")
        if source != target or not source.startswith(PACKAGE_PREFIX):
            raise ValueError(f"source_roots[{index}] must map a package exactly")
        name = source[len(PACKAGE_PREFIX) :]
        if not PACKAGE_NAME_RE.fullmatch(name) or "/" in name:
            raise ValueError(f"Invalid Combo package root: {name!r}")
        if name in roots:
            raise ValueError(f"Duplicate Combo package root: {name}")
        roots[name] = source
    if set(roots) != set(EXPECTED_PACKAGES):
        raise ValueError(
            "Claude source_roots must contain exactly the 14 declared Combo packages"
        )
    return roots


def manifest_package_names(manifest: dict | None = None) -> set[str]:
    return set(_manifest_package_roots(manifest or load_manifest()))


def _manifest_settings(manifest: dict) -> tuple[tuple[str, ...], dict[str, str]]:
    settings = manifest.get("settings", {})
    if not isinstance(settings, dict):
        raise TypeError("settings manifest section must be an object")
    plugins = settings.get(
        "disable_plugins", manifest.get("disable_plugins", list(DISABLE_PLUGINS))
    )
    if not isinstance(plugins, list) or tuple(plugins) != DISABLE_PLUGINS:
        raise ValueError("Claude installer may disable only the three declared plugins")
    overrides = settings.get(
        "skill_overrides", manifest.get("skill_overrides", SKILL_OVERRIDES)
    )
    if not isinstance(overrides, dict) or overrides != SKILL_OVERRIDES:
        raise ValueError("Claude installer may own only the multi-model skill override")
    return tuple(plugins), dict(overrides)


def _manifest_legacy_section(manifest: dict) -> str:
    section = manifest.get("legacy_owned_section", LEGACY_OWNED_SECTION)
    if section != LEGACY_OWNED_SECTION:
        raise ValueError("legacy_owned_section must match the reviewed legacy section")
    return section


def _legacy_prefix(text: str, expected: str) -> str | None:
    for value in (expected, expected.replace("\n", "\r\n")):
        if text.startswith(value) and (
            len(text) == len(value) or text[len(value)] in "\r\n"
        ):
            return value
    return None


def _validate_manifest(manifest: dict) -> dict[str, str]:
    roots = _manifest_package_roots(manifest)
    _manifest_settings(manifest)
    _manifest_path(manifest, "ownership_index", OWNERSHIP_INDEX)
    _manifest_path(manifest, "override_root", OVERRIDE_ROOT)
    _manifest_path(manifest, "policy_source", POLICY_SOURCE)
    _manifest_path(manifest, "agent_source", AGENT_SOURCE)
    _manifest_path(manifest, "claude_file", CLAUDE_FILE)
    _manifest_path(manifest, "settings_file", SETTINGS_FILE)
    agent_target = _relative(manifest.get("agent_target", AGENT_TARGET), "agent_target")
    if agent_target != AGENT_TARGET:
        raise ValueError(f"agent_target must be {AGENT_TARGET}: {agent_target}")
    markers = manifest.get("claude_markers", {})
    if not isinstance(markers, dict):
        raise TypeError("claude_markers must be an object")
    if (
        markers.get("begin", CLAUDE_BEGIN) != CLAUDE_BEGIN
        or markers.get("end", CLAUDE_END) != CLAUDE_END
    ):
        raise ValueError("Claude policy markers are fixed")
    _manifest_legacy_section(manifest)
    return roots


def _is_link(path: Path) -> bool:
    junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(junction and junction())


def _assert_target(path: Path, root: Path) -> None:
    path, root = Path(path), Path(root)
    if _is_link(root):
        raise ValueError(f"Claude target root cannot be a symlink or junction: {root}")
    root_resolved = root.resolve(strict=False)
    if not path.resolve(strict=False).is_relative_to(root_resolved):
        raise ValueError(f"Target escapes ~/.claude: {path}")
    current = path
    while True:
        if current.exists() and _is_link(current):
            raise ValueError(f"Symlink or junction on owned path: {path}")
        if current == root or current.parent == current:
            break
        current = current.parent


def _assert_source(path: Path) -> None:
    path = Path(path)
    source_root = ROOT.resolve(strict=False)
    if not path.resolve(strict=False).is_relative_to(source_root):
        raise ValueError(f"Source escapes this checkout: {path}")
    current = path
    while True:
        if current.exists() and _is_link(current):
            raise ValueError(f"Symlink or junction in source: {path}")
        if current == ROOT or current.parent == current:
            break
        current = current.parent


def _walk_files(root: Path) -> Iterable[Path]:
    if not root.is_dir() or _is_link(root):
        raise ValueError(f"Missing or unsafe source directory: {root}")
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if _is_link(child):
            raise ValueError(f"Symlink or junction in source: {child}")
        if child.is_dir():
            yield from _walk_files(child)
        elif child.is_file():
            yield child
        else:
            raise ValueError(f"Unsupported source entry: {child}")


def _read_file(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if _is_link(path) or not path.is_file():
        raise ValueError(f"Owned path is not a regular file: {path}")
    return path.read_bytes()


def _policy_text(manifest: dict) -> str:
    policy_source = ROOT / _manifest_path(manifest, "policy_source", POLICY_SOURCE)
    _assert_source(policy_source)
    if not policy_source.is_file():
        raise ValueError(f"Missing Claude policy source: {policy_source}")
    text = policy_source.read_text(encoding="utf-8")
    rule_source = ROOT / "skills/combo/practices/project-knowledge-rule.md"
    _assert_source(rule_source)
    text = text.rstrip() + "\n\n" + rule_source.read_text(encoding="utf-8").strip()
    if CLAUDE_BEGIN in text or CLAUDE_END in text:
        raise ValueError("Claude policy source must not contain owned markers")
    return text.rstrip("\r\n")


def _marker_span(text: str) -> tuple[int, int] | None:
    begin_count, end_count = text.count(CLAUDE_BEGIN), text.count(CLAUDE_END)
    if begin_count != end_count:
        raise ValueError("Unbalanced Combo policy markers in CLAUDE.md")
    if begin_count > 1:
        raise ValueError("Duplicate Combo policy block in CLAUDE.md")
    if not begin_count:
        return None
    start = text.index(CLAUDE_BEGIN)
    finish = text.index(CLAUDE_END, start) + len(CLAUDE_END)
    return start, finish


def _consume_owned_newline(text: str, finish: int) -> tuple[int, str]:
    if text.startswith("\r\n", finish):
        return finish + 2, "\r\n"
    if text.startswith("\n", finish):
        return finish + 1, "\n"
    return finish, "\n"


def _unknown_legacy(text: str, expected: str) -> bool:
    if _legacy_prefix(text, expected) is not None:
        return False
    return bool(
        re.match(r"\ufeff?#{1,6}[ \t]+Skill discipline(?:[ \t]*\r?\n|$)", text, re.IGNORECASE)
    )


def outside_owned_policy(raw: bytes | str, manifest: dict | None = None) -> bytes | str:
    """Return CLAUDE.md bytes/text with only the owned policy removed.

    This gives preservation tests a stable comparison surface for Memory Base,
    RTK, Windows, and every other user-owned instruction outside the block.
    """

    manifest = manifest or {}
    expected = _manifest_legacy_section(manifest)
    is_bytes = isinstance(raw, bytes)
    text = raw.decode("utf-8") if is_bytes else raw
    if not isinstance(text, str):
        raise TypeError("CLAUDE.md content must be bytes or str")
    span = _marker_span(text)
    if span:
        start, finish = span
        finish, _ = _consume_owned_newline(text, finish)
        result = text[:start] + text[finish:]
    elif (legacy := _legacy_prefix(text, expected)) is not None:
        result = text[len(legacy) :]
    elif _unknown_legacy(text, expected):
        raise ValueError(
            "Unknown leading Skill discipline section; refusing blanket edit"
        )
    else:
        result = text
    return result.encode("utf-8") if is_bytes else result


def render_claude(
    raw: bytes, manifest: dict | None = None, policy: str | None = None
) -> bytes:
    """Render one owned policy block while preserving all outside bytes."""

    manifest = manifest or {}
    expected = _manifest_legacy_section(manifest)
    text = raw.decode("utf-8")
    policy = _policy_text(manifest) if policy is None else policy.rstrip("\r\n")
    if CLAUDE_BEGIN in policy or CLAUDE_END in policy:
        raise ValueError("Claude policy text must not contain owned markers")
    block = f"{CLAUDE_BEGIN}\n{policy}\n{CLAUDE_END}"
    span = _marker_span(text)
    if span:
        start, finish = span
        finish, eol = _consume_owned_newline(text, finish)
        return (text[:start] + block + eol + text[finish:]).encode("utf-8")
    if (legacy := _legacy_prefix(text, expected)) is not None:
        return (block + "\n" + text[len(legacy) :]).encode("utf-8")
    if _unknown_legacy(text, expected):
        raise ValueError(
            "Unknown leading Skill discipline section; refusing blanket edit"
        )
    return (block + ("\n" + text if text else "\n")).encode("utf-8")


render_claude_md = render_claude


def render_settings(
    raw: bytes | None, manifest: dict | None = None, home: Path | None = None
) -> bytes:
    """Change only the declared plugin flags and Claude skill override."""

    manifest = manifest or {}
    plugins_to_disable, skill_overrides = _manifest_settings(manifest)
    if raw is None:
        before: dict = {}
    else:
        try:
            before = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Claude settings.json is not valid UTF-8 JSON") from exc
        if not isinstance(before, dict):
            raise ValueError("Claude settings.json must contain an object")
    after = copy.deepcopy(before)
    enabled = after.get("enabledPlugins")
    if enabled is not None and not isinstance(enabled, dict):
        raise ValueError("Claude settings enabledPlugins must be an object")
    if isinstance(enabled, dict):
        for plugin in plugins_to_disable:
            if plugin in enabled:
                enabled[plugin] = False
    overrides = after.get("skillOverrides")
    if overrides is not None and not isinstance(overrides, dict):
        raise ValueError("Claude settings skillOverrides must be an object")
    if overrides is None:
        overrides = {}
        after["skillOverrides"] = overrides
    for name, value in skill_overrides.items():
        overrides[name] = value
    return (json.dumps(after, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _frontmatter(
    text: str, path: Path, expected_name: str | None = None
) -> dict[str, str]:
    text = text.removeprefix("\ufeff")
    match = re.match(r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid YAML frontmatter: {path}")
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line[0].isspace():
            continue
        field = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)[ \t]*:[ \t]*(.*)$", line)
        if not field:
            raise ValueError(f"Invalid YAML frontmatter line in {path}: {line}")
        values[field.group(1)] = field.group(2).strip()
    if not values.get("name") or not values.get("description"):
        raise ValueError(f"YAML frontmatter needs name and description: {path}")
    name = values["name"].strip("\"'")
    if expected_name is not None and name != expected_name:
        raise ValueError(f"Skill name mismatch in {path}: {name!r}")
    for key in ("disable-model-invocation", "user-invocable"):
        if key in values and values[key].strip("\"'").lower() not in {"true", "false"}:
            raise ValueError(f"Invalid boolean frontmatter field in {path}: {key}")
    return values


def _strip_markdown_code(text: str) -> str:
    lines: list[str] = []
    fenced = False
    fence_char = ""
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            char = token[0]
            if not fenced:
                fenced, fence_char = True, char
            elif char == fence_char:
                fenced = False
            continue
        if not fenced:
            lines.append(line)
    visible = "".join(lines)
    return re.sub(r"(`+)(?:(?!\1).)*?\1", "", visible, flags=re.DOTALL)


def _link_targets(text: str) -> Iterable[str]:
    text = _strip_markdown_code(text)
    for match in re.finditer(r"\[[^\]]+\]\(([^)]*)\)", text):
        value = match.group(1).strip()
        if value.startswith("<") and ">" in value:
            value = value[1 : value.index(">")]
        else:
            value = value.split(None, 1)[0] if value else ""
        if value:
            yield value


def _validate_links(files: dict[str, bytes]) -> None:
    keys = {key.lower() for key in files}
    dirs = {"."}
    for key in files:
        parts = key.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]).lower())
    for relative, data in files.items():
        if not relative.lower().endswith(".md"):
            continue
        text = data.decode("utf-8")
        parent = PurePosixPath(relative).parent.as_posix()
        for target in _link_targets(text):
            if re.match(r"(?i)^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith(
                ("#", "//")
            ):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            candidate = posixpath.normpath(posixpath.join(parent, target))
            if candidate == ".." or candidate.startswith("../"):
                raise ValueError(
                    f"Markdown link escapes package: {relative} -> {target}"
                )
            lower = candidate.lower().rstrip("/")
            if lower not in keys and lower not in dirs:
                raise ValueError(f"Missing Markdown link: {relative} -> {target}")


def _validate_rendered(files: dict[str, bytes], overrides: set[str]) -> None:
    required = {f"skills/{name}/SKILL.md" for name in EXPECTED_PACKAGES}
    if not required.issubset(files):
        raise ValueError(
            f"Missing skill entrypoints: {sorted(required - files.keys())}"
        )
    for relative, data in files.items():
        path = Path(relative)
        if path.name == "SKILL.md":
            package = (
                path.parts[1]
                if len(path.parts) > 1 and path.parts[0] == "skills"
                else None
            )
            if package is None:
                raise ValueError(f"Skill is outside a package: {relative}")
            if len(path.parts) != 3:
                raise ValueError(f"Nested SKILL.md is not allowed: {relative}")
            _frontmatter(data.decode("utf-8"), Path(relative), package)
            if relative in overrides and re.search(
                r"\$combo(?:\b|-)|agents/openai\.yaml|combo_worker|gpt-[0-9]",
                data.decode("utf-8"),
            ):
                raise ValueError(
                    f"Claude skill contains Codex invocation marker: {relative}"
                )
    _frontmatter(
        files[AGENT_TARGET].decode("utf-8"), Path(AGENT_TARGET), "combo-worker"
    )
    _validate_links(files)


def _ownership_allowed(relative: str, packages: dict[str, str]) -> bool:
    if relative == AGENT_TARGET:
        return True
    return any(relative.startswith(f"{root}/") for root in packages.values())


def _read_owned_index(
    path: Path, root: Path, packages: dict[str, str], manifest: dict
) -> dict[str, str]:
    data = _read_file(path)
    if data is None:
        return {}
    try:
        payload = json.loads(data.decode("utf-8"))
        rows = payload["files"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid Combo ownership index: {path}") from exc
    if not isinstance(rows, list):
        raise TypeError(f"Invalid Combo ownership rows: {path}")
    result: dict[str, str] = {}
    index_rel = _manifest_path(manifest, "ownership_index", OWNERSHIP_INDEX)
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise TypeError(f"Invalid owned row in index: {path}")
        relative = _relative(row["path"], "owned path")
        if relative == index_rel or not _ownership_allowed(relative, packages):
            raise ValueError(f"Owned index contains an out-of-scope path: {relative}")
        checksum = row.get("sha256")
        if not isinstance(checksum, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", checksum
        ):
            raise ValueError(f"Invalid owned checksum: {relative}")
        if relative in result:
            raise ValueError(f"Duplicate owned path: {relative}")
        target = root / PurePosixPath(relative)
        _assert_target(target, root)
        result[relative] = checksum.lower()
    return result


def _ownership_bytes(files: dict[str, bytes], manifest: dict) -> bytes:
    packages = _manifest_package_roots(manifest)
    rows = []
    for relative in sorted(files, key=str.lower):
        if not _ownership_allowed(relative, packages):
            continue
        data = files[relative]
        rows.append({"path": relative, "sha256": digest(data), "bytes": len(data)})
    return (
        json.dumps(
            {"version": manifest.get("version", 1), "package": "combo", "files": rows},
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _existing_package_files(
    root: Path, package_root: str, index_rel: str
) -> Iterable[tuple[str, Path]]:
    target = root / PurePosixPath(package_root)
    if not target.exists():
        return
    if _is_link(target) or not target.is_dir():
        raise ValueError(f"Unsafe Combo package target: {target}")
    for path in _walk_files(target):
        yield path.relative_to(root).as_posix(), path


def _collect_sources(
    packages: dict[str, str], target_root: Path, manifest: dict
) -> tuple[dict[str, bytes], set[str]]:
    target: dict[str, bytes] = {}
    override_paths: set[str] = set()
    for source_rel in packages.values():
        source_root = ROOT / source_rel
        _assert_source(source_root)
        for source_file in _walk_files(source_root):
            relative = source_file.relative_to(source_root).as_posix()
            if source_file.name == ".combo-owned.json":
                continue
            if (
                source_file.name == "openai.yaml"
                and source_file.parent.name == "agents"
            ):
                continue
            target_rel = f"{source_rel}/{relative}"
            _assert_target(target_root / PurePosixPath(target_rel), target_root)
            if target_rel in target:
                raise ValueError(f"Duplicate package target: {target_rel}")
            target[target_rel] = source_file.read_bytes()

    override_root = ROOT / _manifest_path(manifest, "override_root", OVERRIDE_ROOT)
    if override_root.exists():
        _assert_source(override_root)
        for child in sorted(override_root.iterdir(), key=lambda p: p.name.lower()):
            if _is_link(child) or not child.is_dir() or child.name not in packages:
                raise ValueError(f"Unknown or unsafe Claude override package: {child}")
            for override_file in _walk_files(child):
                relative = override_file.relative_to(child).as_posix()
                if (
                    override_file.name == "openai.yaml"
                    and override_file.parent.name == "agents"
                ):
                    continue
                target_rel = f"skills/{child.name}/{relative}"
                _assert_target(target_root / PurePosixPath(target_rel), target_root)
                target[target_rel] = override_file.read_bytes()
                override_paths.add(target_rel)
    return target, override_paths


def build_plan(home: Path, manifest: dict | None = None) -> list[dict]:
    manifest = manifest or load_manifest()
    packages = _validate_manifest(manifest)
    home = Path(home).expanduser().resolve()
    if _is_link(home):
        raise ValueError(f"Claude home cannot be a symlink or junction: {home}")
    target_root = home / CLAUDE_DIR
    _assert_target(target_root, target_root)
    if target_root.exists() and not target_root.is_dir():
        raise ValueError(f"Claude target is not a directory: {target_root}")

    target, overrides = _collect_sources(packages, target_root, manifest)
    agent_source = ROOT / _manifest_path(manifest, "agent_source", AGENT_SOURCE)
    _assert_source(agent_source)
    if not agent_source.is_file():
        raise ValueError(f"Missing Claude worker agent: {agent_source}")
    target[AGENT_TARGET] = agent_source.read_bytes()

    _validate_rendered(target, overrides)

    settings_rel = _manifest_path(manifest, "settings_file", SETTINGS_FILE)
    settings_path = target_root / PurePosixPath(settings_rel)
    claude_rel = _manifest_path(manifest, "claude_file", CLAUDE_FILE)
    claude_path = target_root / PurePosixPath(claude_rel)
    _assert_target(settings_path, target_root)
    _assert_target(claude_path, target_root)
    target[settings_rel] = render_settings(_read_file(settings_path), manifest, home)
    target[claude_rel] = render_claude(_read_file(claude_path) or b"", manifest)

    index_rel = _manifest_path(manifest, "ownership_index", OWNERSHIP_INDEX)
    index_path = target_root / PurePosixPath(index_rel)
    _assert_target(index_path, target_root)
    previous = _read_owned_index(index_path, target_root, packages, manifest)

    # Existing files inside a Combo package are either previously owned or part
    # of this exact desired render.  An unknown collision is user state, so
    # stop before producing any changes.
    for package_root in packages.values():
        for relative, path in _existing_package_files(
            target_root, package_root, index_rel
        ):
            if relative == index_rel or relative in target or relative in previous:
                continue
            raise ValueError(f"Unknown file collides with Combo package: {path}")

    # Check every previously owned file before stale deletion or any write.
    for relative, expected_hash in previous.items():
        current = _read_file(target_root / PurePosixPath(relative))
        if digest(current) != expected_hash:
            raise ValueError(
                f"Owned file drifted; refusing update/removal: {target_root / PurePosixPath(relative)}"
            )
        if relative not in target and current is not None:
            target[relative] = None  # type: ignore[assignment]

    owned_target = {
        relative: data
        for relative, data in target.items()
        if data is not None and _ownership_allowed(relative, packages)
    }
    target[index_rel] = _ownership_bytes(owned_target, manifest)

    changes: list[dict] = []
    for relative, after in sorted(target.items(), key=lambda item: item[0].lower()):
        path = target_root / PurePosixPath(relative)
        _assert_target(path, target_root)
        before = _read_file(path)
        if (
            _ownership_allowed(relative, packages)
            and relative not in previous
            and relative != index_rel
            and before is not None
            and before != after
        ):
            raise ValueError(f"Unowned file collides with Combo package: {path}")
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


def _write_report(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Install Combo into a Claude Code home"
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=("plan", "apply", "verify", "rollback"),
        default="plan",
    )
    parser.add_argument("--home", type=Path, default=REAL_HOME)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    home = args.home.expanduser().resolve()
    if args.action == "rollback":
        if not args.receipt:
            parser.error("rollback requires --receipt")
        rollback(args.receipt, home / CLAUDE_DIR)
        print("Claude rollback complete")
        return

    manifest = load_manifest(args.manifest)
    changes = build_plan(home, manifest)
    if args.action == "plan":
        output = ROOT / "audit/claude/install-plan.json"
        _write_report(
            output, {"target_root": str(home / CLAUDE_DIR), "files": summarize(changes)}
        )
        print(f"{len(changes)} changed files, plan: {output}")
    elif args.action == "verify":
        if changes:
            raise SystemExit(
                f"Installed Claude files differ from source: {len(changes)} files"
            )
        print(
            "Claude installed bytes match source; unmanaged settings and policy bytes preserved"
        )
    else:
        stamp = (
            time.strftime("%Y%m%d-%H%M%S", time.gmtime())
            + f"-{time.time_ns() % 1_000_000:06d}"
        )
        destination = ROOT / "backups" / f"claude-{stamp}"
        receipt = apply(changes, destination, home / CLAUDE_DIR)
        output = ROOT / "audit/claude/install-receipt.json"
        if receipt:
            _write_report(
                output, {"receipt": str(receipt), "files": summarize(changes)}
            )
        print(
            f"Applied {len(changes)} Claude files. Receipt: {receipt}"
            if receipt
            else "Already installed, no changes"
        )


if __name__ == "__main__":
    main()
