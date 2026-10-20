# Debug

Use for a failure, regression, wrong result, flaky behavior, or performance
problem. For diagnosis-only, stop with evidence and a repair proposal.
Read [context](../practices/context.md) once for evidence selection and reporting.

## Establish and distinguish

1. Identify the reported input, environment, expected result, and exact symptom.
   Inspect affected code, real callers, relevant instructions, and recent changes.
   Choose the cheapest check that distinguishes fixed from unfixed.
2. Prefer a deterministic repro, request, journey, trace replay, or timing
   harness. If reproduction is unavailable, use logs, the reported input, and
   known-good comparisons; distinguish observed, inferred, and unknown claims.
   Verify that any reproduced failure is the user's symptom.
3. For performance, measure a baseline. For build/type failures, group dependent
   errors and inspect the earliest causal one using [build](../practices/build.md).
4. When causes compete, use a short hypothesis -> distinguishing probe ->
   observation -> next action loop. Change one relevant variable. If a probe
   cannot separate explanations, choose another boundary instead of repeating
   it. Trace shared transformations, configuration, lifecycle, or concurrency
   only as the signal requires. Prefer a debugger/REPL or targeted instrumentation;
   tag temporary logs and keep secrets out.

Use [security](../practices/security.md) when the failing path crosses a real
trust or sensitive-data boundary. Lack of reproduction alone is not a blocker.

## Repair within authorization

- Convert the repro into a regression at the highest existing seam that detects
  this defect. If no suitable seam exists, keep integration/E2E evidence and
  identify the confidence gap. Use [tests](../practices/tests.md) for seam choices.
  If you forced the red by mutating code or a fixture, diff against a pristine
  copy to confirm the mutation landed before trusting the failure.
- Make the smallest causal repair, preserving real callers' contracts. Retries,
  catches, or refactors need evidence that they address the cause.
- Check the regression and original unminimized symptom; one run can cover both.
  Broaden for affected callers, contracts, dependencies, or required gates.
- Remove diagnostic-only instrumentation; retain durable regression fixtures.
  After relevant checks pass, finish unless new changes or evidence require more.

Report the cause with its evidence/confidence, repair if authorized, and observed
verification. Distinguish fixed, reproduced, not reproduced, inconclusive, and
blocked outcomes. If decisive access is missing, state the exact gap and next
discriminating check while completing independent authorized work.
