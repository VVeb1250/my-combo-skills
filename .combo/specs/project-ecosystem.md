---
id: combo-project-ecosystem
area: combo
tags: specs, retro, shortcuts, verification
status: accepted
summary: Opt-in single-source project knowledge and bounded retrieval
---
# Project knowledge contract

Normative uppercase terms MUST, MUST NOT, SHOULD and MAY follow RFC 2119/8174.

## Requirement: Single source
A project MUST NOT automatically create .combo on unrelated tasks. Generated indexes MUST NOT become separate specs. Existing native OpenSpec sources MUST remain canonical until explicitly migrated.

## Requirement: Selective retrieval
Agents SHOULD load only relevant knowledge. A missing index match MUST NOT authorize guessing.

## Requirement: Evidence
Retro and shortcuts MUST link evidence and applicability. A tested shortcut MUST document preconditions, validation, and fallback. Shortcuts MUST NOT bypass required correctness/security checks.

## Requirement: Acceptance
A task checklist MUST NOT alone prove accepted behavior. Changes MUST keep proposed and accepted states distinct. Routine tasks MAY proceed without new documentation when no durable contract is changed.