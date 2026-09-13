"""Stage temporary A/B Combo discovery variants for the matched experiment.

The builder copies one supplied Combo package into isolated candidate roots,
adds a local fixture discovery overlay, and writes a process-only
``skills.config`` override that disables the globally installed Combo entry.
It never changes global Codex configuration, installed skills, fixtures, or
starts a model session. Candidate B's direct entries are declared in JSON so a
later manifest can add or replace domain entries without changing this builder.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover, Python 3.11+ is required
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[2]
_CANDIDATE_PACKAGE = ROOT / "candidates" / "common" / "combo"
DEFAULT_PACKAGE = (
    _CANDIDATE_PACKAGE if _CANDIDATE_PACKAGE.is_dir() else ROOT / "skills" / "combo"
)
DEFAULT_FIXTURES = ROOT / "evals" / "v2" / "fixtures"
DEFAULT_ENTRY_MANIFEST = Path(__file__).with_name("variants") / "entry-manifest.json"
FRONTMATTER = re.compile(
    r"\A(?P<open>---\r?\n)(?P<body>.*?)(?P<close>---\r?\n)", re.DOTALL
)
SAFE_ENTRY_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class StageError(ValueError):
    """Raised when a requested staging input would make the comparison unsafe."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StageError(f"Cannot read JSON manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StageError(f"Manifest must contain an object: {path}")
    return value


def load_entry_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest.get("schema_version") != 1:
        raise StageError(f"Unsupported entry manifest schema in {path}")
    fallback = manifest.get("fallback")
    if not isinstance(fallback, dict):
        raise StageError("Entry manifest fallback must be an object")
    if (
        fallback.get("name") != "combo"
        or not str(fallback.get("description", "")).strip()
    ):
        raise StageError("Entry manifest fallback must define combo and a description")

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise StageError("Entry manifest entries must be a list")
    names: set[str] = set()
    normalized: list[dict[str, str]] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise StageError(f"Entry {index} must be an object")
        name = raw.get("name")
        description = raw.get("description")
        target = raw.get("target")
        domain = raw.get("domain")
        if not (
            isinstance(name, str)
            and name.strip()
            and isinstance(description, str)
            and description.strip()
            and isinstance(target, str)
            and target.strip()
        ):
            raise StageError(f"Entry {index} needs name, description, and target")
        if domain is not None and (
            not isinstance(domain, str) or not SAFE_ENTRY_NAME.fullmatch(domain.strip())
        ):
            raise StageError(f"Entry {index} has an invalid domain: {domain!r}")
        if name == "combo" or not SAFE_ENTRY_NAME.fullmatch(name):
            raise StageError(f"Invalid or reserved entry name: {name!r}")
        if name in names:
            raise StageError(f"Duplicate entry name: {name}")
        target_path = Path(target)
        if target_path.is_absolute() or ".." in target_path.parts:
            raise StageError(f"Entry target must stay inside the package: {target}")
        names.add(name)
        normalized_entry = {
            "name": name,
            "description": description.strip(),
            "target": target_path.as_posix(),
        }
        if domain is not None:
            normalized_entry["domain"] = domain.strip()
        normalized.append(normalized_entry)
    return {
        "schema_version": 1,
        "fallback": {
            "name": "combo",
            "description": str(fallback["description"]).strip(),
        },
        "entries": normalized,
    }


