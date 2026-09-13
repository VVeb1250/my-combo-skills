#!/usr/bin/env python3
"""Build the bounded reference-only library from the four pinned source packs.

The output contains REFERENCE.md files, never nested SKILL.md entrypoints.
Upstream installers, hooks, runtimes, executable scripts, credentials, and
unrelated repository files are not imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
LOCK_PATH = ROOT / "sources.lock.json"
DEFAULT_OUTPUT = ROOT / "candidates" / "common" / "combo" / "references" / "library"
OUTPUT = DEFAULT_OUTPUT
MANIFEST_PATH = ROOT / "curation" / "full-library.json"
AUDIT_JSON = ROOT / "audit" / "ab" / "source-coverage.json"
AUDIT_MD = ROOT / "audit" / "ab" / "source-coverage.md"

PACK_ORDER = ("karpathy", "ponytail", "matt", "ecc")
EXPECTED_COUNTS = {"karpathy": 1, "ponytail": 6, "matt": 37, "ecc": 286}
DOMAINS = (
    "engineering",
    "research",
    "content",
    "learning",
    "business",
    "media",
    "productivity",
    "host-integration",
    "uncategorized",
)

SUPPORT_DIRS = {
    "asset",
    "assets",
    "doc",
    "docs",
    "example",
    "examples",
    "fixture",
    "fixtures",
    "reference",
    "references",
    "template",
    "templates",
}
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    "scripts",
    "script",
    "bin",
    "install",
    "installer",
    "dist",
    "build",
    "target",
}
MARKDOWN_EXTS = {".md", ".mdc", ".mdx", ".markdown", ".rst", ".txt"}
SAFE_DATA_EXTS = {
    ".csv",
    ".css",
    ".html",
    ".json",
    ".svg",
    ".toml",
    ".tsv",
    ".xml",
    ".yaml",
    ".yml",
}
ASSET_EXTS = {".gif", ".jpeg", ".jpg", ".mp3", ".mp4", ".png", ".webp"}
SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".npmrc",
    "credentials.json",
    "secrets.json",
}
SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
MAX_ASSET_BYTES = 8 * 1024 * 1024


def names(*items: str) -> set[str]:
    return set(items)


RESEARCH_ECC = names(
    "competitive-platform-analysis",
    "competitive-report-structure",
    "deep-research",
    "foundation-models-on-device",
    "ito-baskets",
    "ito-compute",
    "ito-inference",
    "ito-training",
    "market-research",
    "ml-adoption-playbook",
    "mle-workflow",
    "recsys-pipeline-architect",
    "research-ops",
    "scientific-db-pubmed-database",
    "scientific-db-uspto-database",
    "scientific-pkg-gget",
    "scientific-thinking-literature-review",
    "scientific-thinking-scholar-evaluation",
)
CONTENT_ECC = names(
    "article-writing",
    "brand-discovery",
    "brand-voice",
    "content-engine",
    "crosspost",
    "marketing-campaign",
    "seo",
    "social-graph-ranker",
    "social-publisher",
)
BUSINESS_ECC = names(
    "carrier-relationship-management",
    "customer-billing-ops",
    "customs-trade-compliance",
    "energy-procurement",
    "finance-billing-ops",
    "growth-log",
    "inventory-demand-planning",
    "investor-materials",
    "investor-outreach",
    "lead-intelligence",
    "logistics-exception-management",
    "prediction-market-oracle-research",
    "prediction-market-risk-review",
    "product-capability",
    "product-lens",
    "production-audit",
    "production-scheduling",
    "quality-nonconformance",
    "returns-reverse-logistics",
)
MEDIA_ECC = names(
    "blender-motion-state-inspection",
    "dashboard-builder",
    "fal-ai-media",
    "frontend-slides",
    "ios-icon-gen",
    "liquid-glass-design",
    "make-interfaces-feel-better",
    "manim-video",
    "motion-advanced",
    "motion-foundations",
    "motion-patterns",
    "motion-ui",
    "remotion-video-creation",
    "taste",
    "tasteforge-video",
    "ui-demo",
    "video-editing",
    "videodb",
)
HOST_ECC = names(
    "continuous-learning",
    "continuous-learning-v2",
    "agentic-os",
    "agent-sort",
    "automation-audit-ops",
    "canary-watch",
    "ck",
    "claude-devfleet",
    "config-gc",
    "connections-optimizer",
    "configure-ecc",
    "cost-tracking",
    "council",
    "council-multi-model",
    "delivery-gate",
    "dmux-workflows",
    "email-ops",
    "enterprise-agent-ops",
    "ecc-tools-cost-audit",
    "exa-search",
    "gateguard",
    "generating-python-installer",
    "github-ops",
    "git-workflow",
    "google-workspace-ops",
    "hermes-imports",
    "hookify-rules",
    "jira-integration",
    "knowledge-ops",
    "messages-ops",
    "nanoclaw-repl",
    "nasiko-control-plane",
    "openclaw-persona-forge",
    "orch-add-feature",
    "orch-build-mvp",
    "orch-change-feature",
    "orch-fix-defect",
    "orch-pipeline",
    "orch-refine-code",
    "parallel-execution-optimizer",
    "plan-canvas",
    "plan-orchestrate",
    "project-flow-ops",
    "prompt-optimizer",
    "ralphinho-rfc-pipeline",
    "recursive-decision-ledger",
    "rules-distill",
    "santa-method",
    "search-first",
    "skill-comply",
    "skill-scout",
    "skill-stocktake",
    "strategic-compact",
    "team-agent-orchestration",
    "team-builder",
    "terminal-opener",
    "terminal-ops",
    "token-budget-advisor",
    "uncloud",
    "unified-memory",
    "unified-notifications-ops",
    "workspace-surface-audit",
    "windows-desktop-e2e",
    "x-api",
)
HEALTH_ECC = names(
    "healthcare-cdss-patterns",
    "healthcare-emr-patterns",
    "healthcare-eval-harness",
    "healthcare-phi-compliance",
    "hipaa-compliance",
)
DOCS_ECC = names("nutrient-document-processing", "visa-doc-translate")
FINANCE_ECC = names(
    "agent-payment-x402",
    "defi-amm-security",
    "evm-token-decimals",
    "llm-trading-agent-security",
)
PRODUCTIVITY_ECC = names("knowledge-ops", "project-flow-ops")

LEARNING_MATT = names("misc/scaffold-exercises", "productivity/teach")
PRODUCTIVITY_MATT = names(
    "in-progress/retro",
    "in-progress/writing-beats",
    "in-progress/writing-fragments",
    "in-progress/writing-shape",
    "productivity/grill-me",
    "productivity/grilling",
    "productivity/handoff",
    "productivity/to-questionnaire",
    "productivity/wait-what",
    "productivity/writing-for-agents",
)
HOST_MATT = names(
    "engineering/setup-matt-pocock-skills",
    "in-progress/claude-handoff",
    "misc/git-guardrails-claude-code",
    "misc/migrate-to-shoehorn",
    "misc/setup-pre-commit",
)

ADAPTED_KEYS = {
    "karpathy:skills/karpathy-guidelines/SKILL.md",
    "ponytail:skills/ponytail/SKILL.md",
    "ponytail:skills/ponytail-review/SKILL.md",
    "matt:skills/engineering/ask-matt/SKILL.md",
    "matt:skills/engineering/code-review/SKILL.md",
    "matt:skills/engineering/codebase-design/SKILL.md",
    "matt:skills/engineering/diagnosing-bugs/SKILL.md",
    "matt:skills/engineering/tdd/SKILL.md",
}
ADAPTED_KEYS.update(
    f"ecc:skills/{name}/SKILL.md"
    for name in names(
        "api-design",
        "angular-developer",
        "bun-runtime",
        "cpp-coding-standards",
        "dart-flutter-patterns",
        "database-migrations",
        "django-patterns",
        "docker-patterns",
        "dotnet-patterns",
        "fastapi-patterns",
        "golang-patterns",
        "java-coding-standards",
        "kotlin-coroutines-flows",
        "kubernetes-patterns",
        "mcp-server-patterns",
        "nestjs-patterns",
        "nextjs-turbopack",
        "postgres-patterns",
        "prisma-patterns",
        "python-patterns",
        "react-native-patterns",
        "react-patterns",
        "redis-patterns",
        "rust-patterns",
        "springboot-patterns",
        "swift-concurrency-6-2",
        "vue-patterns",
    )
)
DEPRECATED_KEYS = {"ecc:skills/continuous-learning/SKILL.md"}
PERSONA_KEYS = {"ecc:skills/openclaw-persona-forge/SKILL.md"}
EXPERIMENTAL_ECC = names(
    "agent-payment-x402",
    "foundation-models-on-device",
    "nanoclaw-repl",
    "nasiko-control-plane",
    "openclaw-persona-forge",
    "uncloud",
    "x-api",
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def tracked_paths(repo: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def immutable_url(info: dict, source_rel: Path) -> str:
    base = info["url"].removesuffix(".git")
    return f"{base}/blob/{info['commit']}/{source_rel.as_posix()}"


def immutable_tree_url(info: dict, source_rel: Path) -> str:
    base = info["url"].removesuffix(".git")
    return f"{base}/tree/{info['commit']}/{source_rel.as_posix()}"


def discover(lock: dict) -> list[dict]:
    found = []
    for pack in PACK_ORDER:
        repo = SOURCES / pack
        skills = repo / "skills"
        if not skills.is_dir():
            raise RuntimeError(f"missing skills directory: {skills}")
        expected_depth = 3 if pack == "matt" else 2
        for skill_file in sorted(skills.rglob("SKILL.md")):
            rel_under_skills = skill_file.relative_to(skills)
            if len(rel_under_skills.parts) != expected_depth:
                continue
            source_rel = skill_file.relative_to(repo)
            found.append(
                {
                    "pack": pack,
                    "repo": repo,
                    "source_file": skill_file,
                    "source_rel": source_rel,
                    "skill_rel": source_rel.parent,
                    "source_key": f"{pack}:{source_rel.as_posix()}",
                    "pack_info": lock[pack],
                }
            )
    found.sort(
        key=lambda item: (PACK_ORDER.index(item["pack"]), item["source_rel"].as_posix())
    )
    return found


def is_sensitive(path: Path) -> bool:
    lower_name = path.name.lower()
    if lower_name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    return any(token in lower_name for token in ("credential", "secret", "private-key"))


def should_copy(path: Path, skill_dir: Path) -> tuple[bool, str]:
    rel = path.relative_to(skill_dir)
    lower_parts = {part.lower() for part in rel.parts}
    if is_sensitive(path):
        return False, "sensitive-or-auth-material"
    if lower_parts.intersection(EXCLUDED_DIRS):
        return False, "upstream-script-or-build-tree"
    if path.stat().st_size > MAX_ASSET_BYTES:
        return False, "oversize-asset"
    if path.name == "SKILL.md":
        return True, "reference-entrypoint-renamed"
    if path.suffix.lower() in MARKDOWN_EXTS:
        return True, "markdown-support"
    if lower_parts.intersection(SUPPORT_DIRS):
        return True, "referenced-support-asset"
    if path.suffix.lower() in SAFE_DATA_EXTS | ASSET_EXTS:
        return True, "small-support-data"
    return False, "unreferenced-or-executable-source"


def destination_for(item: dict, source_path: Path) -> Path:
    rel_in_skill = source_path.relative_to(item["skill_rel_abs"])
    if source_path.name == "SKILL.md":
        rel_in_skill = rel_in_skill.with_name("REFERENCE.md")
    return OUTPUT / item["pack"] / item["skill_rel"] / rel_in_skill


LINK_RE = re.compile(r"(?P<prefix>\]\()(?P<body><[^>\r\n]+>|[^)\r\n]+)(?P<close>\))")


def split_link_body(body: str) -> tuple[str, str, bool]:
    if body.startswith("<") and ">" in body:
        end = body.index(">")
        return body[1:end], body[end + 1 :], True
    parts = body.split(None, 1)
    return parts[0], (" " + parts[1]) if len(parts) == 2 else "", False


def is_external_target(target: str) -> bool:
    return target.lower().startswith(
        ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "//", "#")
    )


def is_illustrative_target(path_part: str) -> bool:
    """Skip links that are examples for the user's project, not source refs."""
    lowered = path_part.lower()
    if lowered in {"link", "url", "t", "2"}:
        return True
    if "/src/" in f"/{lowered}" or lowered.startswith("src/"):
        return True
    if lowered.startswith(("path/to/", "../path/to/")) or "ecc-tools" in lowered:
        return True
    if lowered.startswith("assets/") and not lowered.endswith(".md"):
        return True
    return bool(re.match(r"^\d{4}-[^/]+\.md$", lowered))


