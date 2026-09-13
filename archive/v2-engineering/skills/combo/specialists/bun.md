# Bun runtime

Use this note when adopting Bun, migrating a Node script, or debugging Bun
installation, runtime, bundling, or tests. Confirm the project's dependencies
and deployment target before changing the runtime.

- Prefer Bun for a new JS/TS toolchain when its runtime and ecosystem support
  the actual dependencies. Keep Node when a package, native addon, or build
  plugin assumes Node behavior or compatibility is more valuable than speed.
- `bun install` writes the current text `bun.lock` by default; older projects
  may have `bun.lockb`. Commit the lockfile and use `bun install --frozen-lockfile`
  in reproducible deployment paths.
- Use `bun run <script>` for package scripts, `bun <file>` or `bun run <file>`
  for TS/JS files, and `bun x` for npx-like one-off commands. Check scripts that
  depend on shell-specific behavior or Node global assumptions.
- The built-in test runner uses `bun:test`; keep test discovery and assertions
  consistent with the repository's existing runner before migrating suites.
- Bun APIs such as `Bun.file` and `Bun.serve` can reduce dependencies, but do
  not rewrite a stable adapter solely for a benchmark claim.
- For a hosted runtime, configure Bun explicitly and verify install, build,
  start, environment, and native dependency behavior in that platform's current
  documentation.

Migration review: compare lockfile changes, native modules, test behavior,
`process`/Web API assumptions, signal handling, and production startup before
declaring Node replacement complete.

Source: ECC `bun-runtime`, pinned and mapped in [source-map.md](../references/source-map.md).
