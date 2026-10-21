# Security lens

Activate this lens when work crosses authentication or authorization, untrusted
input, secrets, uploads, shell or SQL execution, sensitive data, external side
effects, or a meaningful data-loss boundary. It is selective, not a mandatory
pipeline for every code change.

- Identify the trust boundary, asset, actor, and authorization decision before
  changing the path. Validate untrusted data at the boundary with the narrowest
  accepted shape and preserve safe encoding or parameterization.
- Check authentication and authorization separately. Enforce least privilege,
  tenant or resource ownership, and safe defaults before irreversible side
  effects.
- Keep secrets out of source, logs, errors, screenshots, fixtures, and handoff
  artifacts. Redact captured evidence and avoid returning sensitive internals.
- Consider replay, idempotence, rollback, rate limits, file/path traversal,
  injection, SSRF, unsafe deserialization, and race conditions when the path
  makes them relevant.
- Prefer an existing vetted platform or library mechanism. Add a focused test
  or review check for the boundary and report the exact evidence.
- For dependency risk beyond known advisories (existence, publishers, install scripts,
  maintenance), a registry-metadata collector such as Trail of Bits'
  `supply-chain-risk-auditor` reports each signal as assessed-clean, assessed-flagged, or
  unassessable and refuses to report when nothing could be measured. It calls registry
  and advisory hosts and reads the GitHub CLI token when `gh` is on PATH, so run it only
  with that authorized, or with `gh` absent. A package never confirmed to exist in its
  registry is unassessable even when an advisory lookup returns nothing.
- If the risk is outside the requested scope, name it and preserve the user's
  required behavior. Do not invent a broad security rewrite.

Treat security findings as practical risks with a trigger, consequence, and
smallest effective remedy. Do not label an unexercised concern as verified.
