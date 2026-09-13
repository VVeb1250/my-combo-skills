# Redis

Use this note for Redis caches, sessions, rate limits, streams, queues, or
distributed coordination. Define durability and failure semantics before
choosing a data structure.

- Cache-aside is the default: read cache, load the source on a miss, then set
  with a bounded TTL. Version or namespace keys so deployments and tenants do
  not collide, and invalidate related keys on writes when stale data is not
  acceptable.
- Use atomic commands or a Lua/scripted operation for check-and-set, counters,
  and rate limits. A read followed by a write is a race under concurrent clients.
- Store sessions with an explicit expiry and rotation policy. Do not treat Redis
  availability as the only source of identity or authorization truth.
- Streams or a queue pattern need consumer ownership, acknowledgement,
  pending-message recovery, idempotent handlers, and a dead-letter policy. A
  retry can run the handler twice.
- Bound values, TTLs, scan work, and connection pools. Use `SCAN` instead of
  blocking `KEYS` in production and monitor memory eviction/fragmentation.
- Decide what happens when Redis is down: fail closed for a security decision,
  fail open only for a documented non-critical cache, or degrade with a clear
  timeout. Do not let an unbounded retry amplify an outage.

Source: ECC `redis-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
