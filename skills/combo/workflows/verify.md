# Verify

Exercise the requested check or user journey and report an observed verdict.
Verification-only does not authorize repair.
Read [context](../practices/context.md) once for evidence selection and reporting.

1. Identify requested coverage, revision, environment, fixture, and pass signal
   tied to behavior or an invariant. Inspect existing scripts before choosing
   commands.
2. Choose the cheapest reliable check that meets that coverage: focused test,
   typecheck, lint, build, API/integration, or E2E. If a full suite or broad gate
   was requested, run it completely; focused checks may order work, not replace
   requested coverage. Explicit fail-fast behavior remains valid.
3. For UI/cross-component journeys, use the native browser skill and
   [E2E](../practices/e2e.md). Keep secrets out of commands and captured artifacts.
   External state changes require the journey's applicable authorization.
4. Capture the actual completion signal, command, relevant output, revision,
   and environment. A started command is not a pass. Reuse earlier evidence only
   when it remains applicable and fresh verification was not requested.
5. Classify pass, fail, inconclusive, or blocked by environment/access. On failure,
   retain the first useful symptom and distinguish product, fixture, and setup
   failures. An unrelated setup error does not establish a product defect.

Report what ran and its verdict, decisive evidence/artifacts, missing coverage,
and any necessary next action. Suggest [debug](debug.md) for causal analysis or
repair without silently changing the requested stopping point.
