# Review

Review the requested code, diff, branch, or security concern without editing or
publishing unless authorized. Read [context](../practices/context.md) once for
evidence selection and reporting.

1. Resolve the target/revision. If omitted, inspect the current diff and state
   the safe assumption. Confirm the target exists and has reviewable material.
2. Read the originating requirement and affected callers, tests, configuration,
   and conventions. Cover the requested scope even when early files look clean.
3. Evaluate requirement fidelity (missing, incompatible, partial, or extra
   behavior) and implementation quality (correctness, error boundaries, data,
   concurrency, security, and maintainability) in one impact ranking. When
   volume or concurrency matters, state the load assumed (from the README or
   deploy config) and judge scale against it.
4. For each candidate finding, establish location -> reachable trigger ->
   consequence -> evidence -> smallest remedy. Inspect guards and callers that
   could invalidate it; use a focused non-mutating probe when useful.
5. Consolidate symptoms of the same cause while preserving distinct impacts.
   Report supported actionable issues; separate an unresolved concern when the
   missing evidence matters. Style preferences and clean lint are not behavioral
   findings or proof of correctness.

Use [security](../practices/security.md) for actual trust boundaries and
[simplicity](../practices/simplicity.md) for unnecessary layers/options. Additional
reviewers or full suites are conditional, not a universal pipeline.

Lead with the highest-impact findings and precise locations. Include checks and
material unreviewed limits without repeating the whole investigation. If no
material issue is found, say so with the evidence and its limits. For an
authorized repair, continue through [deliver](deliver.md); review-only stops here.
