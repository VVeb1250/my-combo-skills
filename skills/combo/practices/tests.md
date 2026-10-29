# Tests

Use tests to make the requested behavior observable. Define the pass condition
in terms of public behavior, an API contract, a user journey, or a meaningful
invariant before choosing the test shape.

- Prefer the highest existing seam that can detect the real behavior. Add a new
  seam only when the existing surface cannot make the result observable. When
  proposing seams, note for each what it catches and what it misses.
- Use a focused red-green loop for new behavior and demonstrated regressions
  when it gives useful feedback. Keep the test at the call chain where the bug
  actually occurs; a shallow test can give false confidence.
- Prefer deterministic fixtures, pinned time or randomness, isolated state, and
  assertions on the specific symptom. "It did not crash" is rarely enough.
- When behavior admits a falsifiable property over a broad input space
  (round-trip, idempotence, ordering, conservation, seeded reproducibility,
  or valid map/graph reachability), consider property-based testing instead
  of enumerating only examples. Define the expected invariant independently
  of the implementation; reject tautological checks, generators that filter
  away meaningful inputs, and suites that execute no valid cases. Preserve a
  failing seed and minimal counterexample for regression. Otherwise prefer
  focused example tests. Reuse installed testing tools; do not add a property
  testing dependency or run a large randomized campaign by default.
- Run a focused test while iterating, then broaden to typecheck, lint, build,
  integration, or the full suite according to blast radius and repository
  practice.
- For a consequential change, name the one or two critical invariants that
  might be broken before expanding checks; select the smallest existing seam
  that can falsify them. Do not require this step for tiny reversible edits.
- Map checks to acceptance: shared contracts need affected-caller coverage;
  dependency/config changes need the relevant build or integration check;
  trust boundaries need rejection-path checks. Complete explicitly requested
  suites and gates. Reuse results while their relevant inputs and code remain
  unchanged; rerun when freshness is requested or the evidence is invalidated.
- For a recurring defect, first ask whether an existing architecture, type/schema,
  static check, or public-seam regression can make invalid behavior impossible
  or observable. Choose the lowest-maintenance effective enforcement and replay
  the original failure to show it would be caught. A prose rule is not a
  regression check; avoid duplicate gates without distinct failure coverage.
- Do not add a test suite for a tiny reversible edit with no behavior risk. Do
  not test implementation details merely to increase coverage.
- If no appropriate seam exists, record the best available evidence and the
  confidence gap. That is an architecture finding, not permission to assert a
  weaker behavior as if it were equivalent.

Report the exact command, verdict, and any checks that could not run.
