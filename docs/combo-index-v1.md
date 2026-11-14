# Project Knowledge Index v2

Navigation-first, deterministic and opt-in. Read .combo/INDEX.md then the
relevant domain index; use native file tools and links. Known paths bypass
the index. Search is a fallback, not the default. No service or model calls.

## Setup and maintenance

```bash
python /path/to/combo/tools/project_kb.py init
python /path/to/combo/tools/project_kb.py index
python /path/to/combo/tools/project_kb.py check
```

init creates minimal areas/specs/knowledge folders and views. index migrates
the local JSON cache to schema 4 and regenerates Markdown from canonical
records, without rewriting source records. Global catalog keeps schema 3.
check verifies source metadata, generated JSON and Markdown freshness.
Generated views are not canonical records. Handwritten indexes are not
overwritten: reconcile them explicitly. Legacy records remain discoverable.

## Domain and record format

Domain descriptors live in .combo/areas/<domain>.md, with id, area, summary,
and optional source paths. Choose descriptive project vocabulary. A record
may belong to multiple domains; its stable ID has one owner.

```toml
+++
id = "knowledge.shared-junction"
domains = ["terrain", "simulation"]
summary = "Construct connected junctions from incident edges."
status = "candidate"
topics = ["hydrology", "geometry"]
kinds = ["technique", "lesson"]
+++
```

Use a short core: mechanism, when to apply, limits, evidence. Link long
implementation notes or evidence. For supporting Markdown inside indexed
folders use TOML frontmatter record = false; nested knowledge files without
explicit IDs are treated as detail. Legacy records retain existing scan and
validation semantics. New tested knowledge needs local evidence or an evidence
record, not just a label; applicability must be checked by the reader.
Optional fields: paths, tags, topics, kinds, problem_signals, engine, renderer,
evidence, validated_at and typed links. Legacy area remains accepted. Domain
names must be safe path components.

Spec records use the same routing metadata and status accepted/draft/etc.
Keep intent, scenarios, invariants, consequential design decisions, testing
seams and evidence near each other; distinguish proposed/accepted intent
from implemented/verified behavior. No mandatory template or ticket.
Preserve existing ADR/OpenSpec as canonical where applicable.

Generated domain indexes group accepted specs, design/pending, advisory
knowledge, verification and domain entrypoints. They point to actual files,
not duplicated prose. Inactive records remain in JSON and source history,
not default shelves. Cross-domain records appear in each domain, one owner.
Domain growth: group or refine meaningful project domains when needed; no
automatic hierarchy or arbitrary size gate.

## Optional machine utilities

```bash
python /path/to/combo/tools/project_kb.py areas
python /path/to/combo/tools/project_kb.py route --path src/simulation/vehicle.ts
python /path/to/combo/tools/project_kb.py route --query "target oscillation"
python /path/to/combo/tools/project_kb.py hop --from simulation
python /path/to/combo/tools/project_kb.py lookup --id knowledge.shared-junction
```

route without filters shows domains; path/lexical matching is advisory.
Required specs are not top-k limited. hop follows one edge/shelf; no
automatic recursion. Explicit global catalog retains existing scoped
resolution and fallback. Index hashes detect record/view drift, not
semantic code drift or truth of evidence. Check current revision and
primary evidence before consequential reliance. No automatic capture,
publishing, hooks or global synchronization.

## Behavioral acceptance

A fresh agent should discover relevant records from Markdown alone,
apply or challenge them against actual code, and preserve useful
discoveries for a later session. Compare equal-content search-first vs
navigation-first on matched tasks, with a no-knowledge control and routine
negative control. Mechanical compiler tests do not establish model behavior,
token savings or outcome improvement.
