import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
IMPLICIT = {'combo-engineering', 'combo-diagnose', 'combo-assurance', 'combo-research', 'combo-learning', 'combo-production'}
EXPLICIT = {'combo', 'combo-wiki', 'combo-retro', 'combo-maintain', 'combo-author'}


class CandidateChecks(unittest.TestCase):
    def test_skill_discovery_metadata(self):
        self.assertEqual({x.parent.name for x in SKILLS.glob('*/SKILL.md')}, IMPLICIT | EXPLICIT)
        for name in IMPLICIT | EXPLICIT:
            entry = SKILLS / name
            body = (entry / 'SKILL.md').read_text()
            self.assertTrue(body.startswith(f'---\nname: {name}\n'))
            self.assertIn('description: >\n  ', body)
            self.assertIn(f'disable-model-invocation: {str(name in EXPLICIT).lower()}', body)
            self.assertIn(f'allow_implicit_invocation: {str(name in IMPLICIT).lower()}', (entry / 'agents/openai.yaml').read_text())

    def test_links_resolve_inside_candidate(self):
        for doc in ROOT.rglob('*.md'):
            for dest in re.findall(r'\[[^\]]+\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
                if '://' in dest or dest.startswith('#'):
                    continue
                path = (doc.parent / dest.split('#', 1)[0]).resolve()
                self.assertTrue(path.is_relative_to(ROOT), (doc, dest))
                self.assertTrue(path.exists(), (doc, dest))

    def test_every_method_discoverable(self):
        text = '\n'.join(p.read_text() for p in SKILLS.glob('*/SKILL.md'))
        for method in (SKILLS / 'combo/methods').glob('*.md'):
            self.assertIn(f'methods/{method.name}', text)

    def test_technique_shelf_is_selective_and_discoverable(self):
        shelf = SKILLS / 'combo/techniques'
        index = (shelf / 'INDEX.md').read_text()
        discovery = (SKILLS / 'combo/methods/expertise.md').read_text()
        self.assertIn('../techniques/INDEX.md', discovery)
        for note in shelf.glob('*.md'):
            if note.name != 'INDEX.md':
                self.assertIn(f'({note.name})', index)
        for name in ('combo-engineering', 'combo-diagnose', 'combo-assurance',
                     'combo-research', 'combo-production'):
            self.assertIn('../combo/methods/expertise.md', (SKILLS / name / 'SKILL.md').read_text())
        for path in SKILLS.rglob('*.md'):
            body = path.read_text()
            self.assertNotIn('specialists/INDEX.md', body)
            self.assertNotIn('references/library/INDEX.md', body)
        self.assertFalse((SKILLS / 'combo/specialists').exists())

    def test_static_recovery_hook(self):
        configs = [json.loads((ROOT / f'adapters/{h}/recovery-hook.example.json').read_text()) for h in ('codex', 'claude')]
        self.assertEqual(configs[0], configs[1])
        for config in configs:
            self.assertEqual(set(config['hooks']), {'SessionStart'})
            group, = config['hooks']['SessionStart']
            self.assertIsNotNone(re.fullmatch(group['matcher'], 'compact'))
            self.assertIsNotNone(re.fullmatch(group['matcher'], 'resume'))
            self.assertIsNone(re.fullmatch(group['matcher'], 'startup'))
            hook, = group['hooks']
            self.assertEqual(hook['type'], 'command')
            self.assertRegex(hook['command'], r'^echo "[^"$`;&|<>]+"$')
            if shutil.which('sh'):
                actual = subprocess.check_output(['sh', '-c', hook['command']], text=True)
                self.assertIn('pending wiki/checkpoint work', actual)
                self.assertIn('do not restart completed work', actual)

    def test_oracle_distinguishes_baseline_from_new_behavior(self):
        oracle = ROOT / 'evals/commander_oracle.py'
        fixture = ROOT / 'evals/fixtures/commander'
        for phase, status in [('baseline', 0), ('smoke', 1), ('threshold', 1)]:
            with self.subTest(phase=phase):
                result = subprocess.run([sys.executable, '-B', str(oracle), str(fixture), phase], capture_output=True, text=True)
                self.assertEqual(result.returncode, status, result.stdout + result.stderr)


    def test_oracle_accepts_expected_behavior_and_rejects_manual_override_regression(self):
        oracle = ROOT / 'evals/commander_oracle.py'
        fixture = ROOT / 'evals/fixtures/commander'
        for phase in ('smoke', 'threshold'):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'fixture'
                shutil.copytree(fixture, target)
                implementation = target / 'src/arbitration.py'
                original = implementation.read_text()
                candidate = original.replace('Action("retreat", False)', 'Action("retreat", smoke and loaded)')
                if phase == 'threshold':
                    candidate = candidate.replace('risk >= 70', 'risk >= 80')
                implementation.write_text(candidate)
                result = subprocess.run([sys.executable, '-B', str(oracle), str(target), phase], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                implementation.write_text(candidate.replace('return Action("hold", loaded)', 'return Action("retreat", loaded)', 1))
                result = subprocess.run([sys.executable, '-B', str(oracle), str(target), phase], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
