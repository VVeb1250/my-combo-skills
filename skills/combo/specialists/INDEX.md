# Coding specialist index

Use this shelf when a technical mechanism remains unresolved after reading the
relevant project evidence. Search the table for that mechanism and open only
the needed notes; use an already-known note path directly. A direct workflow
entry needs no router reread, and a technology name alone needs no shelf read.
Version-sensitive framework behavior still needs a check against the project's
lockfile and current official documentation.

| Task or signal | Note |
| --- | --- |
| REST/HTTP resources, status codes, pagination, errors, versioning | [http-api.md](http-api.md) |
| React components, hooks, TSX state, Server Components, forms | [react-typescript.md](react-typescript.md) |
| Python typing, exceptions, resources, iterators, async code | [python.md](python.md) |
| Rust ownership, errors, traits, enums, async/concurrency | [rust.md](rust.md) |
| SQL schema changes, migrations, backfills, zero downtime, ORM migration | [sql-migrations.md](sql-migrations.md) |
| MCP tools/resources/prompts, stdio, Streamable HTTP, SDK upgrades | [mcp.md](mcp.md) |

## Rare framework and infrastructure catalog

| Technology signal | Note | Distinctive checks |
| --- | --- | --- |
| Angular Signals, DI, forms, route loading, SSR | [angular.md](angular.md) | Check Angular version; use sidecar refs for exact APIs |
| Bun runtime, lockfile, built-in test runner | [bun.md](bun.md) | Confirm dependency compatibility before replacing Node |
| Bun 1.4 runtime, `bun audit`, test flags | [bun-1-4.md](../references/addenda/bun-1-4.md) | Check the installed Bun version before using flags |
| Modern C++ ownership and RAII | [cpp.md](cpp.md) | Rule of Zero, strong types, lifetime/thread boundaries |
| Django and Django REST Framework | [django.md](django.md) | Settings split, QuerySets, transactions, cache and signals |
| Dockerfiles, Compose, image hardening | [docker.md](docker.md) | Multi-stage build, health gates, non-root runtime |
| .NET/C#, DI and cancellation-aware async | [dotnet.md](dotnet.md) | Nullable contracts, options binding, async all the way |
| FastAPI and Pydantic v2 | [fastapi.md](fastapi.md) | App factory/lifespan, dependency-injected sessions |
| Go errors, zero values, channels | [go.md](go.md) | Context cancellation, channel ownership, wrapped errors |
| Java 17+, Spring, or Quarkus | [java-jvm.md](java-jvm.md) | Detect build framework before applying conventions |
| Kotlin coroutines and Flow | [kotlin.md](kotlin.md) | Structured scopes, StateFlow lifecycle, cancellation |
| Kubernetes workloads and manifests | [kubernetes.md](kubernetes.md) | Probe roles, resources, RBAC, rollout and debug commands |
| NestJS modules, DTOs, guards, interceptors | [nestjs.md](nestjs.md) | Thin controllers, global validation, exception shape |
| Next.js App Router and Turbopack | [nextjs.md](nextjs.md) | Check version, proxy.ts versus middleware.ts |
| PostgreSQL types, indexes, plans, JSONB | [postgres.md](postgres.md) | EXPLAIN and index/order tradeoffs |
| Prisma queries, transactions, pagination | [prisma.md](prisma.md) | select/include, N+1, client lifecycle |
| React Native or Expo | [react-native.md](react-native.md) | Virtualized lists, route params, secure token storage |
| Redis caches, rate limits, streams | [redis.md](redis.md) | TTL/invalidation and atomicity/failure behavior |
| Spring Boot web and data services | [springboot.md](springboot.md) | Service transactions, DTOs, exception mapping |
| Swift 6.2 concurrency | [swift.md](swift.md) | Isolation, MainActor inference, @concurrent boundaries |
| Dart/Flutter state, routing, Dio | [flutter.md](flutter.md) | Null safety, sealed state, retry guard, rebuild scope |
| Vue components, composables, Pinia | [vue.md](vue.md) | Props/events contracts and SSR-safe state |

The [source map](../references/source-map.md) records the pinned source,
adaptation decision, rationale, destination, and archived competing owners.
Angular's linked deep references live under [references/angular](../references/angular/).
Adapted ECC notes are MIT-licensed, with the notice at
[references/licenses/ecc.txt](../references/licenses/ecc.txt). The source map
also records the preserved notices for Karpathy, Ponytail, and Matt material
used by the rest of the combo package.