def rewrite_markdown(
    text: str,
    item: dict,
    source_to_dest: dict[Path, Path],
    tracked: set[str],
    link_stats: dict,
) -> str:
    source_file = item["current_source_file"]
    repo = item["repo"]
    destination_file = item["current_destination"]
    info = item["pack_info"]
    source_name = source_file.relative_to(repo).as_posix()
    if item["pack"] == "ecc" and source_name == "skills/ecc-tools-cost-audit/SKILL.md":
        # This names the user's separate checkout; it is not bundled by ECC.
        text = text.replace(
            "[ECC-Tools](../../ECC-Tools)",
            "ECC-Tools (source workspace path: `../../ECC-Tools`, not bundled)",
        )
    if (
        item["pack"] == "ecc"
        and source_name == "skills/remotion-video-creation/rules/charts.md"
    ):
        # The pinned source misspells the path of its tracked example asset.
        text = text.replace(
            "](assets/charts/bar-chart.tsx)", "](assets/charts-bar-chart.tsx)"
        )

    def replace(match: re.Match[str]) -> str:
        body = match.group("body")
        target, suffix, angle = split_link_body(body)
        if is_external_target(target):
            return match.group(0)
        parsed = urlsplit(target)
        path_part = unquote(parsed.path)
        if not path_part:
            return match.group(0)
        if path_part.startswith("/"):
            candidate = (repo / path_part.lstrip("/")).resolve()
        else:
            candidate = (source_file.parent / path_part).resolve()
        try:
            source_rel = candidate.relative_to(repo.resolve())
        except ValueError:
            return match.group(0)
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        query = f"?{parsed.query}" if parsed.query else ""
        if candidate in source_to_dest:
            relative = os.path.relpath(
                source_to_dest[candidate], destination_file.parent
            ).replace(os.sep, "/")
            replacement = f"{relative}{query}{fragment}"
            link_stats["local_rewrites"] += 1
        elif candidate.is_dir() and any(
            part.startswith(source_rel.as_posix().rstrip("/") + "/") for part in tracked
        ):
            replacement = f"{immutable_tree_url(info, source_rel)}{query}{fragment}"
            link_stats["immutable_rewrites"] += 1
        elif candidate.is_file() and source_rel.as_posix() in tracked:
            replacement = f"{immutable_url(info, source_rel)}{query}{fragment}"
            link_stats["immutable_rewrites"] += 1
        elif is_illustrative_target(path_part):
            link_stats["illustrative_ignored"] += 1
            return match.group(0)
        else:
            link_stats["unresolved"].append(
                {
                    "source": f"{item['pack']}/{item['source_rel'].as_posix()}",
                    "target": target,
                }
            )
            return match.group(0)
        rendered = f"<{replacement}>" if angle else replacement
        return f"{match.group('prefix')}{rendered}{suffix}{match.group('close')}"

    return LINK_RE.sub(replace, text)


