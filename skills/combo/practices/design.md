# Design and seams

Use this practice for consequential architecture or behavior choices, a
cross-module change, a known required variation, or non-obvious state/data
ownership. Do not wait for the agent to declare a decision unresolved:
inspect design risk from the request, code and accepted requirements first.
Start from the user outcome and current domain language.

- Read real callers and nearby tests before choosing a boundary. Keep the
  responsibility where the behavior and data naturally belong.
- Prefer a deep module with a small meaningful interface. Existing seams are
  evidence, not a veto: a confirmed planned variation or domain invariant can
  justify a boundary before a second implementation. Do not build unused variants.
- For substantial cross-module work, model domain states, ownership, data flow
  and invariants first. Prefer localized decisions over scattered special cases.
- Minimize reader load: reduce indirection from a behavior question to its owner
  and hidden mutable state the next agent would need to hold in context.
- State assumptions about lifecycle, ownership, failure, concurrency,
  compatibility, and data integrity. Resolve routine choices from code and
  repository conventions.
- Compare at least two designs when the decision is hard to reverse or the
  blast radius is large. Choose the smallest design that satisfies the complete
  requirement, then record why the rejected shape loses.
- Keep adapters and extension points when two real integrations, an explicit
  requirement, or a real invariant, safety, or testability boundary justifies
  them. Preserve requested extensibility and safety boundaries.
- Use a bounded prototype for a question about state, business logic, UI, or an
  integration that paper reasoning cannot settle. Carry its decision back into
  the real plan and keep throwaway code clearly marked.

## Decision frontier and cheap core probes

- Resolve factual unknowns from code, callers, accepted specs and bounded
  experiments. Separate these from user-owned choices about behavior,
  architecture trade-offs, risk, fidelity or scope.
- For meaningful design risk, identify a few genuinely different viable
  outcomes before implementing. If one consequential choice is user-owned and
  unresolved, apply the bounded auto-grill in [context](context.md); do not
  silently settle it by picking the existing behavior. Once known choices are
  accepted, stop questioning and continue within the authorized scope.
- Challenge a core contract against one or two meaningfully different known
  variations or failure conditions. Use the cheapest contrastive probe (a
  caller trace, state table, minimal test or throwaway prototype) that could
  falsify the boundary. A routine edit needs no probe; do not build the
  future features or a full benchmark to validate a proposed seam.
- Keep the decisions visible in domain naming, localized state ownership and
  interfaces. Retain only rationale that cannot be cheaply recovered from code.

Do not turn a routine edit into architecture work. Link a deeper design note
only when the next executor needs it to make a correct change.
