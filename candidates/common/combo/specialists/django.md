# Django and Django REST Framework

Use this note for Django projects, DRF APIs, ORM queries, caching, signals, or
middleware. Inspect the installed Django/DRF versions and settings layout before
applying a pattern.

## Project and settings boundaries

- Keep feature behavior inside Django apps, with models, serializers, views,
  URLs, permissions, filters, services, and tests near the owning domain.
- Split base, development, production, and test settings. Load secrets from
  the environment, keep production `DEBUG` false, define allowed hosts and
  secure cookies deliberately, and make database selection explicit.
- Keep request/response protocol logic in views or viewsets, validation and wire
  shape in serializers, and multi-model business transactions in a service
  boundary. Permissions must enforce object access, not only authentication.

## ORM and side effects

- Use `select_related` for single-valued joins and `prefetch_related` for
  collections when the access pattern is known. Inspect query counts before
  fixing a suspected N+1; do not prefetch every relation by default.
- Use `transaction.atomic()` around a business invariant and put uniqueness or
  state constraints in the database as well as in form/API validation.
- Design cache keys with a namespace, identity, and version. Invalidate or
  expire on the write path, and decide whether stale reads are acceptable.
- Signals are for decoupled integration where ordering and failure semantics are
  understood. Keep core domain transitions explicit when a caller must know what
  happened or handle failure.

Review the migration, serializer validation, queryset count, permission path,
CSRF/session posture, cache invalidation, and async boundary together.

Source: ECC `django-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
