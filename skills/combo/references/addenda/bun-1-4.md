# Bun 1.4 changes

Use this note with [bun.md](../../specialists/bun.md) when a project targets Bun 1.4 or when a Bun
command, flag, or API below is in question. Run `bun --version` first: flag names
and defaults can change between releases, so check the installed version's help
before relying on anything here.

- **Runtime:** from Bun 1.4 the runtime is implemented in Rust (it was Zig); it still
  runs on JavaScriptCore. Node compatibility is not complete, so verify native
  addons, less-common `node:` internals, and packages that depend on Node specifics
  before using it in production.
- **Dependency commands:** `bun add`, `bun remove`, `bun update [pkg]`, `bun outdated`,
  `bun dedupe` (collapse duplicate installs), `bun prune` (remove unreferenced
  packages), `bun pm ls` (add `--all` for transitive dependencies; it lists from the
  lockfile and is not an integrity check of installed files).
- **`bun audit`:** queries registry advisories using package names and versions from
  `bun.lock` and changes nothing. That sends dependency metadata to the registry, so
  review the destination before auditing private packages. A scoped registry without an
  advisory endpoint is skipped and does not affect the exit code.
- **`bun audit fix`:** modifies the lockfile and installed packages, sometimes direct
  version pins, and may run lifecycle scripts. Treat it as a modifying install and
  review the diff.
- **Workspaces:** declare them in a root `workspaces` array in `package.json`; run one
  workspace's script with `bun run --filter <pkg-name> <script>`.
- **Built-in APIs to check before adding a dependency:** `Bun.file` / `Bun.write`,
  `bun:sqlite`, `Bun.serve`, `Bun.sql`, `Bun.redis`, `Bun.S3Client`.
- **Test runner flags (CI):** `bun test --changed[=<ref>]` runs affected tests;
  `--isolate` gives each file a fresh JavaScript global in the same process (not a
  process or security sandbox); `--parallel[=<n>]` uses worker processes and enables
  isolation by default; `--shard=<n>/<count>` partitions CI jobs; `--timings=<file>`
  reads prior durations for scheduling and `--update-timings` records them. Pick
  timing-file paths per shard deliberately and confirm them in the installed help.
- **Vercel:** set `bunVersion: "1.4.x"` in `vercel.json` to use the 1.4 runtime; keep
  `bun install --frozen-lockfile` for reproducible builds.

Source: ECC `bun-runtime` at `0797158` (upstream head on 2026-10-20), newer than the
pin mapped in [source-map.md](../source-map.md). Written by Combo from that
diff and not generated; re-derive it when the ECC pin is advanced.
