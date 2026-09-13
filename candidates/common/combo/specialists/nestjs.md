# NestJS

Use this note for NestJS TypeScript backends, modules, DTOs, guards,
interceptors, config, or exception filters.

- Keep domain behavior inside feature modules. Controllers parse transport input
  and call providers; services own business rules; export only providers another
  module genuinely consumes.
- Configure one global `ValidationPipe` for public APIs with `whitelist` and
  `forbidNonWhitelisted`, plus `transform` only when implicit conversion is
  intended and documented. Keep DTO validation near its module.
- Use guards for authentication/authorization, interceptors for cross-cutting
  response or timing behavior, and exception filters for a stable error shape.
  Object authorization still belongs at the operation that knows the resource.
- Validate environment configuration at startup and inject it; do not scatter
  unvalidated `process.env` reads through providers.
- Keep persistence transactions in a service/repository boundary and propagate
  cancellation/timeouts through external calls where the adapter supports them.

Review module import/export cycles, DTO transformation, guard ordering, error
serialization, configuration validation, and controller thickness.

Source: ECC `nestjs-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
