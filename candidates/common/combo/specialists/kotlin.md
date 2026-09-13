# Kotlin coroutines and Flow

Use this note for Kotlin or Kotlin Multiplatform coroutine, Flow, cancellation,
or lifecycle code. Match the Android/KMP and coroutine versions in the build.

- Use structured scopes tied to a lifecycle, such as `viewModelScope` or a
  caller-owned `coroutineScope`; do not use `GlobalScope` for application work.
- Use `coroutineScope { async { ... } }` for independent operations that should
  fail together. Use `supervisorScope` when one child may fail while siblings
  continue, and collect/join all children before returning.
- Expose long-lived UI state as `StateFlow`, commonly with `stateIn` and a
  lifecycle-aware `SharingStarted.WhileSubscribed` policy. Keep one-time events
  separate with `SharedFlow` or an explicit event channel.
- Compose streams with `combine`, `debounce`, `distinctUntilChanged`, and
  `flatMapLatest` when the latest query cancels stale work. Use `catch` and
  bounded `retryWhen` for recoverable failures, preserving cancellation.
- Do not swallow `CancellationException`, launch work outside the owner scope,
  or hold a lock across a suspension point. Test cancellation and virtual time
  at the coroutine boundary.

Source: ECC `kotlin-coroutines-flows`, pinned and mapped in [source-map.md](../references/source-map.md).
