# Review

Use this path for a review-only request about code, a diff, a branch, a pull
request, or a security concern. Review describes findings and evidence; it does
not edit, publish, merge, or ask for a second approval unless the user requests
that action.

## Establish review scope

1. Determine the fixed point or review target from the request. If omitted,
   inspect the current diff and state the safe assumption instead of inventing a
   branch. Validate that the target exists and that there is something to review.
2. Read the originating requirement, issue, plan, or user request when
   available. Inspect affected callers, tests, configuration, and repository
   standards that bear on the changed behavior.
3. Build a small trigger-to-consequence map for each suspected issue. Run a
   focused, non-mutating check when it can confirm a finding. Do not treat a
   clean lint result as behavioral evidence.

## Two lenses, one ranking

Keep two lenses while reasoning about every review:

- **Requirement fidelity:** missing, partial, incompatible, or scope-creeping
  behavior compared with the originating request or spec.
- **Implementation quality:** correctness, error boundaries, data and
  concurrency invariants, security assumptions, maintainability, and repository
  standards.

Rank all findings by practical impact and confidence across the report, while
retaining which lens supports each finding when useful. Every
finding should name the location, reachable trigger, consequence, evidence, and
the smallest useful remedy. Use severity such as critical, high, medium, or low
only when it helps order action. A style-only disagreement already enforced by
automation is not a finding.

Apply [security](../practices/security.md) only for a real trust boundary and
[simplicity](../practices/simplicity.md) only when the diff adds unnecessary
complexity. Do not require parallel reviewers, a tracker, or a full test suite
for every review. Review independently when useful, but do not force a
lens-based report layout.

## Report

Lead with the highest-impact actionable findings, followed by lower-impact
items and useful limitations or no-findings. Include check commands and
results, assumptions, and unreviewed areas when relevant. If no material issue
is found, say so plainly and explain the evidence and limits. If the user authorized repair as
part of delivery, route the repair through [deliver](deliver.md); a review-only
request ends with the report.
