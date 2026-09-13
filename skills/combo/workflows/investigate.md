# Investigate

Answer a code/architecture question or compare technical options without edits.
Read [context](../practices/context.md) once for evidence selection and reporting.

1. Bound the question, decision, and relevant version/environment.
2. Inspect primary evidence along the actual input-to-output path: entrypoint,
   callers, transformations, error boundaries, persistence, ownership, and tests.
   Expand only to explain an unresolved link, counterexample, or contract.
3. Separate observations from inference. Use a read-only discriminating probe
   when it can settle the question. For changing or uncertain external facts,
   verify authoritative documentation and retain version/date.
4. For comparisons, state criteria from the user's constraints, evaluate viable
   options, and recommend one. Retain a rejected option only for a material
   tradeoff.

Finish once the path and evidence answer the requested question, or state the
precise missing evidence. Give the conclusion, inspectable paths/symbols or
sources, and a concrete next move. A prototype or repair outside investigation
is a recommendation, not permission to edit, create a harness, or publish.