def toml_literal(value: Any) -> str:
    """Render the scalar/list values used by skills.config without a dependency."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(toml_literal(item) for item in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", key):
                raise StageError(f"Unsupported TOML key in skills.config: {key!r}")
            parts.append(f"{key} = {toml_literal(item)}")
        return "{ " + ", ".join(parts) + " }"
    raise StageError(f"Unsupported skills.config value: {value!r}")


def render_skills_config(rows: Iterable[Mapping[str, Any]]) -> str:
    lines: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise StageError("Each skills.config row must be an object")
        path = row.get("path")
        if not isinstance(path, str) or not path:
            raise StageError("Each skills.config row needs a nonempty path")
        lines.append("[[skills.config]]")
        for key, value in row.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", key):
                raise StageError(f"Unsupported skills.config key: {key!r}")
            lines.append(f"{key} = {toml_literal(value)}")
        lines.append("")
    return "\n".join(lines)


def load_existing_skills_config(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    if tomllib is None:  # pragma: no cover
        raise StageError("Python 3.11 or newer is required to parse config.toml")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise StageError(f"Cannot read base Codex config {path}: {exc}") from exc
    skills = data.get("skills", {})
    rows = skills.get("config", []) if isinstance(skills, dict) else []
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise StageError("skills.config in the base config must be an array of tables")
    return [copy.deepcopy(row) for row in rows]


def merge_skills_config(
    existing: Iterable[Mapping[str, Any]], disabled_path: Path
) -> list[dict[str, Any]]:
    """Preserve existing rows and append or disable exactly the global Combo row."""
    target = str(disabled_path)
    merged: list[dict[str, Any]] = []
    found = False
    for raw in existing:
        if not isinstance(raw, Mapping):
            raise StageError("Each existing skills.config row must be an object")
        row = copy.deepcopy(dict(raw))
        if row.get("path") == target:
            row["enabled"] = False
            found = True
        merged.append(row)
    if not found:
        merged.append({"path": target, "enabled": False})
    return merged


def resolve_base_config(explicit: Path | None) -> Path | None:
    if explicit is not None:
        resolved = explicit.expanduser().resolve()
        if not resolved.is_file():
            raise StageError(f"Base Codex config does not exist: {resolved}")
        return resolved
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    candidate = (codex_home / "config.toml").resolve()
    return candidate if candidate.is_file() else None


def yaml_block_field(name: str, value: str, newline: str = "\n") -> str:
    """Render a frontmatter folded scalar without trusting manifest punctuation."""
    lines = value.splitlines() or [""]
    return f"{name}: >{newline}" + "".join(f"  {line}{newline}" for line in lines)


def narrow_combo_description(raw: bytes, description: str) -> bytes:
    text = raw.decode("utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise StageError("Combo SKILL.md must start with YAML frontmatter")
    body = match.group("body")
    newline = "\r\n" if "\r\n" in match.group("open") else "\n"
    lines = body.splitlines(keepends=True)
    start = next(
        (index for index, line in enumerate(lines) if line.startswith("description:")),
        None,
    )
    if start is None:
        raise StageError("Combo SKILL.md has no frontmatter description")
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line and not line[0].isspace():
            break
        end += 1
    replacement = yaml_block_field("description", description, newline)
    lines[start:end] = [replacement]
    rendered = (
        match.group("open")
        + "".join(lines)
        + match.group("close")
        + text[match.end() :]
    )
    return rendered.encode("utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_bytes(root: Path, *, skip_prefixes: Iterable[str] = ()) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    prefixes = tuple(prefix.rstrip("/") for prefix in skip_prefixes)

    def skipped(relative: str) -> bool:
        return any(
            relative == prefix or relative.startswith(prefix + "/")
            for prefix in prefixes
        )

    # Recursive walks can inspect a directory symlink's children. Fixture
    # discovery roots intentionally point at each candidate package, so prune
    # those links before comparing fixture payloads.
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        current_relative = (
            current_path.relative_to(root).as_posix() if current_path != root else ""
        )
        if current_relative and skipped(current_relative):
            directories[:] = []
            continue
        directories[:] = [
            name
            for name in directories
            if not (current_path / name).is_symlink()
            and not skipped((current_path / name).relative_to(root).as_posix())
        ]
        for name in filenames:
            path = current_path / name
            if path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            if not skipped(relative):
                result[relative] = path.read_bytes()
    return result


def ensure_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise StageError(
            f"Output must be absent or empty, refusing to overwrite: {path}"
        )
    path.mkdir(parents=True, exist_ok=True)


def relative_link(source: Path, link: Path) -> str:
    return os.path.relpath(source, link.parent)


def link_skill_root(source: Path, destination: Path) -> str:
    """Link a fixture's .agents/skills to the candidate root, with safe copy fallback."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(
            relative_link(source, destination), destination, target_is_directory=True
        )
        return "symlink"
    except (OSError, NotImplementedError):
        shutil.copytree(source, destination)
        return "copy"


def overlay_text(variant: str) -> str:
    if variant == "A":
        discovery = (
            "Use the staged `.agents/skills/combo/SKILL.md` entry for substantive "
            "engineering and domain requests."
        )
    else:
        discovery = (
            "When a substantive request has one clear intent, use the matching "
            "staged `combo-*` entry; otherwise use staged `combo` as the fallback "
            "for cross-workflow, uncertain, or explicitly `$combo` requests."
        )
    return (
        "# Evaluation-only Combo discovery overlay\n\n"
        "For this fixture only, supersede only the global Combo discovery paragraph "
        f"and resolve the staged candidate {variant} under `.agents/skills` instead "
        "of the globally installed `$combo` entry. "
        f"{discovery} Simple translation or general conversation stays inline. "
        "An explicit requested stopping point wins over intent selection: keep "
        "plan-only, diagnosis-only, review-only, or verification-only work at that "
        "boundary, while a request to plan and build continues through its full "
        "authorized task. Preserve the common Combo engineering policy and every "
        "other global instruction, including scope, user preferences, permissions, "
        "and memory rules.\n"
    )


