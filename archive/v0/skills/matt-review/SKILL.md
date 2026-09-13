---
name: matt-review
description: Review a code diff, PR, branch, or substantive implementation for correctness and requirement coverage. Use for code review, missing behavior, regressions, or a final review of a risky change. รีวิว code และตรวจว่าทำครบ requirement. Security-only and complexity-only reviews have separate owners.
metadata:
  owner: matt
---

# Review requirements and implementation

Use the user-specified diff/ref when present and verify it resolves. Otherwise,
inspect working changes for a work-in-progress review, or use verified PR metadata
for a PR. Do not invent a base branch. Request missing scope only when necessary.

Read changed code with relevant callers and tests. Review two lenses:
- Requirement fidelity: missing, incorrect, or unrequested behavior.
- Implementation: actionable correctness, compatibility, and maintainability
  defects supported by code and documented project constraints.

The user request can serve as the spec. Missing tracker setup or a formal spec
is not a reason to stop a useful review. Note material unknowns accurately.

Treat code smells as hypotheses. Show the actual consequence before recommending
extraction, polymorphism, or extra interfaces. Tool-enforced style is not a finding.
Preserve justified seams and apply the engineering policy to simplicity conflicts.

Rank actionable findings by impact. For each, give a precise location, concrete
trigger, consequence, and feasible fix. Distinguish verified defects from untested
risks. If no material findings exist, say so without adding filler warnings.

One focused pass is the default. A second specialist pass is warranted by an
actual independent concern, not every touched file. Delegation requires the host's
authorization. Review-only requests do not authorize fixes, comments, or publishing.
