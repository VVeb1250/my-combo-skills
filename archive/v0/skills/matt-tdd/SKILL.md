---
name: matt-tdd
description: Build or fix behavioral code with focused regression tests and vertical red-green cycles. Use for bugs in logic, parsers, state transitions, new testable behavior, or explicit TDD. เขียน test และแก้ bug เชิงพฤติกรรม. Skip docs, formatting, and trivial reversible configuration edits.
metadata:
  owner: matt
---

# Test behavior at public seams

Use the project's existing test runner and public API vocabulary. Select the
highest practical public interface that observes the actual behavior. Reuse
established seams without asking for approval again.

For a defect, reproduce its triggering input. Write one test with an independent
expected outcome and confirm it fails for the reported defect, not an import,
environment, or unrelated setup error. Fix the root cause with the smallest
correct change. Run the test and relevant neighboring checks.

For new behavior, work one vertical slice at a time: one meaningful failing
behavior test, enough implementation to pass, then the next behavior. Avoid a
batch of tests against an imagined implementation.

Tests should survive internal refactors. Avoid private-method assertions,
tautological expected values, internal-collaborator mocks, and incidental snapshots.
Mock slow or nondeterministic external boundaries when needed; exercise the real
logic being changed. Include boundary/failure cases according to actual risk.

Do not force a new framework, coverage percentage, per-function suite, or tests
that mirror reversible low-impact configuration. Existing failing tests are
evidence to investigate, not permission to weaken assertions or skip checks.
Keep behavior-preserving cleanup bounded and verified; wider redesign belongs
to a separately justified change. Report what failed before and passed after.
