# Spring Boot

Use this note for Spring Boot REST, service, repository, transaction, DTO,
cache, or async changes. Confirm the Spring Boot and Java versions in the build.

- Keep controllers focused on HTTP parsing and response mapping, services on
  business invariants and transactions, and repositories on persistence. Do
  not put domain decisions in a controller just because the endpoint is small.
- Use constructor injection and explicit DTOs. Validate request DTOs at the
  boundary, then map to a domain command or model. Do not expose persistence
  entities as a stable public API by accident.
- Place `@Transactional` at the service operation that owns the invariant. Keep
  remote calls outside the database transaction unless the system has a proven
  coordinated protocol.
- Map domain/validation/not-found/conflict failures to a stable error body with
  `@ControllerAdvice`. Avoid returning stack traces or framework internals.
- Add pagination limits and deterministic sorting to collection endpoints. Use
  cache keys and eviction tied to the write path, and use `@Async` only with an
  executor, error policy, and shutdown behavior that the application owns.
- Propagate request correlation and safe structured logging without credentials
  or full sensitive payloads.

Source: ECC `springboot-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
