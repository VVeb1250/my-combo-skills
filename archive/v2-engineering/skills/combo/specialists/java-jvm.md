# Java, Spring, and Quarkus

Use this note for Java 17+ services. Inspect the build file first: a Quarkus
dependency, Spring Boot dependency, or neither changes the applicable defaults.

- Prefer records, final fields, and immutable DTOs. Keep mutable state private
  and make the owning lifecycle clear.
- Use constructor injection for required dependencies. Spring classes usually
  use `*Controller`, while Quarkus JAX-RS resources use `*Resource`; do not
  blindly move annotations between frameworks.
- Return `Optional` from `find*` methods when absence is expected, then use
  `map`/`flatMap` or `orElseThrow` rather than calling `get()`.
- Keep stream pipelines short and transformation-oriented. A complex nested
  pipeline is usually clearer as a loop or named method.
- In Spring, put transaction boundaries on the service operation that owns the
  invariant and map validation/domain exceptions to a stable API shape. In
  Quarkus, preserve the distinction between blocking work and `Uni`/`Multi`
  reactive pipelines, and avoid blocking an event-loop thread.
- Quarkus Panache conventions may use public entity fields and build-time
  processing; apply them only in a detected Quarkus module.

Review package naming, nullability, dependency scope, transaction placement,
blocking/reactive boundaries, and whether a framework-specific annotation is
actually supported by the build.

Source: ECC `java-coding-standards`, pinned and mapped in [source-map.md](../references/source-map.md).
