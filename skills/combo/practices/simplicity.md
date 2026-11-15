# Simplicity

Use this lens when a change adds abstractions, configuration, dependencies,
layers, retries, or a broad refactor, or when the user asks for simplification.
Minimize accidental complexity, not required capability, quality, or the
effort needed to deliver them. Be economical about the solution, thorough about
the change. A simpler candidate that loses fidelity, required variation,
performance, or behavior is not a complete solution. Finish every necessary
caller, test, fixture and integration; do not mistake fewer lines for success.
When no small faithful method exists, implement the necessary complexity in
cohesive modules. For material uncertainty, use the design and actual-output
evidence practices; do not cut discovery to get a shorter implementation.

- Before adding code, check existing code, the standard library, native
  platform facilities, and installed dependencies in that order. A project's
  own component or helper beats a native or standard-library equivalent.
- Challenge single-use wrappers, dead flexibility, unused parameters,
  speculative extension points, and abstractions with no demonstrated second
  use when evidence shows they are unnecessary. Keep a cohesive module that
  hides substantial behavior or enforces an invariant, even with one caller.
- Minimize total future rework, not just diff size. A known required variation
  can justify a small extension seam; a hypothetical possibility cannot.
- Track structural debt at changed hotspots: scattered domain decisions,
  special-case patches, unclear state ownership and shotgun changes. Inspect
  architectural evidence immediately rather than waiting for failed retries;
  major out-of-scope rewrites still need approval.
- Minimize reader load: collapse pointless forwarding layers and localize state,
  while preserving deep modules that hide meaningful behavior. Do not impose
  file-length quotas or refactor healthy unrelated code.
- Watch for duplicated logic, long message chains, primitive domain concepts,
  shotgun edits, divergent responsibilities, and middle-man layers. Fix only
  what the task or the new change makes relevant.
- Treat an overfull folder as a *navigation signal*, never an automatic file-count
  violation. Inspect whether unrelated responsibilities share one directory,
  whether names help locate an owner, and whether meaningful domain/feature
  subdirectories would shorten the path from a behavior question to its code.
  Keep a cohesive flat directory when a split would only add indirection.
- For a justified folder reorganization, prefer mechanical moves with unchanged
  behavior, preserve imports/entrypoints/config/tests, and verify affected callers.
  Separate mechanical moves from behavior changes when that makes rollback and
  review more reliable. Do not reorganize the whole repository as drive-by cleanup.
- Preserve validation, data-loss protection, security, accessibility, explicit
  user requirements, and proven adapters. Fewer lines is not a reason to remove
  a necessary boundary. Code that is moved or merged keeps its validation and
  error handling.
- Do not perform unrelated cleanup or enforce a line-count target. Match the
  repository's style when it does not conflict with correctness.

For a review, phrase a complexity finding as location, concrete cost, what to
cut, and what replaces it, or say the code is already lean. Keep style and
possible smells distinct from correctness defects; repository standards and
actual constraints override generic heuristics. Simplify as part of delivery
only when it improves the requested result or prevents a demonstrated problem.
