# Simplicity

Use this lens when a change adds abstractions, configuration, dependencies,
layers, retries, or a broad refactor, or when the user asks for simplification.
The goal is a smaller maintainable design that still meets the full requirement.

- Before adding code, check existing code, the standard library, native
  platform facilities, and installed dependencies in that order. A project's
  own component or helper beats a native or standard-library equivalent.
- Challenge single-use wrappers, dead flexibility, unused parameters,
  speculative extension points, and abstractions with no demonstrated second
  use when evidence shows they are unnecessary. Keep a cohesive module that
  hides substantial behavior or enforces an invariant, even with one caller.
- Watch for duplicated logic, long message chains, primitive domain concepts,
  shotgun edits, divergent responsibilities, and middle-man layers. Fix only
  what the task or the new change makes relevant.
- Preserve validation, data-loss protection, security, accessibility, explicit
  user requirements, and proven adapters. Fewer lines is not a reason to remove
  a necessary boundary. Code that is moved or merged keeps its validation and
  error handling.
- Do not perform unrelated cleanup or enforce a line-count target. Match the
  repository's style when it does not conflict with correctness.

For a review, phrase a complexity finding as location, what to cut, and what
replaces it, or say the code is already lean. For implementation, apply the
smallest justified simplification before broadening scope.
