# Deliver

Deliver working code for a feature, behavior change, known-cause fix, or refactor.
Honor the requested stopping point; a request to build includes verification.
Read [context](../practices/context.md) once for evidence selection and reporting.

## Choose the slice

1. Identify user-visible behavior and an observable acceptance condition for
   each requirement, including actual compatibility, security, performance,
   accessibility, and data-loss constraints.
2. Inspect status, relevant repository instructions, affected code, real callers,
   and nearby tests. Preserve unrelated edits. Resolve routine choices from
   evidence; ask only when missing input changes correctness or intended scope.
3. Reuse existing public seams. Read [design](../practices/design.md) for unresolved
   ownership, adapter, or invariant decisions. Choose the smallest design that
   meets the complete requirement, retaining demonstrated extension needs.

Implement independently verifiable vertical slices. For mechanical migration,
use expand/migrate/contract when it preserves working callers. Keep validation
and error handling at trust boundaries; use [security](../practices/security.md)
when those boundaries change. Add dependencies, flexibility, or adjacent changes
only when the requirement or causal evidence needs them.

## Verify and finish

- Select behavioral checks with [tests](../practices/tests.md). Use red-green
  when it clarifies new behavior or a regression. Tiny reversible edits need
  inspection and the cheapest relevant check, not an artificial suite.
- Check each meaningful slice. Map every acceptance condition to actual evidence;
  keep this mapping in context unless a report needs it.
- A shared contract change needs affected-caller coverage; dependency/config
  changes need the relevant build or integration check; trust-boundary changes
  need rejection-path evidence. Complete explicit repository/user gates.
  Reuse still-valid checks instead of automatically rerunning each phase.
- For interactive UI changes, exercise the primary journey using
  [e2e](../practices/e2e.md) when browser testing is within the authorized scope.
  Include the transitions that could invalidate saved or derived state, rather
  than treating successful individual controls as a completed journey.
- Inspect the final diff for scope, missed requirements, error paths, and coupling.
  Apply [simplicity](../practices/simplicity.md) when new layers or options appear.
  Repair actionable in-scope findings and verify the affected behavior again.

For failed checks, retain the command and first useful symptom, distinguish
change-caused from pre-existing/environment failures, and fix the causal issue.
Use [build](../practices/build.md) for compiler/dependency chains or
[debug](debug.md) when diagnosis becomes the main task.

Return the result, useful file links, check verdicts, and material unchecked
limits. Commit, publish, or hand off only when existing authorization includes it.
