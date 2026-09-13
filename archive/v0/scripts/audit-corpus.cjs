// Mechanical audit only. Semantic decisions live in manifest.json.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const yaml = require(path.join(process.env.APPDATA, 'npm/node_modules/promptfoo/node_modules/js-yaml'));
const root = path.resolve(__dirname, '..');
const home = process.env.USERPROFILE;
const discovery = JSON.parse(fs.readFileSync(path.join(root, 'audit/baseline-codex.json'), 'utf8'));
const known = new Map(discovery.skills.data.flatMap(d => d.skills).map(s => [s.path.toLowerCase(), s]));
const files = new Set([...known.values()].map(s => s.path));
const scanRoots = [path.join(home,'.codex/skills'),path.join(home,'.codex/skill-library'),path.join(home,'.agents/skills'),path.join(root,'sources/ponytail/skills'),path.join(root,'sources/karpathy/skills'),path.join(root,'sources/matt'),path.join(root,'sources/ecc/skills')];
function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const e of fs.readdirSync(dir,{withFileTypes:true})) {
    if (e.name === '.git' || e.name === 'node_modules') continue;
    const p = path.join(dir,e.name);
    if (e.isDirectory()) walk(p);
    else if (e.isSymbolicLink() && fs.statSync(p).isDirectory()) walk(p);
    else if (e.name === 'SKILL.md') files.add(p);
  }
}
scanRoots.forEach(walk);
const skills = [...files].sort().map(p => {
  const raw=fs.readFileSync(p,'utf8'), errors=[];
  const match=raw.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  let meta={};
  if (!match) errors.push('Frontmatter does not start at byte zero or is unterminated');
  else try {meta=yaml.load(match[1]) || {};} catch(e) {errors.push(e.message);}
  if (!meta.name) errors.push('Missing portable name');
  if (!meta.description) errors.push('Missing description');
  const description=String(meta.description || '');
  if (description.length > 1536) errors.push('Description exceeds 1536 characters');
  return {path:p,name:meta.name || path.basename(path.dirname(p)),registered_name:known.get(p.toLowerCase())?.name || null,
    discovered_before:known.has(p.toLowerCase()),metadata:meta,description_chars:description.length,
    body_chars:raw.length-(match?.[0].length||0),sha256:crypto.createHash('sha256').update(raw).digest('hex'),errors};
});
const byName={};
for (const s of skills) (byName[s.name]??=[]).push(s.path);
const duplicates=Object.fromEntries(Object.entries(byName).filter(([,ps])=>ps.length>1));
const report={captured_at:new Date().toISOString(),scan_roots:scanRoots,skills,duplicate_names:duplicates,
  usage_measurement:'Unknown: no transcript or memory-store parsing performed',
  description_cost:'Characters measured, not tokenizer cost or actual injected context'};
fs.mkdirSync(path.join(root,'audit'),{recursive:true});
fs.writeFileSync(path.join(root,'audit/corpus.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({files:skills.length,discovered:skills.filter(s=>s.discovered_before).length,issues:skills.filter(s=>s.errors.length).length,duplicate_names:Object.keys(duplicates).length}));
