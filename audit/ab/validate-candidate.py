"""Validate expanded B on a disposable copy before promoting any source files."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
candidate = Path('D:/combo-ab-evals/staged-20260909-202834/B/skills')
with tempfile.TemporaryDirectory(prefix='combo-candidate-validation-') as directory:
    target = Path(directory)
    shutil.copytree(candidate, target / 'skills')
    shutil.copytree(ROOT / 'candidates/common/combo/references/library',
        target / 'skills/combo/references/library', dirs_exist_ok=True)
    for entry in (target / 'skills').iterdir():
        if entry.name != 'combo':
            (entry / 'agents').mkdir(exist_ok=True)
            (entry / 'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: true\n', encoding='utf-8')
    shutil.copytree(ROOT / 'skills/combo-maintain', target / 'skills/combo-maintain')
    (target / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts/validate-curated.cjs', target / 'scripts/validate-curated.cjs')
    shutil.copy2(ROOT / 'POLICY.md', target / 'POLICY.md')
    manifest = json.loads((ROOT / 'install-manifest.json').read_text(encoding='utf-8'))
    manifest['source_roots'] = [{'source': f'skills/{p.name}', 'target': f'skills/{p.name}'}
        for p in sorted((target / 'skills').iterdir())]
    (target / 'install-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    process = subprocess.run(['node', str(target / 'scripts/validate-curated.cjs')],
        cwd=target, env=os.environ.copy(), check=False)
    shutil.copy2(target / 'audit/curated-validation.json', ROOT / 'audit/ab/candidate-validation.json')
    raise SystemExit(process.returncode)
