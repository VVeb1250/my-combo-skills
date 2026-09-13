---
name: matt-plan
description: Plan a nontrivial coding feature or refactor from requirements and repository evidence. Use for implementation plans, ambiguous software requirements, test seams, or a requested technical spec. วางแผนพัฒนาและออกแบบขอบเขตงาน code. Skip routine edits and non-coding plans.
metadata:
  owner: matt
---

# Plan a bounded change

Read the relevant implementation, callers, tests, and applicable ADRs. Describe
the user-visible problem and observable result before choosing modules.

Use existing public interfaces as test seams. New seams need a demonstrated
consumer, domain boundary, isolation need, or explicit extensibility requirement.
A single adapter alone is not evidence for a framework; two actual adapters may be.

For a small change, a few sentences are enough. For complex work, record the
requirements, material design decisions, ordered implementation slices, relevant
verification, and exclusions. Prefer behavior-complete vertical slices.

Proceed using confirmed requirements and repository conventions. Ask only when
an unresolved choice materially changes behavior, scope, or compatibility.
Do not require a seam approval ceremony, exhaustive user stories, a tracker setup,
or a document for a plan already clear from the conversation.

If implementation is requested, carry the plan through to verified delivery.
If only planning is requested, deliver the plan without changing application code.
Publish specs or create issues only when that external action is authorized.
