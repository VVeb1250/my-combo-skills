# Angular

Use this note for Angular components, Signals, forms, dependency injection,
routing, SSR, or Angular-specific tests. Read the project's Angular and CLI
versions first because Signals, Signal Forms, and router APIs are versioned.

## Component and reactivity choices

- Use the Angular CLI conventions and standalone/component structure already
  present in the repository. Keep templates declarative and component state
  close to the feature.
- Prefer `signal` for writable state and `computed` for derived state. Use
  `linkedSignal` when writable state follows a source signal, and `resource`
  for the version-supported async signal API. Use `effect` only to synchronize
  with an external system, logging, or DOM integration, never to compute state
  that belongs in `computed`.
- Keep `inject()` inside an injection context. When a framework adapter needs
  injection elsewhere, use the supported `runInInjectionContext` boundary and
  make the lifetime explicit.
- Use the existing form strategy for existing screens. For new forms, prefer
  Signal Forms only when the target version supports them; reactive forms suit
  complex validation and template-driven forms suit genuinely simple forms.

## Routes, SSR, and accessibility

- Lazy-load meaningful feature boundaries. Choose guards for access decisions,
  resolvers only when data must exist before activation, and a rendering mode
  (CSR, prerender, SSR) based on SEO, latency, and hydration requirements.
- Keep the server and browser's first render deterministic. Browser-only APIs
  belong behind the supported client lifecycle boundary.
- Prefer Angular Aria/headless patterns for composite widgets. Preserve roles,
  keyboard behavior, focus, and state attributes together; do not use ARIA to
  hide a broken interaction model.

Deep, versioned sidecars are available when needed: [components](../references/angular/components.md),
[signals](../references/angular/signals-overview.md), [forms](../references/angular/reactive-forms.md),
[DI](../references/angular/di-fundamentals.md), [routing](../references/angular/define-routes.md),
and [ARIA](../references/angular/angular-aria.md).

Source: ECC `angular-developer`, pinned and mapped in [source-map.md](../references/source-map.md).
