---
name: ponytail-review
description: Review code for unnecessary complexity, speculative abstractions, redundant dependencies, or dead flexibility. Use when asked to simplify, delete unnecessary code, check over-engineering, or when a change introduces substantial new layers. ตรวจ over-engineering. Skip general correctness review and ordinary small edits.
metadata:
  owner: ponytail
---

# Find a smaller correct design

Read the actual diff, requirements, callers, and justified architecture first.
Find redundant code, existing stdlib/platform replacements, unused flexibility,
or layers without a current purpose. Explain the concrete maintenance cost.

For each finding, give location, removable complexity, proposed replacement, and
the behavior/constraint that must remain. Validate replacement semantics against
actual inputs. Shorter syntax alone is not an improvement.

Never cut trust-boundary validation, data-loss safeguards, security, accessibility,
required behavior, meaningful tests, or seams justified by real adapters/domain needs.
An email format heuristic is not a replacement for required validation.

Review only unless fixes were requested. If already lean, say so and stop.
Do not use lines deleted as the success criterion or trigger unrelated cleanup.
