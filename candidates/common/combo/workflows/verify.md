# Verify

Use this path when the user asks to run checks, validate a build, or exercise a
real user journey. The task ends with an observed verdict and its limits. Do not
silently implement a fix during verification.

## Choose the check

1. Identify the exact requested outcome, target revision, environment, fixture,
   and any explicit stopping point. Inspect repository scripts and conventions
   before inventing commands.
2. Define a pass signal tied to user-visible behavior or a concrete invariant.
   Pick the cheapest reliable check: focused test, typecheck, lint, build,
   integration path, API request, or E2E journey.
3. For a UI or cross-component journey, use the host's native browser skill and
   its current session capabilities. Follow [E2E](../practices/e2e.md) for
   fixtures, screenshots, console/network evidence, and environment diagnosis.
4. Redact secrets from commands, outputs, screenshots, and captured artifacts.
   Do not broaden scope or alter external state unless the requested journey
   requires it and the action is authorized.

## Run and classify

- Run the selected check and capture the command, relevant output, revision, and
  environment details needed to interpret it.
- Classify the result as **pass**, **fail**, **inconclusive**, or **blocked by
  environment/access**. A command that starts is not proof of a pass. A failed
  unrelated setup step is not proof that the product behavior fails.
- If the check fails, preserve the first useful symptom and identify whether it
  points to a product defect, a test/fixture defect, or an environment issue.
  Recommend [debug](debug.md) when repair or causal analysis is the next task.
- If the user asked for a broad gate, begin with focused evidence and broaden
  only as the actual change or journey warrants. Do not run a full suite merely
  for ceremony.

## Report

State what was exercised, the observed verdict, evidence, checks not run, and
the smallest next action. For E2E, include the user path and artifacts that
make the result inspectable. Never fabricate a result for a check that could not
run.
