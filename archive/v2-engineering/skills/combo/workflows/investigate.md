# Investigate

Use this path when the user wants to understand code, trace behavior, compare
technical options, or investigate a repository without changing it.

## Bound the question

1. Restate the question and the decision or explanation it must support. Define
   the relevant time/version/environment boundary when facts can change.
2. Inspect the smallest useful set of primary evidence: repository instructions,
   entrypoints, real callers, data/control flow, tests, configuration, commits,
   and authoritative external documentation when needed.
3. Map the relevant path from input to output, including error boundaries,
   persistence, side effects, and ownership. Stop expanding once the evidence
   answers the question.
4. Label statements as observed fact, inference, or unresolved uncertainty.
   Test a cheap discriminating hypothesis with a read-only command when useful.

For a nontrivial investigation, keep concise source and observation notes in
current context or an existing task artifact. Prefer a few strong sources over
a broad catalog. If current or niche external facts matter, check an
authoritative primary source and record its version or date; otherwise keep the
investigation inside the repository.

For a comparison, state the criteria first, evaluate each option against the
actual constraints, and recommend one path. Preserve a rejected option only
when its tradeoff matters. If a design question cannot be settled without
running code or seeing a UI, say what bounded prototype or plan would resolve it
and stop at investigation unless the user requested that next step.

## Output

Give the answer early, then the evidence that makes it credible. Include paths,
symbols, versions, or commands that another engineer can inspect, followed by
uncertainties and a concrete next move. Do not create code, tracker items,
decision files, external jobs, or a custom harness by default. If the evidence
reveals a repair or implementation request, state the appropriate next route
without silently switching the stopping point.
