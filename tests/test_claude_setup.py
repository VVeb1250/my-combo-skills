from __future__ import annotations

import copy
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "combo_setup_claude", ROOT / "scripts/setup-claude.py"
)
assert SPEC is not None and SPEC.loader is not None
claude_setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(claude_setup)


class ClaudeSetupTests(unittest.TestCase):
    def _mini_root(self, root: Path) -> None:
        """Create the smallest valid source tree for plan edge cases."""

        for package in claude_setup.EXPECTED_PACKAGES:
            package_root = root / "skills" / package
            package_root.mkdir(parents=True, exist_ok=True)
            (package_root / "SKILL.md").write_text(
                f"---\nname: {package}\ndescription: Mini {package}\n---\n\nBody.\n",
                encoding="utf-8",
            )
        adapter_root = root / "adapters" / "claude"
        practices = root / "skills/combo/practices"
        practices.mkdir(parents=True)
        (practices / "project-knowledge-rule.md").write_text(
            "## Shared documentation rule\nPreserve rationale.\n", encoding="utf-8"
        )
        (adapter_root / "agents").mkdir(parents=True, exist_ok=True)
        (adapter_root / "POLICY.md").write_text(
            "## Mini policy\nUse the selected workflow.\n", encoding="utf-8"
        )
        (adapter_root / "agents" / "combo-worker.md").write_text(
            "---\nname: combo-worker\ndescription: Mini worker\nmodel: inherit\n---\n\n"
            "Complete the delegated task.\n",
            encoding="utf-8",
        )

    def _mini_manifest(self) -> dict:
        return copy.deepcopy(claude_setup.load_manifest())

    def test_both_hosts_load_updated_rule_from_one_source(self):
        spec = importlib.util.spec_from_file_location(
            "combo_setup", ROOT / "scripts/setup.py"
        )
        assert spec is not None and spec.loader is not None
        codex_setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(codex_setup)
        manifest = self._mini_manifest()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._mini_root(root)
            rule = root / "skills/combo/practices/project-knowledge-rule.md"
            with (
                mock.patch.object(claude_setup, "ROOT", root),
                mock.patch.object(codex_setup, "ROOT", root),
            ):
                for body in (
                    "## Shared rule\nFirst revision.",
                    "## Shared rule\nRevised rationale.",
                ):
                    rule.write_text(body, encoding="utf-8")
                    raw = b"# Preferences\nKeep me.\n"
                    for rendered in (
                        claude_setup.render_claude(raw, manifest),
                        codex_setup.render_agents(
                            raw, {"global_pointer": "Use Combo."}
                        ),
                    ):
                        self.assertEqual(rendered.count(body.encode()), 1)
                        self.assertEqual(rendered.count(raw), 1)
                rule.unlink()
                with self.assertRaises(FileNotFoundError):
                    claude_setup.render_claude(raw, manifest)
                with self.assertRaises(FileNotFoundError):
                    codex_setup.render_agents(raw, {"global_pointer": "Use Combo."})

    def test_render_settings_preserves_unowned_semantics_and_is_idempotent(self):
        manifest = claude_setup.load_manifest()
        raw = json.dumps(
            {
                "theme": "dark",
                "custom": {"keep": [1, "สอง"]},
                "enabledPlugins": {
                    "ecc@ecc": True,
                    "other@test": True,
                },
                "skillOverrides": {
                    "custom-skill": "on",
                    "multi-model-orchestrator": "on",
                },
            },
            ensure_ascii=False,
        ).encode("utf-8")

        rendered = claude_setup.render_settings(raw, manifest)
        values = json.loads(rendered.decode("utf-8"))
        self.assertEqual(values["theme"], "dark")
        self.assertEqual(values["custom"], {"keep": [1, "สอง"]})
        self.assertTrue(values["enabledPlugins"]["other@test"])
        self.assertFalse(values["enabledPlugins"]["ecc@ecc"])
        self.assertNotIn("ecc-hubs@bundle", values["enabledPlugins"])
        self.assertEqual(values["skillOverrides"]["custom-skill"], "on")
        self.assertEqual(values["skillOverrides"]["multi-model-orchestrator"], "off")
        self.assertEqual(rendered, claude_setup.render_settings(rendered, manifest))

    def test_exact_legacy_section_handles_crlf_and_preserves_outside_bytes(self):
        manifest = claude_setup.load_manifest()
        legacy = manifest["legacy_owned_section"].replace("\n", "\r\n").encode()
        suffix = "\r\n# Memory: personal\r\nKeep this exactly: 雪\r\n".encode()
        raw = legacy + suffix

        outside_before = claude_setup.outside_owned_policy(raw, manifest)
        rendered = claude_setup.render_claude(
            raw, manifest, policy="## Current policy\nKeep the router."
        )
        self.assertEqual(outside_before, suffix)
        self.assertEqual(
            claude_setup.outside_owned_policy(rendered, manifest), outside_before
        )
        self.assertEqual(
            rendered,
            claude_setup.render_claude(
                rendered, manifest, policy="## Current policy\nKeep the router."
            ),
        )
        with self.assertRaises(ValueError):
            claude_setup.render_claude(
                b"## Skill discipline\r\nInvented legacy wording\r\n",
                manifest,
                policy="## Current policy",
            )

    def test_full_build_plan_uses_real_sources_and_leaves_codex_and_config_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "home"
            codex = home / ".codex"
            codex.mkdir(parents=True)
            codex_config = b'model = "custom"\r\n[plugins]\r\nkeep = true\r\n'
            codex_agents = b"# Codex instructions\r\nKeep this file.\r\n"
            unrelated_config = b"private = true\r\n"
            (codex / "config.toml").write_bytes(codex_config)
            (codex / "AGENTS.md").write_bytes(codex_agents)
            (home / "config.toml").write_bytes(unrelated_config)

            changes = claude_setup.build_plan(home)
            target_root = home / claude_setup.CLAUDE_DIR
            paths = {Path(change["path"]) for change in changes}
            relative_paths = {
                path.relative_to(target_root).as_posix() for path in paths
            }
            self.assertIn("skills/combo/SKILL.md", relative_paths)
            self.assertIn("agents/combo-worker.md", relative_paths)
            self.assertIn("CLAUDE.md", relative_paths)
            self.assertIn("settings.json", relative_paths)
            self.assertTrue(all(path.is_relative_to(target_root) for path in paths))
            self.assertEqual((codex / "config.toml").read_bytes(), codex_config)
            self.assertEqual((codex / "AGENTS.md").read_bytes(), codex_agents)
            self.assertEqual((home / "config.toml").read_bytes(), unrelated_config)

    def test_python_cache_entries_are_never_installed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            home = Path(temporary) / "home"
            self._mini_root(root)
            cache = root / "skills/combo/tools/__pycache__"
            cache.mkdir(parents=True)
            (cache / "project_kb.cpython-314.pyc").write_bytes(b"cache")
            (root / "skills/combo/tools/orphan.pyo").write_bytes(b"cache")
            manifest = self._mini_manifest()

            with mock.patch.object(claude_setup, "ROOT", root):
                changes = claude_setup.build_plan(home, manifest)
            paths = {
                Path(change["path"]).relative_to(home / ".claude").as_posix()
                for change in changes
            }
            self.assertIn("skills/combo/SKILL.md", paths)
            self.assertFalse(
                any(
                    "__pycache__" in path or path.endswith((".pyc", ".pyo"))
                    for path in paths
                )
            )

    def test_claude_router_override_keeps_every_source_practice_link(self):
        # The Claude override is a maintained copy of the portable router. A
        # stale copy silently hides newly added practices from Claude, so guard
        # the practice index rather than only the host-specific wording.
        practice_link = re.compile(r"\(practices/[^)]+\.md\)")
        source = (ROOT / "skills/combo/SKILL.md").read_text(encoding="utf-8")
        override = (
            ROOT / "adapters/claude/overrides/combo/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            set(practice_link.findall(source)),
            set(practice_link.findall(override)),
        )

    def test_unowned_file_inside_package_refuses_plan_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            home = Path(temporary) / "home"
            self._mini_root(root)
            collision = home / ".claude" / "skills" / "combo" / "user-note.md"
            collision.parent.mkdir(parents=True)
            collision.write_bytes(b"user-owned collision")
            manifest = self._mini_manifest()

            with mock.patch.object(
                claude_setup, "ROOT", root
            ), self.assertRaisesRegex(ValueError, "collides"):
                claude_setup.build_plan(home, manifest)
            self.assertEqual(collision.read_bytes(), b"user-owned collision")

    def test_unowned_existing_desired_target_refuses_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            root = temporary_root / "source"
            self._mini_root(root)
            manifest = self._mini_manifest()

            for relative in ("skills/combo/SKILL.md", "agents/combo-worker.md"):
                with self.subTest(relative=relative):
                    home = temporary_root / ("home-" + relative.replace("/", "-"))
                    target = home / ".claude" / relative
                    target.parent.mkdir(parents=True)
                    target.write_bytes(b"user-owned bytes")

                    with mock.patch.object(
                        claude_setup, "ROOT", root
                    ), self.assertRaisesRegex(ValueError, "collides"):
                        claude_setup.build_plan(home, manifest)
                    self.assertEqual(target.read_bytes(), b"user-owned bytes")

    def test_edited_owned_file_stops_plan(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            home = Path(temporary) / "home"
            target = home / ".claude"
            self._mini_root(root)
            stale = target / "skills" / "combo" / "stale.md"
            index = target / claude_setup.OWNERSHIP_INDEX
            stale.parent.mkdir(parents=True)
            stale.write_bytes(b"user edit")
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "package": "combo",
                        "files": [
                            {
                                "path": "skills/combo/stale.md",
                                "sha256": claude_setup.digest(b"original"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest = self._mini_manifest()

            with mock.patch.object(
                claude_setup, "ROOT", root
            ), self.assertRaisesRegex(ValueError, "drifted"):
                claude_setup.build_plan(home, manifest)
            self.assertEqual(stale.read_bytes(), b"user edit")

    def test_deleted_owned_file_stops_plan(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            home = Path(temporary) / "home"
            target = home / ".claude"
            self._mini_root(root)
            index = target / claude_setup.OWNERSHIP_INDEX
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "package": "combo",
                        "files": [
                            {
                                "path": "skills/combo/deleted.md",
                                "sha256": claude_setup.digest(b"original"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest = self._mini_manifest()

            with mock.patch.object(
                claude_setup, "ROOT", root
            ), self.assertRaisesRegex(ValueError, "drifted"):
                claude_setup.build_plan(home, manifest)

    def test_receipt_rollback_restores_files_and_preserves_sibling(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "claude"
            target.mkdir()
            existing = target / "existing.md"
            created = target / "created.md"
            sibling = target / "unmanaged.md"
            existing.write_bytes(b"before\r\n")
            sibling.write_bytes(b"leave me")
            receipt = claude_setup.apply(
                [
                    {"path": existing, "before": b"before\r\n", "after": b"after"},
                    {"path": created, "before": None, "after": b"created"},
                ],
                root / "backup",
                target,
            )
            self.assertIsNotNone(receipt)
            assert receipt is not None
            self.assertEqual(existing.read_bytes(), b"after")
            self.assertEqual(created.read_bytes(), b"created")

            claude_setup.rollback(receipt, target)
            self.assertEqual(existing.read_bytes(), b"before\r\n")
            self.assertFalse(created.exists())
            self.assertEqual(sibling.read_bytes(), b"leave me")
            self.assertEqual(json.loads(receipt.read_text())["status"], "rolled_back")

    def test_receipt_rollback_refuses_later_edit_before_touching_other_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "claude"
            target.mkdir()
            existing = target / "existing.md"
            created = target / "created.md"
            existing.write_bytes(b"before")
            receipt = claude_setup.apply(
                [
                    {"path": existing, "before": b"before", "after": b"after"},
                    {"path": created, "before": None, "after": b"created"},
                ],
                root / "backup",
                target,
            )
            assert receipt is not None
            existing.write_bytes(b"user edit")

            with self.assertRaisesRegex(ValueError, "later edit"):
                claude_setup.rollback(receipt, target)
            self.assertEqual(existing.read_bytes(), b"user edit")
            self.assertEqual(created.read_bytes(), b"created")
            self.assertEqual(json.loads(receipt.read_text())["status"], "applied")

    def test_path_traversal_is_rejected_at_manifest_and_target_boundaries(self):
        for value in ("../outside", "/outside", "C:/outside", "skills\\combo"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                claude_setup._relative(value, "test")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "claude"
            root.mkdir()
            with self.assertRaises(ValueError):
                claude_setup._assert_target(root / ".." / "outside", root)
            index = root / claude_setup.OWNERSHIP_INDEX
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_text(
                json.dumps(
                    {
                        "files": [
                            {
                                "path": "skills/combo/../outside.md",
                                "sha256": "0" * 64,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                claude_setup._read_owned_index(
                    index,
                    root,
                    {"combo": "skills/combo"},
                    {},
                )

    def test_symlink_on_owned_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "claude"
            root.mkdir()
            outside = Path(temporary) / "outside"
            outside.mkdir()
            linked = root / "skills" / "combo" / "linked"
            linked.parent.mkdir(parents=True)
            try:
                linked.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                # Windows may lack symlink privilege. Exercise the same guard
                # without changing any real checkout path.
                with mock.patch.object(
                    claude_setup,
                    "_is_link",
                    side_effect=lambda path: Path(path) != root,
                ), self.assertRaises(ValueError):
                    claude_setup._assert_target(linked / "file.md", root)
            else:
                with self.assertRaises(ValueError):
                    claude_setup._assert_target(linked / "file.md", root)

    def test_active_override_codex_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            home = Path(temporary) / "home"
            self._mini_root(root)
            override = root / "adapters" / "claude" / "overrides" / "combo"
            override.mkdir(parents=True)
            (override / "SKILL.md").write_text(
                "---\nname: combo\ndescription: Mini override\n---\n\n"
                "Invoke $combo for routing.\n",
                encoding="utf-8",
            )
            manifest = self._mini_manifest()

            with mock.patch.object(
                claude_setup, "ROOT", root
            ), self.assertRaisesRegex(ValueError, "Codex invocation marker"):
                claude_setup.build_plan(home, manifest)


if __name__ == "__main__":
    unittest.main()