def write_wrapper(destination: Path, entry: Mapping[str, str]) -> None:
    target = entry["target"]
    link = f"../combo/{target}"
    depth = ""
    if entry.get("domain") == "engineering":
        depth = (
            " For substantive technical mechanisms, consult the [specialist index]"
            "(../combo/specialists/INDEX.md) and, when deeper examples are needed,"
            " the [engineering library](../combo/references/library/engineering.md);"
            " trivial edits can stay inline."
        )
    content = (
        "---\n"
        f"name: {entry['name']}\n"
        + yaml_block_field("description", entry["description"])
        + "---\n\n"
        f"Read and follow the shared Combo workflow at [{target}]({link}). "
        "Preserve the user's requested stopping point and load only the relevant "
        f"practice or specialist notes.{depth}\n"
    )
    destination.write_text(content, encoding="utf-8", newline="\n")
    metadata = destination.parent / "agents/openai.yaml"
    metadata.parent.mkdir(exist_ok=True)
    metadata.write_text(
        "policy:\n  allow_implicit_invocation: true\n", encoding="utf-8"
    )


def copy_fixtures(
    fixtures_root: Path,
    destination_root: Path,
    skills_root: Path,
    variant: str,
    selected: list[str] | None,
) -> list[dict[str, str]]:
    if not fixtures_root.is_dir():
        raise StageError(f"Fixture root does not exist: {fixtures_root}")
    available = {path.name: path for path in fixtures_root.iterdir() if path.is_dir()}
    names = selected or sorted(available)
    missing = [name for name in names if name not in available]
    if missing:
        raise StageError("Unknown fixture(s): " + ", ".join(missing))
    if not names:
        raise StageError("At least one fixture is required for per-fixture overlays")

    rows: list[dict[str, str]] = []
    for name in names:
        source = available[name]
        destination = destination_root / name
        shutil.copytree(source, destination)
        overlay = destination / "AGENTS.md"
        if overlay.exists():
            raise StageError(
                f"Fixture already has AGENTS.md; refusing to overwrite: {source}"
            )
        overlay.write_text(overlay_text(variant), encoding="utf-8", newline="\n")
        agents_skills = destination / ".agents" / "skills"
        if agents_skills.exists() or agents_skills.is_symlink():
            raise StageError(
                f"Fixture already has .agents/skills; refusing to overwrite: {source}"
            )
        link_mode = link_skill_root(skills_root, agents_skills)
        source_bytes = file_bytes(source)
        staged_bytes = file_bytes(
            destination, skip_prefixes=("AGENTS.md", ".agents/skills")
        )
        if source_bytes != staged_bytes:
            changed = sorted(set(source_bytes) | set(staged_bytes))
            changed = [
                relative
                for relative in changed
                if source_bytes.get(relative) != staged_bytes.get(relative)
            ]
            raise StageError(
                f"Fixture copy changed source content in {name}: {', '.join(changed)}"
            )
        rows.append(
            {
                "id": name,
                "cwd": f"fixtures/{name}",
                "agents_overlay": f"fixtures/{name}/AGENTS.md",
                "discovery_skills_root": f"fixtures/{name}/.agents/skills",
                "discovery_link_mode": link_mode,
            }
        )
    return rows


