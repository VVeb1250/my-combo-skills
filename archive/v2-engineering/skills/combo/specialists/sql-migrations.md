# SQL schemas and migrations

Use this note for schema changes, data backfills, index work, or ORM migration
commands. Identify the database engine and migration tool first. Treat a
deployed migration as immutable history.

## Migration shape

- Every production change is a reviewed migration. Prefer a new forward
  migration to editing or running a manual fix against a deployed database.
- Separate schema changes from data backfills so lock duration, retries, and
  rollback behavior can be observed independently.
- Use expand-contract for compatibility changes: add a nullable/new field,
  deploy code that can read/write both, backfill in bounded batches, switch
  reads and writes, then remove the old field in a later release.
- Test against production-sized data and record lock, duration, replication,
  and rollback expectations. An empty development database proves little.

## Lock-aware SQL

PostgreSQL examples:

```sql
-- Safe additive shape for an existing table
ALTER TABLE users ADD COLUMN avatar_url text;

-- Avoid blocking writes on a large existing table
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

`CREATE INDEX CONCURRENTLY` cannot run in a transaction block, so configure the
migration tool accordingly. Do not add a `NOT NULL` column with no safe default
to a populated table. For large backfills, process bounded batches, use a
stable key and an observable checkpoint, and make retries safe. `FOR UPDATE SKIP
LOCKED` is useful for queue-like work, not a substitute for a consistent
accounting or integrity read.

## ORM workflows

- Prisma: use `prisma migrate dev --name ...` during development and
  `prisma migrate deploy` in production. Use `--create-only` for SQL the schema
  DSL cannot express, such as a concurrent index. Never use reset commands in
  production.
- Drizzle: generate a migration, review the SQL, then run the migration
  command. `drizzle-kit push` is a development convenience and does not replace
  production migration history. Kysely: use its configured migration runner to
  create/apply migrations, review the generated SQL, and record the migration
  in the repository's deployment path.
- Keep application schema and database state compatible during the expand and
  contract window. Add a compatibility test for old and new readers when the
  rollout spans versions.

## Preflight and rollback

1. Name the affected tables, row counts, indexes, foreign keys, and lock risks.
2. Confirm the migration is repeat-safe or has an explicit failure recovery.
3. Decide whether down/rollback is safe. In production, a forward compensating
   migration is often safer than restoring a destructive down migration.
4. Rehearse on a recent copy, monitor query latency and replication, and state
   how an interrupted backfill resumes.
5. Remove an old column or constraint only after all application versions stop
   referencing it.

Source: ECC `database-migrations`, pinned and mapped in [source-map.md](../references/source-map.md).