def classify(item: dict) -> str:
    pack = item["pack"]
    rel = item["skill_rel"].relative_to(Path("skills")).as_posix()
    if pack in {"karpathy", "ponytail"}:
        return "engineering"
    if pack == "matt":
        if rel in LEARNING_MATT:
            return "learning"
        if rel in PRODUCTIVITY_MATT:
            return "productivity"
        if rel in HOST_MATT:
            return "host-integration"
        return "engineering"
    name = item["skill_rel"].name
    if name in HEALTH_ECC or name in RESEARCH_ECC:
        return "research"
    if name in DOCS_ECC or name in CONTENT_ECC:
        return "content"
    if name in BUSINESS_ECC or name in FINANCE_ECC:
        return "business"
    if name in MEDIA_ECC:
        return "media"
    if name in PRODUCTIVITY_ECC:
        return "productivity"
    if name in HOST_ECC:
        return "host-integration"
    if name in all_known_ecc_names():
        return "engineering"
    return "uncategorized"


_KNOWN_ECC_CACHE: set[str] | None = None


def all_known_ecc_names() -> set[str]:
    global _KNOWN_ECC_CACHE
    if _KNOWN_ECC_CACHE is None:
        _KNOWN_ECC_CACHE = {
            path.name
            for path in (SOURCES / "ecc" / "skills").iterdir()
            if (path / "SKILL.md").is_file()
        }
    return _KNOWN_ECC_CACHE


