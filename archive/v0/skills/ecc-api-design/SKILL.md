---
name: ecc-api-design
description: Design or change HTTP API contracts, resource names, pagination, versioning, errors, and idempotency. Use when endpoint behavior or compatibility is a design decision. ออกแบบ API contract. Skip simple calls to an existing API and general project planning.
metadata:
  owner: ecc
---

# Make the endpoint contract explicit

Inspect existing routes, clients, schemas, and failure handling before adding a
new shape. Use existing naming and error conventions. Define the request, success
response, relevant errors, authorization, and compatibility impact.

Choose methods/status codes by semantics. Bound list responses; use stable
ordering and a pagination strategy consistent with expected writes and callers.
Make retries/idempotency explicit for operations that can duplicate side effects.
Validate external input at the boundary and avoid leaking internal errors.

Prefer extending the existing contract over introducing a version or adapter
without a compatibility need. Use public request/response behavior for verification.
For detailed examples only, consult `references/upstream.md`; its generic
recommendations are design options, not a requirement to add rate limits,
versioning, new dependencies, or infrastructure to every endpoint.
