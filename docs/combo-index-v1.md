# Progressive Index v1

Default is **A: agent-driven progressive route + deliberate one-hop**. This is an
optional, project-local document router, not a vector DB, AST index, agent
replacement, personal memory store, or model-powered summary generator.

## Commands

From a project root with an opted-in `.combo/`:

```bash
python /path/to/combo/tools/project_kb.py index
python /path/to/combo/tools/project_kb.py areas
python /path/to/combo/tools/project_kb.py route --path src/ai/commander/orders.ts --query 'target oscillation'
python /path/to/combo/tools/project_kb.py route --path src/ai/commander/orders.ts target oscillation
python /path/to/combo/tools/project_kb.py hop --from commander
python /path/to/combo/tools/project_kb.py hop --from adr.target-state --limit 10 --offset 0
python /path/to/combo/tools/project_kb.py lookup --area commander --kind retro
python /path/to/combo/tools/project_kb.py lookup --id adr.target-owner
python /path/to/combo/tools/project_kb.py check
```

The `index` command explicitly migrates index schema 1 to 2 without changing
source Markdown. Legacy single-line `---` metadata remains valid. TOML `+++`
metadata supports arrays and `[[links]]` on Python 3.11+.

## Agent contract

1. If the exact relevant source is already known, read it directly. Otherwise
   query once for the current task, using real intent/paths/area.
2. Treat `required` accepted specs as binding candidate contracts, not a
   finite top-k recommendation. Verify actual relevance and user's current intent.
3. Use `suggested` to navigate a small shelf. Decide which record or area
   merits another hop; `hop` never recurses. Follow another step only for a
   newly found dependency, unresolved question or evidence contradiction.
4. When the index misses, broaden or inspect primary code/test/doc sources.
   Do not guess absent knowledge.
5. Retro and shortcuts are advisory and must be validated against current code,
   owner-approved specs and evidence.

## Document format

```toml
+++
id = "adr.target-owner"
area = "commander"
status = "accepted"
summary = "Squad owns the targeting state"
tags = ["targeting", "state"]
paths = ["src/ai/commander/**"]
[[links]]
relation = "constrained_by"
target = "spec.commander.targeting"
+++
```

Store one canonical Markdown source per record. `id` should remain stable
across renames. Optional `.combo/areas/<area>.md` supplies ownership and
path hints. Supported relations: `related_to`, `constrained_by`,
`depends_on`, `verified_by`, `supersedes`, `informs`.

The script validates IDs, broken links, tested evidence and shortcut headings.
It writes index.json atomically, and read commands fail on content mismatches,
naming the added, changed or removed record paths so the Agent can decide to
re-index. Hashes detect Markdown/index drift, not whether a historical lesson
still applies to a changed codebase. No automatic capture, run execution or hooks.

## Phase A knowledge ownership (not yet indexed)

[Project ecosystem guidance](../skills/combo/practices/project-ecosystem.md) separates technique methods, retro lessons, lower-cost shortcuts, and scoped verification. Technique Discovery is a conditional process, not a stored kind. Do not create every record kind for each task.

**Runtime boundary:** `project_kb.py` currently uses schema 2 and recognizes only the existing seven KINDS. The `.combo/techniques/TEMPLATE.md` file is intentionally excluded from indexing; `problem_signals`, engine/renderer compatibility, technique lifecycle, global libraries and cross-scope IDs/links are NOT implemented by adding the template. `route`, `lookup`, `hop`, the CLI and index validation behavior remain unchanged. Agent-controlled multi-hop means repeated deliberate `hop` calls, not automatic recursion.

**Future phases (not authorized by this documentation change):** extend local technique metadata parsing, validation and relevance matching while preserving existing CLI contracts and unrestricted `required` accepted specs. Measure recall, false positives, compatibility errors, tokens and latency against schema 2. Then consider project-first/global-fallback resolution using the same index contract, explicitly scoped identity and checked external links, without allowing a global recommendation to override project requirements.

**Phase A acceptance scenarios for future tests (not executed):** unsuccessful experiments do not become verified techniques; tested-in-one-project does not imply portable; unmeasured shortcuts do not claim savings; overlapping retro/technique records link rather than duplicate; specs outrank advisory recipes; unknown applicability stays unknown; missing evidence cannot certify tested claims; concurrent canonical edits detect conflicts; schema-2 projects keep functioning.

## A/B limitation

A is implemented. A deterministic one-hop B is only a proposed comparison.
A/B conclusions require actual task traces, known-needed document IDs,
quality/correctness verdicts, and per-task token/tool cost. Unit tests of A
do not establish a token saving or superior RTS debugging.