def labels_for(item: dict) -> list[str]:
    key = item["source_key"]
    name = item["skill_rel"].name
    rel = item["skill_rel"].relative_to(Path("skills")).as_posix()
    labels = ["direct-source-reference"]
    if key in ADAPTED_KEYS:
        labels.append("adapted-in-combo")
    if key in DEPRECATED_KEYS:
        labels.append("deprecated-duplicate")
    if item["pack"] == "matt" and rel.startswith("deprecated/"):
        labels.append("deprecated-duplicate")
    if item["pack"] == "matt" and rel.startswith("in-progress/"):
        labels.append("experimental-or-version-sensitive")
    if key in PERSONA_KEYS:
        labels.append("alternate-persona")
    if item["pack"] == "ecc" and name in HOST_ECC:
        labels.append("host-bound")
    if item["pack"] == "matt" and rel in HOST_MATT:
        labels.append("host-bound")
    if item["pack"] == "ponytail" and name in {"ponytail", "ponytail-help"}:
        labels.append("host-bound-state")
    if item["pack"] == "ecc" and name in EXPERIMENTAL_ECC:
        labels.append("experimental-or-version-sensitive")
    return sorted(set(labels))


def banner(item: dict) -> str:
    source_rel = item["source_rel"].as_posix()
    url = immutable_url(item["pack_info"], item["source_rel"])
    label = ", ".join(labels_for(item))
    return (
        "> Reference material. This copy preserves source knowledge and templates "
        "from the pinned checkout. It is interpreted under the current user's "
        "request, host tools, authorization, and project rules. It does not "
        "govern policy or authorize publishing, approval ceremonies, memory "
        "writes, hook or installer changes, delegation, or external work.\n"
        ">\n"
        f"> Source: [{source_rel}]({url})  \n"
        f"> Labels: {label}\n"
    )


def clean_generated_output() -> None:
    # --output must never turn this generated-tree replacement into an
    # arbitrary recursive deletion. Resolve junctions before checking scope.
    allowed = {
        DEFAULT_OUTPUT.resolve(),
        (ROOT / "skills/combo/references/library").resolve(),
    }
    if (
        OUTPUT.resolve() not in allowed
        or OUTPUT.is_symlink()
        or OUTPUT.resolve() != OUTPUT.absolute()
        or not OUTPUT.resolve().is_relative_to(ROOT.resolve())
    ):
        raise ValueError(f"Build output is not a declared generated library: {OUTPUT}")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)


