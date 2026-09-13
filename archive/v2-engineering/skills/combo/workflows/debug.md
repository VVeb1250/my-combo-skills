# Debug

Use this path when the user reports a failure, regression, exception, wrong
result, flaky behavior, or performance problem and wants it understood or
repaired. The target is a causal repair supported by evidence, with verification
at the user's original symptom.

## Establish the signal

1. Read relevant repository instructions, `CONTEXT.md` and nearby ADRs when
   present, then inspect the affected callers and recent changes.
2. Define the exact symptom, input, environment, expected result, and the
   cheapest check that could distinguish fixed from unfixed.
3. Prefer a tight failing test, fixture, CLI/API request, browser journey, trace
   replay, or timing harness. Make it deterministic and specific to the
   reported behavior. Narrow it when practical, but do not turn setup into a
   ritual.
4. If no reproduction is available, continue from the reported input, logs,
   traces, code path, or known-good comparison. Mark each claim as observed,
   inferred, or unknown. Lack of reproduction does not prohibit an evidence-
   based hypothesis and does not automatically make the task blocked.

Do not confuse a nearby failure with the user's bug. For a performance issue,
measure a baseline before changing code. For a build or type failure, group
messages by dependency and repair the earliest causal error first.

## Narrow the cause

- Trace shared callers, data transformations, configuration, error boundaries,
  and concurrency or lifecycle assumptions. Look for the smallest boundary at
  which the symptom can be explained.
- When multiple explanations are plausible, choose the smallest set of ranked,
  falsifiable hypotheses needed to select the next probe. State the observation
  that would increase or reduce confidence. Hypotheses are working
  explanations, not verified causes, and do not need user reapproval before a
  cheap discriminating check.
- Change one relevant variable at a time. Prefer a debugger or REPL, then a
  targeted log or metric at a boundary that distinguishes hypotheses. Tag
  temporary logs so they can be removed in one search. Never log everything by
  default or expose secrets.
- Use [security](../practices/security.md) if the path crosses auth, untrusted
  input, secrets, uploads, external side effects, or sensitive data. Use
  [build](../practices/build.md) for compiler and dependency failures.

## Repair and verify

1. Turn a minimized repro into a regression test at the highest seam that
   exercises the real bug pattern. If that seam does not exist, use the best
   available end-to-end or integration evidence and record the confidence gap.
2. Apply the smallest root-cause repair. Do not mask the symptom with retries,
   broad catches, or unrelated refactors unless evidence requires them.
3. Re-run the regression or discriminating check, then the original unminimized
   signal. Broaden checks according to blast radius.
4. Remove temporary instrumentation and diagnostic-only harnesses created by
   this diagnosis. Retain regression tests or fixtures that encode the defect
   or provide durable verification. Re-check that the original symptom is gone
   and state whether the cause is verified or still only the best-supported
   explanation.

If the environment or artifact needed for a decisive check is unavailable,
report the exact gap, the evidence already gathered, and the next check that
would resolve it. Continue useful code analysis; stop only when no authorized
or safe progress remains. A final report must distinguish fixed, reproduced,
not reproduced, inconclusive, and blocked states.
