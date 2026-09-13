# FastAPI

Use this note for FastAPI routes, Pydantic v2 schemas, dependencies, lifespan,
async sessions, or endpoint tests. Inspect the project's Python and FastAPI
versions and keep schema, service, and persistence boundaries visible.

## Application shape

- Use an app factory with a lifespan context for startup and shutdown resources.
  Production schema changes belong to Alembic or the repository's migration
  tool, rather than `create_all` on every process start.
- Keep routers thin, Pydantic request/response schemas explicit, and business
  transactions in services. Use `from_attributes` or the version-supported
  mapping setting for ORM response models.
- Load settings with `pydantic-settings`, validate secrets and allowed origins,
  and avoid mutable global client/session state that outlives the app lifecycle.

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)

class UserResponse(BaseModel):
    id: int
    model_config = {"from_attributes": True}
```

## Dependencies and async I/O

- Yield database sessions from a dependency and close them on exit. Pass the
  session explicitly to the service that owns the transaction.
- Keep async handlers free of blocking database, filesystem, or HTTP calls.
  Propagate cancellation and use client timeouts. A sync handler is acceptable
  when all of its work is intentionally synchronous.
- Use `Depends` for authentication, authorization, and request-scoped resources,
  but enforce object authorization after loading the actual resource.
- Test the ASGI app at the HTTP seam with the repository's supported async
  client, overriding dependencies for a controlled database or fake service.

Check OpenAPI schema compatibility, validation errors, CORS/credential scope,
transaction rollback, lifespan cleanup, and response serialization before
calling an endpoint complete.

Source: ECC `fastapi-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
