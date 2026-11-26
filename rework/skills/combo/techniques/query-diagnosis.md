# Query diagnosis

Trace the slow user operation through actual callers to query count, parameters, data distribution, concurrency and returned rows. Separate round trips, execution, serialization and rendering before changing indexes or caching.

Compare plans and measured latency on representative data and parameters. Inspect estimated vs actual cardinality, scans/joins, repeated loops, sorts/spills and I/O or lock waits when available. Large estimation errors suggest a different probe from a missing index. Use engine-specific plan tooling; verify whether it executes the query (e.g. PostgreSQL EXPLAIN ANALYZE executes it). Never run a mutating probe against shared data without authority and isolation.

Evaluate the candidate under the same workload, including write/storage cost, changed result semantics and affected queries. Do not infer improvement from plan shape alone. Preserve the actual reproducible bottleneck and measurement limits if future decisions depend on them.
