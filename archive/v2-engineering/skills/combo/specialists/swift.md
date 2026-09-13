# Swift 6.2 concurrency

Use this note for Swift 6.2 concurrency migration, actor isolation, or
background work. Verify the Swift language mode and compiler settings because
isolation inference differs between versions and build configurations.

- Make isolation part of the API design. Keep UI state on `@MainActor`, use
  actors for shared mutable state, and mark conformances/requirements with the
  isolation the protocol actually permits.
- Swift 6.2 approachable-concurrency modes can infer MainActor isolation for
  suitable application code. Treat that as a compiler-mode contract and inspect
  warnings before assuming a background operation is offloaded.
- Use `@concurrent` where supported to state that an async function may execute
  away from its actor. Keep captured values Sendable and avoid hidden mutable
  global/static state.
- Do not make every type `@MainActor` to silence diagnostics. Separate UI
  orchestration from CPU/I/O work, then test the boundary for data races and
  cancellation.
- During migration, classify each warning as an intended isolation boundary,
  a missing `Sendable` contract, or an unsafe shared state. Fix the design at
  that boundary instead of adding unchecked escape hatches.

Source: ECC `swift-concurrency-6-2`, pinned and mapped in [source-map.md](../references/source-map.md).
