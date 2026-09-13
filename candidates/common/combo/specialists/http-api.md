# HTTP and API contracts

Use this note when the task changes an HTTP endpoint or its public contract.
Read the existing callers, clients, and error conventions first. The contract
is the observable behavior, so a neat route name does not justify breaking
existing consumers.

## Resource shape

- Model URLs as plural, lowercase nouns, normally kebab-case: `/api/v1/users`
  and `/api/v1/users/{id}/orders`.
- Put filtering, sorting, and paging in query parameters. Use an action verb
  only when the operation is not CRUD, for example `POST /orders/{id}/cancel`.
- Pick one response convention for the API surface. A public API can use
  `{data, meta, links}` and `{error:{code,message,details}}`; a small internal
  API can return a flat body. Do not mix shapes without a documented rule.
- Keep timestamps and identifiers consistently typed and formatted. Preserve
  existing wire names when compatibility matters.

## Method and status semantics

| Method | Meaning | Typical response |
| --- | --- | --- |
| GET | Read, safe and idempotent | 200 |
| POST | Create or trigger an action | 201 with `Location`, or 202 for accepted work |
| PUT | Full replacement, idempotent | 200 or 204 |
| PATCH | Partial update; make idempotent when retries are expected | 200 or 204 |
| DELETE | Remove, idempotent at the resource boundary | 204 |

Use status codes to carry the outcome: 400 for malformed input, 401 for
missing/invalid authentication, 403 for authenticated but forbidden access,
404 for a missing resource, 409 for a state or uniqueness conflict, 422 for
semantically invalid data when the API uses that distinction, 429 for a limit,
and 5xx for server or upstream failure. Never encode a failed operation as a
successful 200 response or expose stack traces in a 500 body.

## Collections and query bounds

- Offset paging is easy and supports jumping to a page, but large offsets get
  slow and can shift under concurrent inserts.
- Choose cursor paging when the collection is large, traversal is sequential,
  or concurrent inserts make offsets unstable. Offset paging is reasonable for
  small bounded collections or an explicit jump-to-page requirement. For a
  cursor, order by a stable, unique tuple such as `(created_at, id)`, encode the
  cursor, and use a strict predicate that matches the direction. Return the next
  cursor only when another page exists.
- Bound page size server-side. Validate filter and sort fields against an
  allowlist, and define a deterministic default order.
- Return totals only when the cost and consistency are acceptable. A count over
  a large, changing table can be more expensive than the page itself.

## Retries, idempotency, and evolution

- Identify every operation a client may retry. GET is safe and idempotent; PUT
  and DELETE mutate state but their intended effect is idempotent. POST creation
  needs an idempotency key or a documented
  duplicate policy when network retries can repeat the request.
- Store an idempotency key and request result durably with the local operation,
  but do not imply that a local database transaction can atomically commit an
  external payment, email, or other provider effect. Identify which system
  deduplicates those effects. Use provider idempotency when available; add
  durable dispatch or an outbox and reconciliation when the required crash
  recovery needs them. Document any remaining duplicate-effect window. Return
  the original result for a replay and reject a key reused with a different
  payload.
- Add a version only when the compatibility boundary requires it. Once a
  version is public, deprecate deliberately, preserve old fields long enough
  for clients to migrate, and test both wire versions during the transition.
- Set `Retry-After` for 429 and temporary 503 responses when the client can
  make a useful retry. Do not ask clients to retry validation or authorization
  failures.

## Review checklist

1. Is the route a resource or a justified action, and do existing clients still
   parse its body and statuses?
2. Are authentication, object authorization, and input validation enforced at
   the relevant boundary rather than inferred from the URL?
3. Are list limits, stable ordering, cursor/offset behavior, and invalid query
   fields specified?
4. Are errors structured without secrets, and do logs carry a correlation id
   without raw credentials or sensitive payloads?
5. Can a timeout or retry duplicate a side effect, and is that behavior tested?
6. Are generated OpenAPI/schema artifacts and client contracts updated with the
   implementation?

Source: ECC `api-design`, pinned and mapped in [source-map.md](../references/source-map.md).
