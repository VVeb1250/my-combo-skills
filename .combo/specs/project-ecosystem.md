+++
id = "combo-project-ecosystem"
domains = ["combo"]
status = "accepted"
summary = "Navigation-first, single-source project knowledge and behavioral contracts"
tags = ["specs", "knowledge", "navigation", "verification"]
+++
# Project knowledge contract

## Intent
An opted-in project's knowledge must help a fresh agent make better decisions before work and retain consequential discoveries afterward, without a required search query, repetitive documentation or a new runtime. Existing project documents stay canonical unless deliberately migrated.

## Observable behavior
- Given an opted-in project with domain records, generating the index yields a compact root Markdown map and one shelf per domain. An agent can follow file links to accepted specs, advisory knowledge and runnable verification entrypoints without guessing an ID or query. One record may appear in multiple domains without duplicating its canonical file.
- Given an existing legacy project, rebuilding its index preserves the records, stable IDs, evidence, and authority; only derived views change. Legacy techniques, retros, shortcuts, decisions and changes remain discoverable. Migrate individual records when useful. Never overwrite a handwritten index or silently replace an existing ADR/OpenSpec source.
- Given changed, duplicated or broken canonical data, the compiler detects stale views, invalid metadata, duplicate IDs and invalid typed links. Generated Markdown and JSON are never independent sources of truth. An index miss does not establish absence of a requirement.
- Given a substantive task, read applicable project-wide and domain contracts before consequential choices. Define scenarios, independent expected behavior and appropriate public testing seams before implementation. Keep proposed, accepted, implemented and verified states distinct. An implementation or passing proxy alone does not establish acceptance.
- Given a useful discovery, capture or improve one concise knowledge record with applicability, limitations and evidence. Candidate knowledge is advisory; a tested claim requires scoped evidence, and measured savings require a comparable baseline. Revalidate when using it. Routine work need not create records. Shortcuts must preserve required correctness and security checks.

## Design and verification
Use two primary record types (specs and knowledge), project-defined domains, direct Markdown links and optional details. Keep the JSON index and route/lookup/hop as compatible utilities, not the default interface. No crawler, vector database, Memory Base or mandatory per-task logs.

The [navigation tests](../../tests/test_project_kb_navigation.py) exercise generated views, multi-domain membership, legacy migration, authority, evidence links and stale detection. The [compiler](../../skills/combo/tools/project_kb.py) is the runnable entrypoint. Deterministic checks establish structure and compatibility; actual model behavior and outcome improvement require matched behavioral evaluation, not merely a file-read trace.