def build_variant(
    *,
    package: Path,
    fixtures_root: Path,
    output: Path,
    variant: str,
    global_combo_path: Path,
    entries_manifest: Mapping[str, Any],
    base_config: Path | None,
    selected_fixtures: list[str] | None,
) -> dict[str, Any]:
    if not package.is_dir() or not (package / "SKILL.md").is_file():
        raise StageError(f"Common Combo package is missing SKILL.md: {package}")
    variant_root = output / variant
    skills_root = variant_root / "skills"
    combo_destination = skills_root / "combo"
    fixture_destination = variant_root / "fixtures"
    process_destination = variant_root / "process"
    variant_root.mkdir(parents=True, exist_ok=False)
    skills_root.mkdir()
    shutil.copytree(package, combo_destination)

    direct_entries: list[dict[str, str]] = []
    if variant == "B":
        fallback_description = str(entries_manifest["fallback"]["description"])
        combo_skill = combo_destination / "SKILL.md"
        combo_skill.write_bytes(
            narrow_combo_description(combo_skill.read_bytes(), fallback_description)
        )
        for entry in entries_manifest["entries"]:
            target = combo_destination / entry["target"]
            if not target.is_file():
                raise StageError(
                    f"Entry target does not exist in common package: {entry['target']}"
                )
            wrapper = skills_root / entry["name"] / "SKILL.md"
            wrapper.parent.mkdir(parents=True)
            write_wrapper(wrapper, entry)
            direct_entries.append(dict(entry))

    base_rows = load_existing_skills_config(base_config)
    merged_rows = merge_skills_config(base_rows, global_combo_path)
    process_destination.mkdir()
    process_config = process_destination / "skills.config.toml"
    rendered_config = render_skills_config(merged_rows)
    if tomllib is not None:
        try:
            tomllib.loads(rendered_config)
        except tomllib.TOMLDecodeError as exc:
            raise StageError(
                f"Generated process skills.config is invalid TOML: {exc}"
            ) from exc
    process_config.write_text(rendered_config, encoding="utf-8", newline="\n")

    fixture_rows = copy_fixtures(
        fixtures_root,
        fixture_destination,
        skills_root,
        variant,
        selected_fixtures,
    )
    metadata = {
        "schema_version": 1,
        "variant": variant,
        "package_root": "skills",
        "combo_skill": "skills/combo/SKILL.md",
        "direct_entries": direct_entries,
        "fixtures": fixture_rows,
        "process_override": {
            "config_file": "process/skills.config.toml",
            "config_key": "skills.config",
            "disabled_path": str(global_combo_path),
            "base_config_read": str(base_config) if base_config else None,
            "existing_rows_preserved": bool(base_rows),
            "harness_merge_required": not bool(base_rows),
            "rows": merged_rows,
        },
    }
    (variant_root / "variant.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return metadata


def verify_common_content(output: Path) -> dict[str, Any]:
    a = file_bytes(output / "A" / "skills" / "combo")
    b = file_bytes(output / "B" / "skills" / "combo")
    if set(a) != set(b):
        raise StageError("A/B common package file sets differ")
    differing = sorted(relative for relative in a if a[relative] != b[relative])
    if differing != ["SKILL.md"]:
        raise StageError(
            "Unexpected A/B common package differences: " + ", ".join(differing)
        )

    a_fixtures = output / "A" / "fixtures"
    b_fixtures = output / "B" / "fixtures"
    fixture_differences: list[str] = []
    fixture_names = sorted(path.name for path in a_fixtures.iterdir() if path.is_dir())
    if fixture_names != sorted(
        path.name for path in b_fixtures.iterdir() if path.is_dir()
    ):
        raise StageError("A/B fixture sets differ")
    for name in fixture_names:
        left = file_bytes(a_fixtures / name, skip_prefixes=(".agents/skills",))
        right = file_bytes(b_fixtures / name, skip_prefixes=(".agents/skills",))
        for relative in sorted(set(left) | set(right)):
            if relative == "AGENTS.md":
                continue
            if left.get(relative) != right.get(relative):
                fixture_differences.append(f"{name}/{relative}")
    if fixture_differences:
        raise StageError(
            "Unexpected A/B fixture differences: " + ", ".join(fixture_differences)
        )
    return {
        "common_package_identical_except": ["skills/combo/SKILL.md"],
        "fixture_content_identical_except": ["AGENTS.md", ".agents/skills link"],
        "common_file_count": len(a),
        "fixture_count": len(fixture_names),
        "a_combo_sha256": sha256(output / "A" / "skills" / "combo" / "SKILL.md"),
        "b_combo_sha256": sha256(output / "B" / "skills" / "combo" / "SKILL.md"),
    }


def verify_entry_surfaces(
    output: Path, entries: Iterable[Mapping[str, str]]
) -> dict[str, Any]:
    """Check that B exposes link-only wrappers and A exposes only the fallback."""
    expected = [dict(entry) for entry in entries]
    a_skills = output / "A" / "skills"
    b_skills = output / "B" / "skills"
    a_names = sorted(path.name for path in a_skills.iterdir() if path.is_dir())
    b_names = sorted(path.name for path in b_skills.iterdir() if path.is_dir())
    expected_b = sorted(["combo"] + [entry["name"] for entry in expected])
    if a_names != ["combo"]:
        raise StageError(
            "Candidate A exposes entries besides combo: " + ", ".join(a_names)
        )
    if b_names != expected_b:
        raise StageError("Candidate B entry set does not match manifest")

    for entry in expected:
        wrapper = b_skills / entry["name"] / "SKILL.md"
        content = wrapper.read_text(encoding="utf-8")
        target = entry["target"]
        link = f"[{target}](../combo/{target})"
        if link not in content:
            raise StageError(f"Wrapper does not link to its shared workflow: {wrapper}")
        if entry.get("domain") == "engineering":
            for required in (
                "../combo/specialists/INDEX.md",
                "../combo/references/library/engineering.md",
            ):
                if required not in content:
                    raise StageError(
                        f"Engineering wrapper lacks selective depth link {required}: {wrapper}"
                    )
    return {"a_entries": a_names, "b_entries": b_names}


def build(
    *,
    package: Path,
    fixtures_root: Path,
    output: Path,
    global_combo_path: Path,
    entry_manifest: Path,
    base_config: Path | None = None,
    selected_fixtures: list[str] | None = None,
) -> dict[str, Any]:
    package = package.expanduser().resolve()
    fixtures_root = fixtures_root.expanduser().resolve()
    output = output.expanduser().resolve()
    global_combo_path = global_combo_path.expanduser().resolve()
    entry_data = load_entry_manifest(entry_manifest.expanduser().resolve())
    base_config = resolve_base_config(base_config)
    for source in (package, fixtures_root):
        if output == source or output.is_relative_to(source):
            raise StageError(f"Output must be outside input tree: {output}")
    ensure_empty_output(output)

    variants: dict[str, Any] = {}
    for variant in ("A", "B"):
        variants[variant] = build_variant(
            package=package,
            fixtures_root=fixtures_root,
            output=output,
            variant=variant,
            global_combo_path=global_combo_path,
            entries_manifest=entry_data,
            base_config=base_config,
            selected_fixtures=selected_fixtures,
        )
    comparison = verify_common_content(output)
    comparison["entry_surfaces"] = verify_entry_surfaces(output, entry_data["entries"])
    root_manifest = {
        "schema_version": 1,
        "experiment": "one-entry-vs-modular-pack",
        "common_package_source": str(package),
        "fixture_source": str(fixtures_root),
        "entry_manifest_source": str(entry_manifest.expanduser().resolve()),
        "variants": {name: f"{name}/variant.json" for name in variants},
        "comparison": comparison,
        "integration": {
            "fixture_cwds": "<variant>/fixtures/<fixture>",
            "native_discovery": "Call scripts/codex_inventory.py against each fixture cwd after applying the process config override.",
            "process_config": "Read <variant>/process/skills.config.toml as the skills.config overlay; preserve current rows when constructing the per-process override.",
            "disabled_global_combo_path": str(global_combo_path),
            "no_prompt_mutation": True,
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(root_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return root_manifest


def check_defaults() -> dict[str, Any]:
    sentinel = Path("C:/codex-eval/global/skills/combo/SKILL.md")
    with tempfile.TemporaryDirectory(prefix="combo-ab-stage-") as temp:
        output = Path(temp) / "variants"
        result = build(
            package=DEFAULT_PACKAGE,
            fixtures_root=DEFAULT_FIXTURES,
            output=output,
            global_combo_path=sentinel,
            entry_manifest=DEFAULT_ENTRY_MANIFEST,
            base_config=None,
            selected_fixtures=None,
        )
        summary = {
            "status": "passed",
            "variants": sorted(result["variants"]),
            "comparison": result["comparison"],
        }
    summary["output_cleaned"] = not output.exists()
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        type=Path,
        default=DEFAULT_PACKAGE,
        help="Common combo package directory",
    )
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=DEFAULT_FIXTURES,
        help="Fixture directory to copy",
    )
    parser.add_argument(
        "--output", type=Path, help="Empty output directory for A/ and B/ variants"
    )
    parser.add_argument(
        "--global-combo-path",
        type=Path,
        help="Installed global combo SKILL.md path to disable per process",
    )
    parser.add_argument(
        "--entry-manifest",
        type=Path,
        default=DEFAULT_ENTRY_MANIFEST,
        help="JSON manifest declaring B direct entries",
    )
    parser.add_argument(
        "--base-config",
        type=Path,
        help="Optional Codex config.toml to read existing skills.config rows from",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        help="Stage one fixture by name; repeatable",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build and validate defaults in an isolated temporary directory",
    )
    args = parser.parse_args(argv)
    if not args.check and (args.output is None or args.global_combo_path is None):
        parser.error(
            "--output and --global-combo-path are required unless --check is used"
        )
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check:
            print(json.dumps(check_defaults(), ensure_ascii=False, indent=2))
            return 0
        result = build(
            package=args.package,
            fixtures_root=args.fixtures_root,
            output=args.output,
            global_combo_path=args.global_combo_path,
            entry_manifest=args.entry_manifest,
            base_config=args.base_config,
            selected_fixtures=args.fixtures,
        )
    except StageError as exc:
        print(f"stage_variants: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "passed",
                "output": str(args.output.resolve()),
                "manifest": result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
