# Go

Use this note for Go package design, errors, concurrency, and service code.
Follow the module's Go version and existing package conventions.

- Keep the zero value useful when possible. If a type needs initialization,
  make the constructor and invalid state explicit rather than relying on a nil
  map, channel, or pointer panic.
- Accept small interfaces at the point of use and return concrete structs. Keep
  interfaces focused on the behavior a consumer needs, not on an imagined
  implementation hierarchy.
- Wrap errors with operation and safe identity context using `%w`. Use
  `errors.Is` for sentinel decisions and `errors.As` for typed details. Handle
  every error; an ignored cleanup error should be an explicit, documented choice.
- Pass `context.Context` for cancellation and deadlines, and check `ctx.Done()`
  in long loops or worker pipelines. Do not store request contexts in structs.
- Define channel ownership: the creator/producer normally closes a channel, and
  receivers should not close a channel they do not own. Join goroutines and
  return their errors instead of leaving work detached.
- Protect shared mutable state with a narrow mutex or redesign around message
  passing. Run the race detector for changes that cross goroutine boundaries.

Review nil behavior, error wrapping, context propagation, goroutine lifetime,
channel close ownership, and whether a new interface is demanded by a consumer.

Source: ECC `golang-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
