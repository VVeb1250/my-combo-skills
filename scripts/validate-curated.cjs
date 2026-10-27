const fs = require('fs');
const path = require('path');
const yaml = require(path.join(process.env.APPDATA, 'npm/node_modules/promptfoo/node_modules/js-yaml'));

const root = path.resolve(__dirname, '..');
const packageNamePattern = /^combo(?:-[a-z0-9]+)*$/;
const defaultOwnershipIndex = 'skills/combo/.combo-owned.json';
const adapterTarget = 'agents/combo-worker.toml';
const errors = [];
const stats = [];
const relativeLink = /!?\[[^\]]*\]\(([^)\s]+)(?:\s+['"][^)]*['"])?\)/g;
let packageRoots = [];
let manifestEntries = [];
let ownershipIndex = defaultOwnershipIndex;
const explicitOnly = new Set();

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

function isInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === '' || (relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
}

function canonicalRelative(value, label) {
  if (typeof value !== 'string' || value.length === 0) {
    errors.push(`${label} must be a non-empty relative path`);
    return null;
  }
  if (value.includes('\\')) {
    errors.push(`${label} must use POSIX separators: ${value}`);
    return null;
  }
  const normalized = path.posix.normalize(value);
  const parts = normalized.split('/');
  if (value.startsWith('/') || path.posix.isAbsolute(value) || parts.includes('..') || parts.includes('.')) {
    errors.push(`${label} escapes its allowed root: ${value}`);
    return null;
  }
  if (normalized !== value) {
    errors.push(`${label} is not canonical: ${value}`);
    return null;
  }
  return value;
}

function frontmatter(file, name) {
  const text = read(file);
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    errors.push(`${name}: invalid frontmatter`);
    return { text, meta: {} };
  }
  let meta;
  try {
    meta = yaml.load(match[1]) || {};
  } catch (error) {
    errors.push(`${name}: invalid YAML frontmatter`);
    meta = {};
  }
  if (meta.name !== name) errors.push(`${name}: name collision/mismatch`);
  if (typeof meta.description !== 'string' || meta.description.length === 0 || meta.description.length > 400) {
    errors.push(`${name}: description must be a non-empty string of 1-400 characters`);
  }
  const allowed = new Set(['name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools']);
  for (const key of Object.keys(meta)) if (!allowed.has(key)) errors.push(`${name}: nonportable frontmatter ${key}`);
  return { text, meta, bodyLines: text.slice(match[0].length).trim().split(/\r?\n/).length };
}

function checkLinks(file, packageRoot) {
  // Markdown examples and inline code are source text, not navigable links.
  const text = read(file).replace(/^ {0,3}(`{3,}|~{3,})[^\n]*\n[\s\S]*?^ {0,3}\1\s*$/gm, '')
    .replace(/(`+)[^\n]*?\1/g, '');
  for (const match of text.matchAll(relativeLink)) {
    let target = match[1].trim().replace(/^<|>$/g, '');
    if (!target || target.startsWith('#') || /^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith('//')) continue;
    target = decodeURIComponent(target.split(/[?#]/, 1)[0]);
    const resolved = path.resolve(path.dirname(file), target);
    const insideDeclaredBundle = packageRoots.some(name => isInside(path.join(root, 'skills', name), resolved));
    if (!insideDeclaredBundle || !fs.existsSync(resolved)) {
      errors.push(`${path.relative(root, file)}: unresolved relative reference ${match[1]}`);
    }
  }
}

function validatePackage(name) {
  const packageRoot = path.join(root, 'skills', name);
  const entry = path.join(packageRoot, 'SKILL.md');
  const policy = path.join(packageRoot, 'agents', 'openai.yaml');
  if (!fs.existsSync(entry)) {
    errors.push(`${name}: missing SKILL.md`);
    return;
  }
  if (!fs.existsSync(policy)) errors.push(`${name}: missing agents/openai.yaml`);
  else {
    try {
      const parsed = yaml.load(read(policy));
      const implicit = parsed?.policy?.allow_implicit_invocation;
      if (explicitOnly.has(name)) {
        if (implicit !== false) errors.push(`${name}: explicit-only entry must disable implicit invocation`);
      } else if (implicit !== true) {
        errors.push(`${name}: implicit invocation is not enabled`);
      }
    } catch (_) {
      errors.push(`${name}: invalid agents/openai.yaml`);
    }
  }
  const result = frontmatter(entry, name);
  const files = [];
  for (const current of walk(packageRoot)) {
    files.push(current);
    const relative = path.relative(packageRoot, current);
    if (path.basename(current) === 'SKILL.md' && relative !== 'SKILL.md') errors.push(`${name}: nested SKILL.md is not allowed`);
    if (current.endsWith('.md')) checkLinks(current, packageRoot);
  }
  stats.push({ name, files: files.length, description_chars: typeof result.meta.description === 'string' ? result.meta.description.length : 0, body_lines: result.bodyLines || 0 });
  return files.length;
}

function* walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const current = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) {
      errors.push(`${path.relative(root, current)}: symlink is not allowed in package`);
    } else if (entry.isDirectory()) {
      yield* walk(current);
    } else if (entry.isFile()) {
      yield current;
    }
  }
}

let manifest;
try {
  manifest = JSON.parse(read(path.join(root, 'install-manifest.json')));
  if (manifest.version !== 2) errors.push('install-manifest.json: expected version 2');
  if (!Array.isArray(manifest.source_roots) || manifest.source_roots.length === 0) {
    errors.push('install-manifest.json: source_roots must be a non-empty array');
  } else {
    manifestEntries = manifest.source_roots;
    const seen = new Set();
    for (const [index, entry] of manifest.source_roots.entries()) {
      const source = typeof entry === 'string' ? entry : entry && entry.source;
      const target = typeof entry === 'string' ? entry : entry && entry.target;
      const sourcePath = canonicalRelative(source, `install-manifest.json: source_roots[${index}].source`);
      const targetPath = canonicalRelative(target, `install-manifest.json: source_roots[${index}].target`);
      if (!sourcePath || !targetPath) continue;
      if (sourcePath !== targetPath) {
        errors.push(`install-manifest.json: source_roots[${index}] source/target must match exactly`);
        continue;
      }
      if (!sourcePath.startsWith('skills/')) {
        errors.push(`install-manifest.json: source root must be under skills/: ${sourcePath}`);
        continue;
      }
      const name = sourcePath.slice('skills/'.length);
      if (!packageNamePattern.test(name) || name.includes('/')) {
        errors.push(`install-manifest.json: invalid Combo package name: ${name}`);
        continue;
      }
      if (seen.has(name)) {
        errors.push(`install-manifest.json: duplicate Combo package root: ${name}`);
        continue;
      }
      seen.add(name);
      packageRoots.push(name);
    }
    if (!seen.has('combo')) errors.push('install-manifest.json: source_roots must include combo');
  }
  const architecture = manifest.architecture;
  if (architecture && architecture.explicit_only !== undefined) {
    if (!Array.isArray(architecture.explicit_only)) {
      errors.push('install-manifest.json: architecture.explicit_only must be an array');
    } else {
      for (const name of architecture.explicit_only) {
        if (typeof name !== 'string' || !packageRoots.includes(name)) {
          errors.push(`install-manifest.json: explicit-only entry is not a declared package: ${name}`);
        } else {
          explicitOnly.add(name);
        }
      }
    }
  }
  ownershipIndex = canonicalRelative(manifest.ownership_index || defaultOwnershipIndex, 'install-manifest.json: ownership_index') || defaultOwnershipIndex;
  if (ownershipIndex !== defaultOwnershipIndex) {
    errors.push(`install-manifest.json: ownership_index must be ${defaultOwnershipIndex}`);
  }
  for (const entry of manifest.adapter_files || []) {
    const target = canonicalRelative(entry && entry.target, 'install-manifest.json: adapter target');
    if (target !== adapterTarget) errors.push(`install-manifest.json: adapter target must be ${adapterTarget}`);
    const source = canonicalRelative(entry && entry.source, 'install-manifest.json: adapter source');
    if (source && !source.startsWith('adapters/')) errors.push(`install-manifest.json: unsafe adapter source ${source}`);
  }
  if (!Array.isArray(manifest.adapter_files)) errors.push('install-manifest.json: adapter_files must be an array');
  else if (manifest.adapter_files.length > 1) errors.push('install-manifest.json: only combo-worker.toml may be declared as an adapter');
  for (const entry of manifest.disable_local || []) {
    const value = typeof entry === 'string' ? entry : entry.path;
    const normalized = canonicalRelative(value, 'install-manifest.json: disable path');
    if (!normalized || !(normalized.startsWith('.agents/') || normalized.startsWith('.codex/'))) {
      errors.push(`install-manifest.json: unsafe disable path ${value}`);
    }
  }
} catch (error) {
  errors.push(`install-manifest.json: ${error.message}`);
}

const skillsRoot = path.join(root, 'skills');
const directories = fs.existsSync(skillsRoot)
  ? fs.readdirSync(skillsRoot, { withFileTypes: true }).filter(entry => entry.isDirectory()).map(entry => entry.name)
  : [];
for (const directory of directories) if (!packageRoots.includes(directory)) errors.push(`skills/${directory}: superseded top-level entrypoint remains active`);
for (const name of packageRoots) validatePackage(name);
const packageFiles = stats.reduce((sum, row) => sum + row.files, 0);
const maxPackageFiles = Number.isInteger(manifest && manifest.max_package_files) && manifest.max_package_files > 0
  ? manifest.max_package_files
  : null;
if (maxPackageFiles !== null && packageFiles > maxPackageFiles) errors.push(`Combo packages exceed ${maxPackageFiles} files: ${packageFiles}`);

const policyPath = path.join(root, 'POLICY.md');
if (fs.existsSync(policyPath)) {
  const policyLines = read(policyPath).trim().split(/\r?\n/).length;
  if (policyLines > 60) errors.push(`Policy exceeds 60 lines: ${policyLines}`);
} else errors.push('POLICY.md: missing');

const report = { checked_at: new Date().toISOString(), package_roots: packageRoots, package_files: packageFiles, ownership_index: ownershipIndex, skills: stats, errors };
fs.mkdirSync(path.join(root, 'audit'), { recursive: true });
fs.writeFileSync(path.join(root, 'audit', 'curated-validation.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ packages: stats.length, files: packageFiles, errors }));
if (errors.length) process.exitCode = 1;
