---
name: ecc-language-review
description: "Review language or database-specific correctness: lifetimes, concurrency, async cancellation, ownership, transactions, schema migrations, and query behavior. Use when those mechanisms are central to a change or explicitly requested. รีวิวเฉพาะภาษาและฐานข้อมูล. Skip generic PR review and routine syntax edits."
metadata:
  owner: ecc
---

# Inspect the mechanism that can fail

Start with the actual language/runtime/database version, affected code, and
caller contract. Inspect only concerns relevant to that mechanism:

- TypeScript/JavaScript: runtime validation vs types, async error propagation,
  stale closures, effect ownership, resource cleanup, and public API compatibility.
- Python: mutable defaults, exception/resource lifetimes, iterator consumption,
  blocking work in async code, cancellation, and serialization boundaries.
- Rust/Go/C++/JVM: ownership/lifetimes, synchronization, races, cancellation,
  resource leaks, error propagation, unsafe/FFI assumptions where present.
- Databases: transaction boundaries, concurrent updates, constraints, query plans,
  N+1 behavior, index tradeoffs, and schema compatibility during rollout/rollback.

Use the repository's compiler, typechecker, linter, tests, and migration tooling.
Verify version-sensitive details in primary docs. For migration review, separate
reversibility of schema from recoverability of data. Do not run destructive
migrations on a real database just to check a hypothesis.

Report reachable defects with input/interleaving, consequence, location, and repair.
Suggest abstractions only when the actual mechanism requires them. Language
idioms do not own the general review process or override Matt's behavioral tests.
