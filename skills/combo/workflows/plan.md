# Plan

Produce an actionable requirements, design, or implementation plan. Plan-only
ends with the plan; building or prototyping requires applicable authorization.
Read [context](../practices/context.md) once for evidence selection and reporting.

1. Identify the outcome, constraints, compatibility obligations, and requested
   fidelity. Inspect relevant code, real callers, tests, domain terms, and ADRs.
2. Resolve routine details from evidence. Surface unknowns only when they change
   behavior, contracts, integrity, security, cost, or scope. Use primary sources
   with version/date for changing external facts.
3. Compare viable approaches against these constraints and recommend one.
   Keep an alternative only when its tradeoff affects the decision.
4. Preserve existing adapters and public seams. Use [design](../practices/design.md)
   for unresolved boundaries and [tests](../practices/tests.md) for acceptance.
   If an uncertainty needs a runnable prototype, run it only within the requested
   scope and host mode; otherwise specify the bounded experiment in the plan.
5. Express implementation as vertical slices with observable done conditions and
   genuine dependencies. For broad migrations, use expand/migrate/contract to
   keep callers working between steps where feasible.

The plan is ready when an executor can identify affected areas, required contract
behavior, the chosen approach, acceptance checks, and the first action, with
decision-changing unknowns resolved or explicitly assigned. Stop exploring
equivalent alternatives at that point.

A bounded plan can live in the response. Use existing artifact conventions for
multi-session or independent execution when useful. Include rationale and risks
that change execution; create trackers or additional specs only when requested
or necessary for the agreed deliverable. Ask only the smallest unresolved
question that changes the plan.
