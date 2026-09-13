# PostgreSQL

Use this note for PostgreSQL schema, index, query-plan, JSONB, full-text, or
concurrency decisions. Pair it with [sql-migrations.md](sql-migrations.md) for
deployment order and lock-safe rollout.

- Choose types for semantics: `timestamptz` for instants, `numeric` for exact
  money/quantities, and constrained text or lookup tables for changing status
  values. Make nullability reflect the domain rather than convenience.
- Design indexes from real predicates and orderings. Put equality columns before
  range/sort columns when that matches the query, and use partial or covering
  indexes only after measuring the write/storage cost.
- Run `EXPLAIN (ANALYZE, BUFFERS)` on a representative dataset for a slow query.
  Check row estimates, scan type, join order, sort/temp work, and buffer reads;
  an index that helps one query may hurt writes or another plan.
- Use `jsonb` when the document shape genuinely varies and queried fields are
  indexed deliberately. Normalize high-value relational constraints instead of
  hiding them in JSON.
- Use `SELECT ... FOR UPDATE` only for a known row-lock invariant, keep
  transactions short, and define retry behavior for serialization/deadlock
  errors. Avoid holding locks while making remote calls.

Before changing a query, capture its current plan, cardinality, latency, and
concurrency context. Recheck the plan after the migration and statistics settle.

Source: ECC `postgres-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
