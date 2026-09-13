# Plan

Use this path when the user asks for requirements, design, architecture, or an
implementation plan. Stop at the requested planning point unless building or
prototyping was also requested.

## Bound the decision

1. Identify the user outcome, constraints, compatibility obligations, requested
   fidelity, and the decisions that remain open.
2. Inspect the relevant code, callers, tests, repository conventions, domain
   vocabulary, and ADRs. Cite concrete paths or symbols where they support a
   decision. Do not inventory the whole repository.
3. Separate facts from inferences. Surface only unknowns that can change
   product behavior, public contracts, data integrity, security, cost, or
   scope. Resolve routine implementation details from evidence.
4. Compare viable approaches against the real constraints, then commit to one
   recommendation. Keep alternatives only when they clarify a material tradeoff
   or a decision the owner must make.

Use [design](../practices/design.md) for seams and module shape. Prefer existing
public seams and the highest useful test seam. Use [tests](../practices/tests.md)
to state how behavior will be verified. A small runnable prototype is useful
when state, business logic, UI, or an integration question cannot be settled
reliably on paper. Keep it clearly bounded and carry its decision back into the
plan.

## Scale the artifact

- A clear bounded change can be a concise plan in the response. Do not create a
  tracker, spec, ticket tree, or custom state schema merely because the work has
  more than one file.
- For multi-session or independently executable work, write an artifact in the
  repository's existing convention only if it helps the next executor. Describe
  vertical slices, one done condition per slice, and genuine dependency edges.
  Do not require tracker setup, labels, or a user approval loop.
- For a wide mechanical refactor, prefer an expand, migrate, contract sequence
  sized by blast radius. Keep CI green between migrations when feasible.
- Research or external documentation belongs here only when it resolves a
  material uncertainty. Use primary sources and record version or date for
  facts that can change.

## Plan output

Tailor the result to the requested fidelity. Include the relevant items from
problem and desired behavior, chosen approach and rationale, affected areas,
acceptance criteria, test or verification strategy, risks, explicit out-of-
scope items, and the next executor action. If a genuine preference or contract
decision remains, ask the smallest question that changes the plan. Do not
silently turn a plan-only request into implementation.
