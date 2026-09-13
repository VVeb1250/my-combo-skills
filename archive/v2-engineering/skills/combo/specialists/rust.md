# Rust

Use this note for Rust ownership, errors, state modeling, traits, async code,
or concurrency. Read the crate's edition, feature flags, and existing error
types before adding a dependency.

## Ownership and interfaces

- Borrow (`&T` or `&mut T`) when a function only reads or temporarily mutates.
  Take ownership when the function stores, consumes, or transfers the value.
  Avoid cloning solely to silence the borrow checker.
- Use `Cow` when a fast path can borrow and a normalization path must allocate.
- Prefer concrete return types and trait bounds at the boundary. Use a trait
  object (`dyn Trait`) when heterogeneous values or runtime plugins are required;
  use generics when static dispatch and monomorphization are the right tradeoff.
- Keep `pub` surfaces small. Newtypes distinguish identifiers and units at
  compile time, and enums model legal states instead of boolean combinations.

## Errors and state

- Propagate expected failure with `Result` and `?`, adding context at I/O and
  protocol boundaries. Production `unwrap`/`expect` needs a proven invariant;
  otherwise return or map the error.
- Libraries generally expose typed `thiserror` variants. Applications can use
  `anyhow` at the top-level boundary while retaining source/context for logs.
- Use `Option` combinators for simple optional transforms, but use explicit
  matching when it communicates a state transition. Match business enums
  exhaustively; a wildcard can hide a newly added variant.

```rust
#[derive(Debug, thiserror::Error)]
pub enum StorageError {
    #[error("record not found: {id}")]
    NotFound { id: String },
    #[error("connection failed")]
    Connection(#[from] std::io::Error),
}
```

## Concurrency and async

- Choose ownership before synchronization. `Arc<Mutex<T>>` is appropriate for
  shared mutable state with short critical sections; channels are clearer for
  ownership transfer and worker pipelines. Do not hold a lock across `.await`.
- Propagate cancellation and shutdown through the runtime's task handles or
  channels. Join spawned tasks and define what partial failure means.
- Keep unsafe code behind a small documented boundary with an invariant and a
  focused test. Prefer safe standard-library primitives and value semantics.

## Review checklist

Check lifetime and ownership rather than accepting unexplained clones, inspect
error context and panic paths, confirm every enum state is handled, verify
trait-object versus generic dispatch is intentional, and look for locks held
across await points or detached tasks that outlive their owner.

Source: ECC `rust-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
