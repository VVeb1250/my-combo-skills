---
name: ecc-database
description: Design SQL schemas, indexes, queries, transactions, and safe database migrations. Use for query performance, concurrent updates, schema evolution, or database integrity decisions. ออกแบบฐานข้อมูลและ migration. Skip ordinary data analysis over CSV and generic code review.
metadata:
  owner: ecc
---

# Design for data integrity and actual access patterns

Identify the database engine/version, schema, workload, and existing migration
process. Use constraints for invariants the database can enforce. Select indexes
from real query predicates/order and query plans, accounting for write cost.

Check transaction boundaries, concurrent updates, uniqueness races, N+1 queries,
null behavior, parameterization, and authorization at the appropriate layer.
Choose optimistic/pessimistic coordination from the actual contention scenario.

For schema changes, consider old/new application compatibility, lock duration,
backfill size, failure recovery, and which data cannot be reconstructed by a down
migration. Use existing tooling and disposable test databases for verification.
Production migration execution needs authorization for that external state change.

For PostgreSQL examples only, read `references/upstream.md`. Supabase-specific
rules are conditional on Supabase use; do not transplant them to every database.
