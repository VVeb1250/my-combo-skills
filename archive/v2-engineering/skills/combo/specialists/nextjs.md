# Next.js and Turbopack

Use this note for Next.js App Router, Turbopack development behavior, or a
version-specific routing/build issue. Check `package.json` before applying the
Next 16 guidance below.

- In current Next 16 projects, `next dev` uses Turbopack by default and reuses
  filesystem cache under `.next`. Use the project's documented webpack escape
  hatch only for a verified plugin or bundler incompatibility.
- Keep server components as the default where the App Router supports them.
  Move only interactive/browser-dependent code behind a client boundary and
  pass serializable props across it.
- `proxy.ts` is the Next 16 middleware filename. Older projects use
  `middleware.ts`; the choice follows the Next version, not Turbopack versus
  webpack. Verify the version before renaming a file.
- For bundle size or slow builds, inspect actual analyzer output and dependency
  boundaries. Do not clear the cache or switch bundlers as a first guess.
- Confirm whether the deployed `next build` uses the same bundler behavior as
  local development for the project's release before drawing performance claims.

Source: ECC `nextjs-turbopack`, pinned and mapped in [source-map.md](../references/source-map.md).