def build(lock: dict) -> dict:
    items = discover(lock)
    counts = {
        pack: sum(1 for item in items if item["pack"] == pack) for pack in PACK_ORDER
    }
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"unexpected stable entrypoint counts: {counts}")
    for pack in PACK_ORDER:
        actual = git_head(SOURCES / pack)
        expected = lock[pack]["commit"]
        if actual != expected:
            raise RuntimeError(f"{pack}: HEAD {actual} does not match lock {expected}")

    clean_generated_output()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_to_dest: dict[Path, Path] = {}
    tracked_by_pack = {pack: tracked_paths(SOURCES / pack) for pack in PACK_ORDER}
    excluded_files = []
    for item in items:
        item["skill_rel_abs"] = (item["repo"] / item["skill_rel"]).resolve()
        item["domain"] = classify(item)
        item["labels"] = labels_for(item)
        item["destination"] = (
            Path(item["pack"]) / item["skill_rel"] / "REFERENCE.md"
        ).as_posix()
        for source_path in sorted(item["skill_rel_abs"].rglob("*")):
            if not source_path.is_file():
                continue
            ok, reason = should_copy(source_path, item["skill_rel_abs"])
            if not ok:
                excluded_files.append(
                    {
                        "pack": item["pack"],
                        "source": source_path.relative_to(item["repo"]).as_posix(),
                        "reason": reason,
                    }
                )
                continue
            source_to_dest[source_path.resolve()] = destination_for(
                item, source_path
            ).resolve()

    link_stats = {
        "local_rewrites": 0,
        "immutable_rewrites": 0,
        "illustrative_ignored": 0,
        "unresolved": [],
    }
    copied_files = []
    entries = []
    for item in items:
        item["support_files"] = []
        for source_path in sorted(item["skill_rel_abs"].rglob("*")):
            if not source_path.is_file():
                continue
            ok, _ = should_copy(source_path, item["skill_rel_abs"])
            if not ok:
                continue
            destination = source_to_dest[source_path.resolve()]
            destination.parent.mkdir(parents=True, exist_ok=True)
            item["current_source_file"] = source_path
            item["current_destination"] = destination
            if source_path.suffix.lower() in MARKDOWN_EXTS:
                body = source_path.read_text(encoding="utf-8", errors="replace")
                body = rewrite_markdown(
                    body,
                    item,
                    source_to_dest,
                    tracked_by_pack[item["pack"]],
                    link_stats,
                )
                if source_path.name == "SKILL.md":
                    body = banner(item) + "\n\n" + body
                destination.write_text(body, encoding="utf-8", newline="\n")
            else:
                shutil.copyfile(source_path, destination)
            dest_rel = destination.relative_to(OUTPUT).as_posix()
            if source_path != item["source_file"]:
                item["support_files"].append(dest_rel)
            copied_files.append(
                {
                    "pack": item["pack"],
                    "source": source_path.relative_to(item["repo"]).as_posix(),
                    "destination": dest_rel,
                }
            )
        entries.append(
            {
                "id": f"{item['pack']}/{item['skill_rel'].as_posix()}",
                "pack": item["pack"],
                "source": item["source_rel"].as_posix(),
                "source_url": immutable_url(item["pack_info"], item["source_rel"]),
                "immutable_commit": item["pack_info"]["commit"],
                "destination": item["destination"],
                "domain": item["domain"],
                "labels": item["labels"],
                "review_status": (
                    "body-reviewed-for-adaptation"
                    if item["source_key"] in ADAPTED_KEYS
                    else "metadata-classified"
                ),
                "support_files": sorted(item["support_files"]),
            }
        )

    domain_counts = {domain: 0 for domain in DOMAINS}
    label_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    for entry in entries:
        domain_counts[entry["domain"]] += 1
        review_counts[entry["review_status"]] = (
            review_counts.get(entry["review_status"], 0) + 1
        )
        for label in entry["labels"]:
            label_counts[label] = label_counts.get(label, 0) + 1

    manifest = {
        "schema_version": 1,
        "generated_by": "scripts/build-full-library.py",
        "purpose": "Pinned reference-only source library; not an active skill router.",
        "stable_entrypoint_rule": (
            "A direct source entrypoint is a direct SKILL.md under a pack skills "
            "directory. Nested support SKILL.md files are renamed REFERENCE.md."
        ),
        "source_packs": [
            lock[pack] | {"pack": pack, "stable_entrypoints": counts[pack]}
            for pack in PACK_ORDER
        ],
        "counts": {
            "stable_entrypoints": sum(counts.values()),
            "copied_files": len(copied_files),
            "excluded_files": len(excluded_files),
            "domain_entries": domain_counts,
            "labels": dict(sorted(label_counts.items())),
            "review_status": dict(sorted(review_counts.items())),
        },
        "entries": entries,
        "copied_files": copied_files,
        "excluded_files": excluded_files,
        "link_stats": link_stats,
    }
    write_indexes(manifest)
    manifest["file_hashes"] = {
        path.relative_to(OUTPUT).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(OUTPUT.rglob("*"))
        if path.is_file()
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_audit(manifest)
    return manifest


def engineering_group(entry: dict) -> str:
    """Choose a short navigation bucket for the large engineering catalog."""
    source = Path(entry["source"]).parent.name.lower().replace("_", "-")
    language_tokens = (
        "angular",
        "bun",
        "cpp",
        "csharp",
        "dart",
        "django",
        "dotnet",
        "fastapi",
        "flutter",
        "golang",
        "java",
        "javascript",
        "kotlin",
        "nestjs",
        "nextjs",
        "node",
        "python",
        "react",
        "rust",
        "spring",
        "swift",
        "typescript",
        "vue",
        "svelte",
        "tailwind",
        "laravel",
        "quarkus",
        "nuxt4",
        "perl",
        "fsharp",
        "jpa",
        "vite",
        "tinystruct",
        "android",
        "compose",
    )
    data_tokens = (
        "database",
        "-db",
        "data",
        "ml",
        "model",
        "mle",
        "recsys",
        "sql",
        "postgres",
        "prisma",
        "redis",
        "inference",
        "training",
        "embedding",
        "vector",
        "etl",
        "pytorch",
        "clickhouse",
    )
    infrastructure_tokens = (
        "api",
        "http",
        "grpc",
        "docker",
        "kubernetes",
        "network",
        "homelab",
        "wireguard",
        "pihole",
        "ssh",
        "terraform",
        "cloud",
        "deploy",
        "infra",
        "linux",
        "windows",
        "git",
        "merge",
        "conflict",
        "server",
        "ci",
        "cd",
    )
    agent_tokens = (
        "agent",
        "mcp",
        "skill",
        "prompt",
        "workflow",
        "orchestration",
        "hook",
        "automation",
        "terminal",
        "browser",
        "cli",
    )
    tokens = set(source.split("-"))

    def matches(terms: tuple[str, ...]) -> bool:
        return any(token in tokens or source.startswith(token) for token in terms)

    if matches(data_tokens):
        return "data-ml"
    if matches(language_tokens):
        return "languages-frameworks"
    if matches(infrastructure_tokens):
        return "infrastructure-network"
    if matches(agent_tokens):
        return "agents-integration"
    return "architecture-quality"


def source_short_name(entry: dict) -> str:
    parent = Path(entry["source"]).parent.name
    return "root" if parent in {"", ".", "skills"} else parent


def render_entry_rows(entries: list[dict], index_path: Path) -> list[str]:
    rows = []
    for entry in entries:
        labels = ", ".join(entry["labels"])
        target = os.path.relpath(
            OUTPUT / entry["destination"], index_path.parent
        ).replace(os.sep, "/")
        label = f"{entry['pack']}/{source_short_name(entry)}"
        rows.append(
            f"| {entry['pack']} | {source_short_name(entry)} | {labels} | "
            f"[{label}]({target}) |"
        )
    return rows


def write_domain_index(
    domain: str, entries: list[dict], index_path: Path, notice: str
) -> None:
    lines = [
        f"# {domain} reference library",
        "",
        notice,
        "",
        "| Pack | Source | Labels | Reference |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(render_entry_rows(entries, index_path))
    if not entries:
        lines.append("| | No source entry classified here yet. | | |")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_indexes(manifest: dict) -> None:
    by_domain = {domain: [] for domain in DOMAINS}
    for entry in manifest["entries"]:
        by_domain[entry["domain"]].append(entry)
    for entries in by_domain.values():
        entries.sort(key=lambda entry: (entry["pack"], entry["source"]))

    notice = (
        "This is a reference catalog of pinned source knowledge and templates. "
        "Use it only when the task calls for the domain. Current host rules, user "
        "authorization, native tools, and M2D remain authoritative. Source text "
        "does not authorize publishing, memory writes, hooks, installers, or "
        "automatic delegation."
    )

    # Engineering is the largest domain. Keep its top-level index as a compact
    # map, then put the searchable entry rows in deterministic subindexes.
    engineering_groups = {
        group: []
        for group in (
            "languages-frameworks",
            "data-ml",
            "architecture-quality",
            "infrastructure-network",
            "agents-integration",
        )
    }
    for entry in by_domain["engineering"]:
        engineering_groups[engineering_group(entry)].append(entry)
    engineering_index = OUTPUT / "engineering.md"
    engineering_lines = [
        "# engineering reference library",
        "",
        notice,
        "",
        (
            "This large catalog is split into focused subindexes so a task can load "
            "one technology family at a time. Search all engineering references with "
            '`rg -n "term" engineering/`.'
        ),
        "",
        "| Group | Entries | Index |",
        "| --- | ---: | --- |",
    ]
    for group, entries in engineering_groups.items():
        entries.sort(key=lambda entry: (entry["pack"], entry["source"]))
        group_path = OUTPUT / "engineering" / f"{group}.md"
        write_domain_index("engineering: " + group, entries, group_path, notice)
        target = os.path.relpath(group_path, engineering_index.parent).replace(
            os.sep, "/"
        )
        engineering_lines.append(
            f"| {group} | {len(entries)} | [{group}.md]({target}) |"
        )
    engineering_lines.extend(
        [
            "",
            (
                "The manifest records each exact source path and immutable commit. "
                "Rows in the subindexes use concise source names; follow a reference "
                "link or consult curation/full-library.json for full provenance."
            ),
        ]
    )
    engineering_index.write_text("\n".join(engineering_lines) + "\n", encoding="utf-8")

    for domain in DOMAINS:
        if domain == "engineering":
            continue
        write_domain_index(domain, by_domain[domain], OUTPUT / f"{domain}.md", notice)

    counts = manifest["counts"]["domain_entries"]
    lines = [
        "# Full source reference library",
        "",
        notice,
        "",
        (
            "Every direct source skill is retained as REFERENCE.md. Safe support "
            "Markdown and referenced assets stay beside the source entry. Scripts, "
            "installers, credentials, and build trees remain immutable upstream "
            "links or are recorded in the manifest."
        ),
        "",
        "## Domain indexes",
        "",
        "| Domain | Entries | Index |",
        "| --- | ---: | --- |",
    ]
    for domain in DOMAINS:
        lines.append(f"| {domain} | {counts[domain]} | [{domain}.md]({domain}.md) |")
    lines.extend(
        [
            "",
            "## Provenance and licenses",
            "",
            (
                "Each entry links to its immutable GitHub source commit. Package license "
                "notices are supplied by the sibling ../licenses directory: "
                "[Karpathy](../licenses/karpathy.txt), [Ponytail](../licenses/ponytail.txt), "
                "[Matt](../licenses/matt.txt), and [ECC](../licenses/ecc.txt)."
            ),
            "",
            (
                "The generated manifest at curation/full-library.json records exact source "
                "paths, commits, destinations, labels, support files, excluded files, "
                "and rewritten-link statistics."
            ),
        ]
    )
    (OUTPUT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def current_combo_stats() -> dict:
    workflow_dir = ROOT / "skills" / "combo" / "workflows"
    practice_dir = ROOT / "skills" / "combo" / "practices"
    specialist_dir = ROOT / "skills" / "combo" / "specialists"
    return {
        "entrypoints": sum(
            int(path.is_file())
            for path in (
                ROOT / "skills" / "combo" / "SKILL.md",
                ROOT / "skills" / "combo-maintain" / "SKILL.md",
            )
        ),
        "workflows": len(list(workflow_dir.glob("*.md")))
        if workflow_dir.is_dir()
        else 0,
        "practices": len(list(practice_dir.glob("*.md")))
        if practice_dir.is_dir()
        else 0,
        "specialist_notes": (
            len(
                [
                    path
                    for path in specialist_dir.glob("*.md")
                    if path.name != "INDEX.md"
                ]
            )
            if specialist_dir.is_dir()
            else 0
        ),
    }


def write_audit(manifest: dict) -> None:
    source_counts = {
        pack["pack"]: pack["stable_entrypoints"] for pack in manifest["source_packs"]
    }
    audit = {
        "schema_version": 2,
        "generated_by": "scripts/build-full-library.py",
        "mode": "read-only coverage inventory plus reference-library build stats",
        "date": "2026-09-09",
        "source_commits": {
            pack["pack"]: {"url": pack["url"], "commit": pack["commit"]}
            for pack in manifest["source_packs"]
        },
        "direct_source_entrypoints": source_counts
        | {"total": sum(source_counts.values())},
        "current_combo": current_combo_stats(),
        "reference_library": {
            "destination": "candidates/common/combo/references/library",
            "entries": manifest["counts"]["stable_entrypoints"],
            "domain_entries": manifest["counts"]["domain_entries"],
            "labels": manifest["counts"]["labels"],
            "review_status": manifest["counts"]["review_status"],
            "copied_files": manifest["counts"]["copied_files"],
            "excluded_files": manifest["counts"]["excluded_files"],
            "link_stats": {
                "local_rewrites": manifest["link_stats"]["local_rewrites"],
                "immutable_rewrites": manifest["link_stats"]["immutable_rewrites"],
                "unresolved": len(manifest["link_stats"]["unresolved"]),
            },
        },
        "decisions": {
            "software_and_all_types": (
                "Both experiment arms should expose the same reference domains "
                "and source revisions; vary discovery and entrypoint shape only."
            ),
            "active_router": (
                "The A/B arms use the same full-domain reference library. "
                "The selected shipping layout and evidence are in audit/ab/DECISION.md; "
                "domain files remain indexes, not global skill entrypoints."
            ),
            "host_bound": (
                "Memory, hooks, installers, orchestration, notifications, and "
                "native UI assumptions are reference-only. M2D and host tools "
                "remain authoritative."
            ),
        },
        "limits": [
            (
                "Only selected sources were body-reviewed for prior adaptation. "
                "Remaining entries are retained and metadata-classified."
            ),
            (
                "Domain labels use explicit source-name maps with engineering as the "
                "ECC default and uncategorized as the future-name fallback."
            ),
            (
                "Version-sensitive and regulated material still requires current "
                "official-source verification at task time."
            ),
        ],
    }
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    counts = audit["direct_source_entrypoints"]
    combo = audit["current_combo"]
    library = audit["reference_library"]
    lines = [
        "# Four-pack source coverage and full-library build",
        "",
        (
            "Generated read-only audit. A direct source entrypoint means a source "
            "skill directory with SKILL.md; nested support files are not counted "
            "as separate skills."
        ),
        "",
        "## Source counts",
        "",
        "| Pack | Immutable commit | Direct source entrypoints |",
        "| --- | --- | ---: |",
    ]
    for pack in manifest["source_packs"]:
        lines.append(
            f"| {pack['pack']} | {pack['commit']} | {pack['stable_entrypoints']} |"
        )
    lines.append(f"| Total | | {counts['total']} |")
    lines.extend(
        [
            "",
            "## Current combo baseline",
            "",
            (
                f"The baseline has {combo['entrypoints']} entrypoints, "
                f"{combo['workflows']} workflow documents, {combo['practices']} "
                f"practice documents, and {combo['specialist_notes']} specialist notes. "
                f"The common library retains all {library['entries']} source entrypoints "
                "as reference material."
            ),
            "",
            "## Domain inventory",
            "",
            "| Domain | Entries |",
            "| --- | ---: |",
        ]
    )
    for domain, count in library["domain_entries"].items():
        lines.append(f"| {domain} | {count} |")
    lines.extend(
        [
            "",
            "## Labels and review status",
            "",
            (
                "Labels overlap. adapted-in-combo identifies the previously reviewed "
                "working subset. host-bound, experimental-or-version-sensitive, "
                "alternate-persona, and deprecated-duplicate identify constraints, "
                "not runtime authority."
            ),
            "",
            (
                "The builder copied safe support files, excluded scripts/installers/"
                "credentials/build trees, rewrote copied local links, and used immutable "
                "source URLs for excluded tracked files."
            ),
            "",
            (
                "Both A/B experiment arms should expose these same domain indexes and "
                "pinned revisions. Vary discovery shape, not capability access."
            ),
            "",
            "## Limits",
            "",
            (
                "- Only selected sources were body-reviewed for prior adaptation; the "
                "remaining entries are retained and metadata-classified."
            ),
            "- Domain labels use explicit maps with an uncategorized fallback.",
            (
                "- Version-sensitive or regulated advice needs current official-source "
                "verification at task time."
            ),
        ]
    )
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check() -> int:
    if not MANIFEST_PATH.is_file():
        print(f"missing manifest: {MANIFEST_PATH}", file=sys.stderr)
        return 1
    manifest = read_json(MANIFEST_PATH)
    errors = []
    expected_hashes = manifest.get("file_hashes", {})
    actual_hashes = {
        path.relative_to(OUTPUT).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(OUTPUT.rglob("*"))
        if path.is_file()
    }
    if not expected_hashes or actual_hashes != expected_hashes:
        errors.append("generated file set or contents drifted from the build manifest")
    heads = {pack: git_head(SOURCES / pack) for pack in PACK_ORDER}
    entries = manifest.get("entries", [])
    if manifest.get("counts", {}).get("stable_entrypoints") != sum(
        EXPECTED_COUNTS.values()
    ):
        errors.append("manifest stable entrypoint count is not 330")
    seen_destinations = set()
    for entry in entries:
        destination = OUTPUT / entry["destination"]
        if destination in seen_destinations:
            errors.append(f"duplicate destination: {entry['destination']}")
        seen_destinations.add(destination)
        if not destination.is_file():
            errors.append(f"missing generated reference: {entry['destination']}")
        if destination.name == "SKILL.md":
            errors.append(f"nested skill entrypoint: {entry['destination']}")
        try:
            actual = heads[entry["pack"]]
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"cannot read {entry['pack']} HEAD: {exc}")
        else:
            if actual != entry["immutable_commit"]:
                errors.append(f"{entry['pack']} HEAD drifted from manifest")
        for support in entry.get("support_files", []):
            if not (OUTPUT / support).is_file():
                errors.append(f"missing support file: {support}")
    if manifest.get("link_stats", {}).get("unresolved"):
        errors.append(
            f"unresolved local links: {len(manifest['link_stats']['unresolved'])}"
        )
    for path in OUTPUT.rglob("SKILL.md"):
        errors.append(f"nested SKILL.md remains: {path.relative_to(OUTPUT)}")
    for domain in DOMAINS:
        if not (OUTPUT / f"{domain}.md").is_file():
            errors.append(f"missing domain index: {domain}.md")
    if errors:
        print("FULL_LIBRARY_CHECK_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "FULL_LIBRARY_CHECK_OK "
        f"entries={len(entries)} files={manifest['counts']['copied_files']} "
        f"domains={len(DOMAINS)} links={manifest['link_stats']['local_rewrites']}local/"
        f"{manifest['link_stats']['immutable_rewrites']}immutable"
    )
    return 0


def main() -> int:
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="library output directory, relative to the workspace root",
    )
    args = parser.parse_args()
    output = Path(args.output)
    OUTPUT = output if output.is_absolute() else ROOT / output
    if args.check:
        return check()
    lock_raw = read_json(LOCK_PATH)
    lock = {item["pack"]: item for item in lock_raw}
    missing = [pack for pack in PACK_ORDER if pack not in lock]
    if missing:
        raise RuntimeError(f"missing lock entries: {missing}")
    manifest = build(lock)
    print(
        "FULL_LIBRARY_BUILT "
        f"entries={manifest['counts']['stable_entrypoints']} "
        f"files={manifest['counts']['copied_files']} "
        f"excluded={manifest['counts']['excluded_files']}"
    )
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
