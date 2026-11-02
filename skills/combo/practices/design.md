# Design and seams

Use this practice when the change crosses modules, introduces an adapter, or
requires a non-obvious state or data decision. Start from the user outcome and
the current domain language.

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

Do not turn a routine edit into architecture work. Link a deeper design note
only when the next executor needs it to make a correct change.
