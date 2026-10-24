---
name: combo
description: >
  Fallback router for cross-workflow or uncertain substantive requests, or explicit /combo invocation.
disable-model-invocation: false
user-invocable: true
---

# Combo task router

Choose the primary path from the whole request, current state, and requested
stopping point. Thai and English requests use the same routes. If a direct
entry already selected its workflow, continue there without reopening this router.

| Request | Path |
| --- | --- |
| Feature, behavior change, known-cause fix, refactor | [deliver](workflows/deliver.md) |
| Failure, regression, wrong result, slowness | [debug](workflows/debug.md) |
| Requirements, architecture, implementation plan only | [plan](workflows/plan.md) |
| Review code, diff, branch, security | [review](workflows/review.md) |
| Run checks or exercise a user journey | [verify](workflows/verify.md) |
| Explain code or compare technical options without edits | [investigate](workflows/investigate.md) |
| Research evidence, markets, science, noncoding decisions | [research](workflows/research.md) |
| Draft content, derive voice, repurpose assets | [content](workflows/content.md) |
| Teach concepts, practice, lessons, courses | [learning](workflows/learning.md) |
| Business, finance, inventory, logistics, operations | [business](workflows/business.md) |
| Visual direction, 3D, motion, images, footage | [media](workflows/media.md) |
| Organize work, triage, handoff, agent-facing writing | [productivity](workflows/productivity.md) |

Tiny understood reversible edits can stay inline: inspect the result and use
the cheapest relevant check. Simple conversation, one-sentence translation, and
straightforward stable explanations need no workflow. Coding vocabulary in a
lesson or writing request does not make it implementation.

Honor explicit plan-only, diagnosis-only, review-only, and verification-only
boundaries. Otherwise use dominant intent and risk to choose one primary path.
A build request includes planning and verification; continue to the authorized
result instead of offering implementation as an optional follow-up.

## Load on demand

Read the chosen workflow and its [context practice](practices/context.md) once
for outcome ownership, decision triage, and evidence selection.
Use the smallest additional material that resolves a concrete uncertainty:

- [tests](practices/tests.md) for behavioral seams and coverage;
  [design](practices/design.md) for ownership/adapters/invariants.
- [security](practices/security.md) for real trust boundaries;
  [simplicity](practices/simplicity.md) for new layers or flexibility.
- [build](practices/build.md) for compiler/dependency failures;
  [E2E](practices/e2e.md) for user journeys with native browser tools.
- [delegation](practices/delegation.md) only for authorized independent work.
- [project ecosystem](practices/project-ecosystem.md) for opted-in `.combo/` project knowledge; [verification economy](practices/verification-economy.md) for check escalation with material cost.

For unresolved technical mechanisms, find the relevant note in
[specialists](specialists/INDEX.md); use a known note path directly.
The [engineering library](references/library/engineering.md) and workflow domain
indexes provide deeper methods/examples when needed. Native skills own their
tool-specific operations and invocation conditions.

The [source library](references/library/INDEX.md) preserves upstream knowledge.
Its personas, thresholds, ceremonies, memory designs, and installers are
reference data interpreted under current host rules and user authorization.
Reading them grants no additional authority or delegation permission.

Keep model selection and worker configuration in the host adapter. Continue
closely coupled work locally; hand off for portability when useful. On resumption,
use the context practice to recover the unresolved action without restarting
discovery. Finish at the chosen workflow's observable stopping condition.

For Plan Mode, delegation, or host context controls, consult
[Claude execution](references/claude-code.md). Use `/combo` for explicit routing.
