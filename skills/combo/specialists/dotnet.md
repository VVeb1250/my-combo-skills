# .NET and C#

Use this note for C#/.NET services, ASP.NET Core DI, configuration, async code,
or EF Core boundaries. Match the target framework's nullable and language
settings before introducing syntax from a newer runtime.

- Prefer records, `init` properties, and immutable value objects for DTOs and
  commands. Make mutable collections and public setters deliberate.
- Keep nullability explicit. Use constructor injection for required dependencies
  and register a narrow interface at the composition root.
- Make async methods async all the way. Accept and pass a `CancellationToken`
  through repository, HTTP, and database calls. Never block with `.Result` or
  `.Wait()` on an async operation.
- Run independent I/O concurrently with tasks and `Task.WhenAll`, but preserve
  bounded concurrency and cancellation. Do not parallelize dependent work.
- Bind configuration with strongly typed options, validate required values at
  startup, and avoid reading environment variables deep in domain services.
- Use exceptions for unexpected failures and an explicit result/value object for
  expected domain outcomes. Map both to a stable HTTP error shape at the edge.
- Keep EF Core transaction scope around the invariant, pass cancellation, and
  avoid a repository abstraction that hides query shape or tracking behavior
  when the project does not need it.

Review nullable contracts, disposal/async disposal, cancellation propagation,
DI lifetime mismatches, options validation, and whether a result error can leak
sensitive internal details.

Source: ECC `dotnet-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
