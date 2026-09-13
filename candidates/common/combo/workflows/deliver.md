# Deliver

Use this path for a requested feature, behavior change, bug fix whose cause is
already clear, or behavior-preserving refactor. The output is working code at
the user's requested stopping point.

## Understand the slice

1. Restate the user-visible behavior and the smallest observable success check.
   Include compatibility, security, performance, or data-loss constraints that
   are actually present.
2. Read repository instructions, the affected modules, real callers, and nearby
   tests. Inspect status before editing and preserve unrelated user changes.
3. Separate observed facts, assumptions, and decisions. Resolve routine choices
   from the codebase. Ask one focused question only when an answer changes
   correctness or the requested scope.
4. Choose the narrowest design that satisfies the complete requirement. Prefer
   an existing public seam. Use [design](../practices/design.md) when module
   boundaries, adapters, or invariants need explicit thought.

For a multi-part change, split along independently verifiable vertical behavior
slices. Keep each slice small enough to understand and check in the current
context. A wide mechanical refactor may use expand, migrate, and contract steps
when keeping the old form temporarily is what keeps callers green.

## Implement

- Change the smallest correct set of files. Do not add speculative options,
  dependencies, abstractions, or adjacent cleanup.
- Use [tests](../practices/tests.md) to select the highest seam that can observe
  the requested behavior. Use a red-green test-first loop when it clarifies a
  new behavior or regression; a trivial reversible edit needs no artificial
  test suite.
- Keep validation at trust boundaries and preserve accessibility, error
  handling, and explicit user requirements. Add [security](../practices/security.md)
  only when the change crosses a real security or data boundary.
- Run the narrowest useful check after each meaningful slice. Group compiler or
  dependency errors by causal root with [build](../practices/build.md).

## Finish

1. Re-run the focused behavior check and then broaden to typecheck, lint, build,
   integration, or full tests in proportion to the blast radius.
2. Inspect the diff for accidental changes, dead code created by this work,
   error-boundary regressions, and hidden coupling. Apply the [simplicity](../practices/simplicity.md)
   lens when the change has new layers or flexibility.
3. Review requirement fidelity and implementation quality proportionally. Fix
   findings that are within the user's authorized scope; leave a finding for
   anything that needs a separate decision.
4. Report changed files, user-visible result, checks with their verdicts, and
   any check that could not run. A commit, issue publication, or handoff is a
   separate action unless the request or repository workflow already includes
   it.

If a check fails, retain the exact command and useful output in the state
snapshot, identify whether the failure is caused by this change, and continue
with the smallest corrective step or route to [debug](debug.md) when diagnosis
has become the dominant task.
