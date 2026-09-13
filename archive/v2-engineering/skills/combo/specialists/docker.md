# Docker and Compose

Use this note for Dockerfiles, Compose services, local stacks, or container
hardening. Treat the image, build context, runtime user, network, and persistent
volume as part of the deployment contract.

## Image construction

- Use multi-stage builds. Copy lockfiles before source to preserve dependency
  caching, run the build in a dedicated stage, and copy only runtime artifacts
  into a minimal production stage.
- Pin a deliberate base image and dependency lockfile. Avoid `:latest` for a
  deployed image. Keep the build context small with `.dockerignore`.
- Run the production process as a non-root user, drop unnecessary capabilities,
  and make the root filesystem read-only when the application permits it. Give
  writable paths explicit volumes or mounts.
- Put a service-appropriate health check in the image or deployment. An HTTP
  readiness endpoint is useful for a web service, while a worker or CLI may need
  a queue/heartbeat or completion check instead. Keep readiness (eligible for
  traffic) separate from liveness (stuck and should restart), and make shutdown
  behavior compatible with the process signal and grace period.

## Compose environments

- Keep a development Compose target with source mounts and hot reload separate
  from a production target. Do not leak debug ports, credentials, or bind mounts
  into the production configuration.
- Gate app startup on database health where ordering matters, but still make
  the app retry or fail clearly because `depends_on` is not a distributed
  readiness guarantee.
- Name networks and volumes deliberately. Treat database volumes as data that
  needs backup and migration handling, not disposable container state.

Review the final image contents and user, secrets injection, exposed ports,
health/readiness semantics, volume backup path, and whether a rebuild is
reproducible on the target CI/host.

Source: ECC `docker-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
