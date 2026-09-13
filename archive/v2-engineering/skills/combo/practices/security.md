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
- If the risk is outside the requested scope, name it and preserve the user's
  required behavior. Do not invent a broad security rewrite.

Treat security findings as practical risks with a trigger, consequence, and
smallest effective remedy. Do not label an unexercised concern as verified.
