"""Create a single original-state rollback receipt for one install session."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib
import setup

p=argparse.ArgumentParser()
p.add_argument('--out',type=Path,required=True)
p.add_argument('receipts',type=Path,nargs='+')
args=p.parse_args()
merged={}
for receipt_path in args.receipts:
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    if receipt['status']!='applied': raise SystemExit(f'Not applied: {receipt_path}')
    for row in receipt['files']:
        old=merged.get(row['path'])
        if old:
            if old['after_sha256']!=row['before_sha256']:
                raise SystemExit(f'Intervening drift in receipt chain: {row["path"]}')
            old['after_sha256']=row['after_sha256']
            old['bytes_after']=row['bytes_after']
        else:
            merged[row['path']]={**row,'source_backup':receipt_path.parent/row['backup'] if row['backup'] else None}
for row in merged.values():
    current=Path(row['path']).read_bytes()
    if hashlib.sha256(current).hexdigest()!=row['after_sha256']:
        # A real Codex CLI launch can refresh marketplace cache paths in config.
        # Preserve that non-owned change instead of reverting it with our install.
        if Path(row['path']).name!='config.toml' or not row['source_backup']:
            raise SystemExit(f'Current file has later changes: {row["path"]}')
        original=row['source_backup'].read_bytes()
        manifest=json.loads((setup.ROOT/'manifest.json').read_text(encoding='utf-8'))
        expected=setup.render_config(original,manifest,Path.home())
        if hashlib.sha256(expected).hexdigest()!=row['after_sha256']:
            raise SystemExit('Cannot reconstruct expected config; refusing consolidation')
        actual_data=tomllib.loads(current.decode('utf-8-sig'))
        expected_data=tomllib.loads(expected.decode('utf-8-sig'))
        if {k:v for k,v in actual_data.items() if k!='marketplaces'}!={k:v for k,v in expected_data.items() if k!='marketplaces'}:
            raise SystemExit('Later config changes exceed marketplace refresh; refusing consolidation')
        pattern=r'^\[marketplaces(?:\.[^\]\n]+)?\][^\n]*\n[\s\S]*?(?=^\[|\Z)'
        market_sections=re.findall(pattern,current.decode('utf-8-sig'),re.M)
        restored=re.sub(pattern,'',original.decode('utf-8-sig'),flags=re.M).rstrip()+'\n\n'+''.join(market_sections)
        restored_data=tomllib.loads(restored)
        intended=tomllib.loads(original.decode('utf-8-sig'))
        intended['marketplaces']=actual_data.get('marketplaces',{})
        if restored_data!=intended: raise SystemExit('Marketplace preservation changed other fields')
        row['replacement_backup']=restored.encode('utf-8')
        row['original_before_sha256']=row['before_sha256']
        row['before_sha256']=hashlib.sha256(row['replacement_backup']).hexdigest()
        row['after_sha256']=hashlib.sha256(current).hexdigest()
        row['note']='Restore original combo-owned settings while preserving Codex marketplace refresh.'
args.out.mkdir(parents=True,exist_ok=False)
rows=[]
for i,row in enumerate(merged.values()):
    source=row.pop('source_backup')
    row['backup']=f'{i:03}.bin' if source else None
    if source:
        data=row.pop('replacement_backup',None) or source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['before_sha256']: raise SystemExit('Backup integrity failure')
        (args.out/row['backup']).write_bytes(data)
    rows.append(row)
(args.out/'receipt.json').write_text(json.dumps({'status':'applied','files':rows,
    'source_receipts':[str(x) for x in args.receipts]},indent=2),encoding='utf-8')
print(args.out/'receipt.json')
