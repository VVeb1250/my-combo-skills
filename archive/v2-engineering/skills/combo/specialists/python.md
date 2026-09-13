# Python

Use this note for substantive Python implementation, typing, resource
management, iterators, exceptions, or async behavior. Inspect the project's
Python version, formatter/linter, and package layout before choosing syntax.

## Boundaries and types

- Prefer clear names and explicit control flow over clever comprehensions or
  hidden import-time setup. Keep module imports cheap and side-effect free.
- Use built-in generics on Python 3.9+ (`list[str]`, `dict[str, int]`) and modern
  unions where the project version permits. Type public functions, return
  values, and data crossing module or I/O boundaries.
- Use `Protocol` when a small structural interface is enough; use a concrete
  class or an explicit abstract boundary when invariants and ownership matter.
- Model domain data with the project's established dataclass or validation
  layer. Keep mutable defaults out of shared instances and make mutability
  visible in the type or constructor.

## Exceptions and resources

- EAFP is useful when the operation itself is the race-safe check, but catch the
  narrow exception you expect. Never use a bare `except` or silently turn an
  operational failure into `None`.
- Add context while preserving the cause: `raise ConfigError("...") from err`.
  Define a small domain exception hierarchy at a package boundary and map it to
  the caller's protocol there.
- Use `with`/`async with` for files, locks, sessions, transactions, and clients.
  A custom context manager should make acquisition, cleanup, and failure
  semantics explicit.

```python
def load_config(path: str) -> Config:
    try:
        with open(path, encoding="utf-8") as stream:
            return Config.from_json(stream.read())
    except FileNotFoundError as err:
        raise ConfigError(f"config not found: {path}") from err
    except json.JSONDecodeError as err:
        raise ConfigError(f"invalid config: {path}") from err
```

## Iteration and async work

- Return an iterator or generator when the caller can consume data lazily;
  document whether it is single-use and where failures occur.
- Keep async all the way through an async call chain. Do not block an event
  loop with synchronous I/O or call `.result()` on a pending task.
- Create tasks inside a structured scope, await them, and propagate cancellation
  on timeout or caller cancellation. Close async clients and generators.
- Bound concurrency with a semaphore or queue when work fans out. Preserve
  ordering only when the contract requires it.

## Review checklist

1. Is the public boundary typed and explicit about `None`, exceptions, and
   ownership?
2. Are resources released on success, cancellation, and exceptions?
3. Do exception handlers preserve causes and avoid catching unrelated failures?
4. Does lazy or async work have a clear lifetime, backpressure, and cancellation
   path?
5. Did import-time behavior, mutable defaults, or global state change?

Source: ECC `python-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
