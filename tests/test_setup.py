import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC=importlib.util.spec_from_file_location('combo_setup',Path(__file__).resolve().parents[1]/'scripts/setup.py')
setup=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)

class SetupTests(unittest.TestCase):
    def test_manifest_package_roots_accept_declared_combo_siblings(self):
        manifest = {
            'source_roots': [
                {'source': 'skills/combo', 'target': 'skills/combo'},
                {'source': 'skills/combo-maintain', 'target': 'skills/combo-maintain'},
                {'source': 'skills/combo-deliver', 'target': 'skills/combo-deliver'},
            ]
        }
        self.assertEqual(
            setup.manifest_package_names(manifest),
            {'combo', 'combo-maintain', 'combo-deliver'},
        )

    def test_manifest_package_roots_reject_remaps_and_traversal(self):
        base = {'source_roots': [{'source': 'skills/combo', 'target': 'skills/combo'}]}
        for source, target in (
            ('skills/combo', 'skills/elsewhere'),
            ('skills/../secret', 'skills/../secret'),
            ('skills/Combo-extra', 'skills/Combo-extra'),
            ('skills/combo_extra', 'skills/combo_extra'),
        ):
            manifest = {'source_roots': [{'source': source, 'target': target}]}
            with self.assertRaises(ValueError):
                setup.manifest_package_names(manifest)
        self.assertEqual(setup.manifest_package_names(base), {'combo'})

    def test_owned_index_rejects_undeclared_package_and_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); home = root/'home'; codex = home/'.codex'; codex.mkdir(parents=True)
            index = codex/'skills/combo/.combo-owned.json'; index.parent.mkdir(parents=True)
            manifest = {
                'source_roots': [
                    {'source': 'skills/combo', 'target': 'skills/combo'},
                    {'source': 'skills/combo-maintain', 'target': 'skills/combo-maintain'},
                ],
                'ownership_index': 'skills/combo/.combo-owned.json',
            }
            for owned_path in ('skills/other/file.md', 'skills/combo/../outside.md'):
                index.write_text(json.dumps({'files': [{'path': owned_path, 'sha256': '0' * 64}]}), encoding='utf-8')
                with self.assertRaises(ValueError):
                    setup._read_owned_index(index, home, manifest)

    def test_ownership_bytes_includes_declared_sibling_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); home = root/'home'; codex = home/'.codex'; codex.mkdir(parents=True)
            manifest = {
                'source_roots': [
                    {'source': 'skills/combo', 'target': 'skills/combo'},
                    {'source': 'skills/combo-maintain', 'target': 'skills/combo-maintain'},
                    {'source': 'skills/combo-deliver', 'target': 'skills/combo-deliver'},
                ]
            }
            files = {
                codex/'skills/combo-deliver/SKILL.md': b'wrapper',
                codex/'skills/combo-maintain/SKILL.md': b'maintain',
                codex/'agents/combo-worker.toml': b'role',
                codex/'config.toml': b'preserve',
            }
            rows = json.loads(setup._ownership_bytes(files, home, manifest))['files']
            self.assertEqual(
                {row['path'] for row in rows},
                {'skills/combo-deliver/SKILL.md', 'skills/combo-maintain/SKILL.md', 'agents/combo-worker.toml'},
            )

    def test_config_preserves_unrelated_values_and_is_idempotent(self):
        raw=b'model = "custom"\n[mcp_servers.example]\ncommand = "keep-me"\n[plugins."ecc@ecc"]\nenabled = true\n[plugins."other@test"]\nenabled = true\n'
        manifest={'disable_plugins':['ecc@ecc'],'rows':[{'mechanism':'disable-local','path':str(setup.REAL_HOME/'.agents/skills/tdd/SKILL.md')}]}
        first=setup.render_config(raw,manifest,setup.REAL_HOME)
        values=setup.tomllib.loads(first.decode())
        self.assertEqual(values['model'],'custom')
        self.assertEqual(values['mcp_servers']['example']['command'],'keep-me')
        self.assertTrue(values['plugins']['other@test']['enabled'])
        self.assertFalse(values['plugins']['ecc@ecc']['enabled'])
        self.assertFalse(values['skills']['config'][0]['enabled'])
        self.assertEqual(first,setup.render_config(first,manifest,setup.REAL_HOME))

    def test_memory_and_preferences_preserved_exactly(self):
        raw=b'# Preferences\nKeep this exactly\n\n# Codex Instructions\nOld install\n\n## Local rule\nKeep this too\n\n## Memory: canonical\nPrivate rules\n'
        result=setup.render_agents(raw)
        self.assertTrue(result.startswith(b'# Preferences\nKeep this exactly\n'))
        self.assertIn(b'## Local rule\nKeep this too', result)
        self.assertTrue(result.endswith(b'## Memory: canonical\nPrivate rules\n'))
        self.assertEqual(result,setup.render_agents(result))

    def test_global_pointer_is_neutral_and_manifest_driven(self):
        manifest = {
            'global_pointer': 'Use the selected Combo entry for this task.',
        }
        rendered = setup.render_agents(
            b'# Preferences\nKeep this\n',
            manifest,
        )
        self.assertIn(b'Use the selected Combo entry for this task.', rendered)
        self.assertNotIn(b'software engineering tasks', rendered)

    def test_apply_rollback_restores_bytes_and_removes_only_created_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); old=root/'existing'; new=root/'new'; sibling=root/'sibling'
            old.write_bytes(b'original\r\n'); sibling.write_bytes(b'untouched')
            receipt=setup.apply([{'path':old,'before':b'original\r\n','after':b'changed'},
                                 {'path':new,'before':None,'after':b'new'}],root/'backup')
            setup.rollback(receipt)
            self.assertEqual(old.read_bytes(),b'original\r\n')
            self.assertFalse(new.exists())
            self.assertEqual(sibling.read_bytes(),b'untouched')

    def test_rollback_refuses_later_user_edit_before_changing_any_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); a=root/'a'; b=root/'b'
            receipt=setup.apply([{'path':a,'before':None,'after':b'a'},
                                 {'path':b,'before':None,'after':b'b'}],root/'backup')
            b.write_bytes(b'user edit')
            with self.assertRaisesRegex(ValueError,'later edit'): setup.rollback(receipt)
            self.assertEqual(a.read_bytes(),b'a')
            self.assertEqual(b.read_bytes(),b'user edit')

    def _fake_codex_home(self, root):
        home=root/'home'; codex=home/'.codex'; codex.mkdir(parents=True)
        (codex/'config.toml').write_text(
            'model = "custom"\n'
            '[plugins."ecc@ecc"]\n'
            'enabled = true\n'
            '[plugins."other@test"]\n'
            'enabled = true\n', encoding='utf-8')
        (codex/'AGENTS.md').write_text(
            '# Preferences\nKeep this\n\n## Memory: canonical\nKeep memory\n',
            encoding='utf-8')
        return home, codex

    def test_build_plan_targets_only_live_packages_and_declared_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, codex=self._fake_codex_home(Path(tmp))
            changes=setup.build_plan(home)
            paths={Path(change['path']).relative_to(codex).as_posix() for change in changes}
            self.assertTrue(any(path.startswith('skills/combo/') for path in paths))
            self.assertTrue(any(path.startswith('skills/combo-maintain/') for path in paths))
            self.assertIn('agents/combo-worker.toml', paths)
            self.assertNotIn('skills/ecc-api-design/SKILL.md', paths)
            self.assertNotIn('skills/matt-plan/SKILL.md', paths)
            self.assertNotIn('hooks.json', paths)

    def test_python_cache_entries_are_never_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'source'
            package = root / 'skills/combo'
            (package / 'tools/__pycache__').mkdir(parents=True)
            (package / 'tools/__pycache__/project_kb.cpython-314.pyc').write_bytes(b'cache')
            (package / 'tools/orphan.pyc').write_bytes(b'cache')
            (package / 'SKILL.md').write_text(
                '---\nname: combo\ndescription: Mini\n---\n\nBody.\n', encoding='utf-8')
            (package / 'practices').mkdir()
            (package / 'practices/project-knowledge-rule.md').write_text('rule', encoding='utf-8')
            home = Path(tmp) / 'home'; codex = home / '.codex'; codex.mkdir(parents=True)
            (codex / 'config.toml').write_text('model = "custom"\n', encoding='utf-8')
            (codex / 'AGENTS.md').write_text('# Keep\n', encoding='utf-8')
            manifest = {
                'version': 2,
                'source_roots': [{'source': 'skills/combo', 'target': 'skills/combo'}],
                'ownership_index': 'skills/combo/.combo-owned.json',
                'global_pointer': 'Use Combo.',
            }
            with mock.patch.object(setup, 'ROOT', root):
                changes = setup.build_plan(home, manifest)
            paths = {Path(change['path']).relative_to(codex).as_posix() for change in changes}
            self.assertIn('skills/combo/SKILL.md', paths)
            self.assertFalse(
                any('__pycache__' in path or path.endswith(('.pyc', '.pyo')) for path in paths)
            )

    def test_owned_stale_file_is_deleted_and_restored_by_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, codex=self._fake_codex_home(Path(tmp))
            stale=codex/'skills/combo/removed.md'; stale.parent.mkdir(parents=True)
            stale.write_bytes(b'old generated note')
            index=codex/'skills/combo/.combo-owned.json'
            index.write_text(json.dumps({'version':2,'package':'combo','files':[
                {'path':'skills/combo/removed.md','sha256':setup.digest(stale.read_bytes())}
            ]}), encoding='utf-8')
            changes=setup.build_plan(home)
            self.assertTrue(any(change['path']==stale and change['after'] is None for change in changes))
            receipt=setup.apply(changes,Path(tmp)/'backup',codex)
            self.assertFalse(stale.exists())
            setup.rollback(receipt,codex)
            self.assertEqual(stale.read_bytes(),b'old generated note')

    def test_owned_stale_drift_blocks_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, codex=self._fake_codex_home(Path(tmp))
            stale=codex/'skills/combo/removed.md'; stale.parent.mkdir(parents=True)
            stale.write_bytes(b'user edit')
            index=codex/'skills/combo/.combo-owned.json'
            index.write_text(json.dumps({'version':2,'package':'combo','files':[
                {'path':'skills/combo/removed.md','sha256':setup.digest(b'old generated note')}
            ]}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'drifted'):
                setup.build_plan(home)
            self.assertEqual(stale.read_bytes(),b'user edit')

    def test_failed_atomic_write_restores_completed_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); target=root/'state'; target.mkdir(); a=target/'a'; b=target/'b'
            a.write_bytes(b'old a')
            original=setup._atomic_write
            def fail_on_b(path,data):
                if Path(path)==b:
                    raise OSError('seeded write failure')
                return original(path,data)
            with mock.patch.object(setup,'_atomic_write',side_effect=fail_on_b), self.assertRaisesRegex(OSError,'seeded write failure'):
                setup.apply([
                    {'path':a,'before':b'old a','after':b'new a'},
                    {'path':b,'before':None,'after':b'new b'}
                ],root/'backup',target)
            self.assertEqual(a.read_bytes(),b'old a')
            self.assertFalse(b.exists())

    def test_rollback_rejects_backup_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); target_root=root/'state'; target_root.mkdir(); target=target_root/'file'; target.write_bytes(b'after')
            backup_dir=root/'backup'; backup_dir.mkdir(); outside=root/'outside.bin'; outside.write_bytes(b'before')
            receipt=backup_dir/'receipt.json'
            receipt.write_text(json.dumps({
                'schema':2,'status':'applied','target_root':str(target_root),
                'files':[{'path':str(target),'before_sha256':setup.digest(b'before'),
                          'after_sha256':setup.digest(b'after'),'backup':'../outside.bin'}]
            }), encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'escapes'):
                setup.rollback(receipt,target_root)
            self.assertEqual(target.read_bytes(),b'after')

if __name__=='__main__': unittest.main()
