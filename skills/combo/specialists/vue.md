# Vue

Use this note for Vue components, composables, Pinia state, or SSR/hydration
issues. Follow the project's Vue/Nuxt version and existing build conventions.

- Organize larger apps by feature. Keep Single-File Components in the
  project's consistent order, expose a small props/emits contract, and avoid
  mutating props. Use emits for child-to-parent events.
- Put reusable stateful behavior in composables with explicit inputs and
  cleanup. Keep server/cache state separate from local UI state; use Pinia only
  when cross-route or cross-component ownership justifies it.
- Keep the first SSR render deterministic. Browser-only APIs, random/time-based
  values, and storage reads belong behind the client lifecycle boundary. Avoid
  fixing a hydration mismatch by disabling SSR without identifying the cause.
- Make watchers narrow and cleanup-aware. Use computed values for derivation and
  watchers for synchronization with external systems.
- For Nuxt, prefer `useFetch`/`useAsyncData` for SSR-safe reads, stable keys for
  composed async data, and `$fetch` for user-triggered writes. Choose route
  caching or prerender rules per route group.

Source: ECC `vue-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
