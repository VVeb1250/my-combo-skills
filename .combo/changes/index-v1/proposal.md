+++
id = "change.combo-index-v1"
area = "combo"
status = "superseded"
summary = "Progressive agent-selected index and hop with metadata checks"
tags = ["index", "route", "hop", "retrieval"]
paths = ["skills/combo/tools/project_kb.py"]
[[links]]
relation = "constrained_by"
target = "combo-project-ecosystem"
+++
# Proposed index upgrade

## Problem
Legacy index provides flat area/tag filters without freshness or relationship navigation.

## Approach
Provide hierarchical area shelves and one-hop links; agent owns further expansion.
Keep accepted specs separate from supporting documents, fail on stale cache and broken links.
No vector DB, AST index, automated semantic ranking or new Combo workflow.

## Acceptance
Deterministic index; path routing; bounded hops; stale detection; duplicate and link
validation; historical records excluded from active suggestions.

## Status
Historical v1 implementation, superseded as the primary navigation interface by the [accepted navigation-first contract](../../specs/project-ecosystem.md). The CLI utilities and legacy record format remain supported. Retrieval-quality and actual token-cost A/B remain to be evaluated.
