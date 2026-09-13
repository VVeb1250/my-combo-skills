# Prisma ORM

Use this note for Prisma schema, query shape, transactions, pagination, or
client lifecycle. Keep the generated client and migration history aligned with
the repository's deployment process.

- Use `select` to request the smallest shape a caller needs. Use `include` when
  a relation is deliberately part of the response, and inspect nested access
  for N+1 queries or unexpectedly large payloads.
- Prefer a singleton PrismaClient in a long-lived process and a controlled
  lifecycle in scripts/serverless environments. Do not create a new client per
  request without a proven runtime reason.
- Choose the transaction form from the invariant: an interactive transaction
  for dependent logic, a batch transaction for independent writes, and a normal
  single write when the database constraint already protects the operation.
  Keep the callback short and do not perform remote calls inside it.
- Use cursor pagination for feeds and large sets. Order by a stable unique key,
  pass the cursor from the last row, fetch one extra row for `hasNextPage`, and
  avoid offset pagination once data volume makes it unstable or expensive.
- Treat soft delete as a query policy that every read path must honor. A unique
  constraint and restore flow need an explicit design; a `deletedAt` field alone
  does not prevent accidental exposure.

Review generated SQL/query count, transaction retry behavior, client reuse,
cursor ordering, and migration compatibility with old application binaries.

Source: ECC `prisma-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
