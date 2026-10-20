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
- Run a focused test while iterating, then broaden to typecheck, lint, build,
  integration, or the full suite according to blast radius and repository
  practice.
- Map checks to acceptance: shared contracts need affected-caller coverage;
  dependency/config changes need the relevant build or integration check;
  trust boundaries need rejection-path checks. Complete explicitly requested
  suites and gates. Reuse results while their relevant inputs and code remain
  unchanged; rerun when freshness is requested or the evidence is invalidated.
- Do not add a test suite for a tiny reversible edit with no behavior risk. Do
  not test implementation details merely to increase coverage.
- If no appropriate seam exists, record the best available evidence and the
  confidence gap. That is an architecture finding, not permission to assert a
  weaker behavior as if it were equivalent.

Report the exact command, verdict, and any checks that could not run.
