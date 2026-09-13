"""Promote selected B source layout, preserving the engineering baseline."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
stage = Path('D:/combo-ab-evals/staged-20260909-202834/B/skills')
archive = ROOT / 'archive/v2-engineering'
if archive.exists():
    raise SystemExit('Baseline archive exists; inspect instead of overwriting')
archive.mkdir(parents=True)
shutil.copytree(ROOT / 'skills', archive / 'skills')
for name in ('POLICY.md', 'install-manifest.json', 'README.md'):
    shutil.copy2(ROOT / name, archive / name)
for entry in stage.iterdir():
    shutil.copytree(entry, ROOT / 'skills' / entry.name, dirs_exist_ok=True)
# Two upstream reference repairs are packaging corrections, outside tested routes.
shutil.copytree(ROOT / 'candidates/common/combo/references/library',
    ROOT / 'skills/combo/references/library', dirs_exist_ok=True)
for entry in (ROOT / 'skills').iterdir():
    (entry / 'agents').mkdir(exist_ok=True)
    (entry / 'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: true\n', encoding='utf-8')
manifest_path = ROOT / 'install-manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['source_roots'] = [{'source': f'skills/{p.name}', 'target': f'skills/{p.name}'}
    for p in sorted((ROOT / 'skills').iterdir()) if p.is_dir()]
manifest['config']['worker_role']['description'] = 'Bounded worker for independent research, implementation, artifacts, and checks.'
manifest['architecture'] = {'layout': 'modular-workflow-pack', 'primary_entries': 12,
    'shared_router': 'combo', 'maintenance': 'combo-maintain',
    'decision': 'audit/ab/DECISION.md'}
manifest['full_library'] = True
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'selected': 'B', 'packages': len(manifest['source_roots']), 'baseline_archive': str(archive)}))
