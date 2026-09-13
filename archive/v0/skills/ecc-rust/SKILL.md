---
name: ecc-rust
description: Implement Rust behavior involving ownership, borrowing, errors, traits, or async concurrency. Use for substantive Rust code and design decisions around these mechanisms. เขียน Rust. Skip trivial formatting and generic reviews without a Rust-specific concern.
metadata:
  owner: ecc
---

# Make ownership and failure explicit

Follow the crate's edition, toolchain, API, and dependency conventions. Prefer
borrowing over avoidable cloning, Result over panic for expected failures, and
concrete types until a real abstraction boundary calls for a trait.

Check lock scope, await boundaries, cancellation/resource cleanup, and public
compatibility. Unsafe code needs explicit invariants checked at its boundary;
do not broaden unsafe or use unchecked operations merely to silence the compiler.
Do not add Arc/Mutex, generics, or a crate without a demonstrated requirement.

Use the crate's tests, cargo check/build, formatting, and lint commands according
to the change. For detailed idioms, consult `references/upstream.md` selectively.
Testing process belongs to Matt; this reference contributes Rust-specific checks.
