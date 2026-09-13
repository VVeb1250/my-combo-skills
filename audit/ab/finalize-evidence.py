"""Record compact follow-up evidence and source drift without changing raw runs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit/ab'
STAGE = Path('D:/combo-ab-evals/staged-20260909-202834')

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob('*') if p.is_file()}

report = {'diagnostic_repeats': [], 'initial_thai_a_instruction_diff': {}}
for path in sorted((AUDIT / 'diagnostic-repeat/arms').glob('*/*/result.json')):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    events = [json.loads(line) for line in Path(data['events_path']).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    errors = [e for e in events if e.get('type') in {'error', 'turn.failed'}]
    report['diagnostic_repeats'].append({
        'case': data['case_id'], 'variant': data['variant'],
        'duration_seconds': data['duration_seconds'], 'classification': data['classification'],
        'acceptance': data['acceptance'], 'timed_out': data['timed_out'],
        'errors': errors, 'usage': data['usage'], 'changed_files': data['changed_files'],
    })
initial = json.loads((AUDIT / 'matched-rest/arms/A/thai-delivery/result.json').read_text(encoding='utf-8-sig'))
before = hashes(STAGE / 'A/skills')
after = hashes(Path(initial['workdir']) / '.agents/skills')
report['initial_thai_a_instruction_diff'] = {
    'modified': [key for key in before.keys() & after.keys() if before[key] != after[key]],
    'removed': sorted(before.keys() - after.keys()), 'added': sorted(after.keys() - before.keys()),
}
report['installation'] = {
    'receipt': 'backups/20260909-163949-897900/receipt.json',
    'selected_variant': 'B', 'workflow_entries': 12, 'packages': 14,
    'files': 649, 'changed_install_paths': 571,
    'source_entries': 330, 'reset_credits_used': 1,
    'verification': 'audit/ab/installation-verification.json',
    'preservation': 'audit/ab/preservation.json',
}
(AUDIT / 'final-evidence.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'repeats': [{'case': r['case'], 'variant': r['variant'], 'seconds': r['duration_seconds'], 'classification': r['classification'], 'errors': r['errors'], 'acceptance': r['acceptance']} for r in report['diagnostic_repeats']], 'instruction_diff': report['initial_thai_a_instruction_diff']}))
