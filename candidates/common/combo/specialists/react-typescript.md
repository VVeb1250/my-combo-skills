# React and TypeScript UI

Use this note for React components, hooks, TSX state, Server Components, forms,
or client data fetching. Match the project's React/Next version and existing
state library before introducing a new abstraction.

## Render and state

- Treat render as a pure function of props and state. Derive values during
  render instead of storing them in state and synchronizing them in an effect.
  This avoids an extra render and stale derived values.
- Put state at the narrowest owner that needs it: local `useState`, then lift to
  a common parent. Use Context for low-frequency cross-tree values such as
  locale or auth. Use an external store when cross-tree coordination, existing
  project conventions, or high-frequency updates make lifting and Context a
  poor fit.
- Server-derived data is server state. Prefer the project's cache/fetch layer
  (RSC fetch, TanStack Query, or SWR) over a hand-built `useEffect` fetch with no
  cache, cancellation, retry, or stale-response policy.
- Model UI states as a discriminated union when loading, success, empty, and
  failure have different legal data. Let TypeScript make impossible branches
  visible rather than using nullable bags with undocumented combinations.

## Hooks and effects

- Call hooks at the top level, in the same order on every render.
- Use a functional updater when next state depends on previous state.
- Effects are for synchronization with an external system: subscriptions,
  timers, DOM APIs, and network coordination. Keep event-specific mutations in
  event handlers or form actions.
- Return cleanup for listeners, intervals, subscriptions, and abortable work.
  Do not add `useMemo` or `useCallback` by reflex. A profiler result or a real
  dependency identity problem should justify memoization.
- Extract a custom hook when the same state/effect sequence is reused, while
  keeping component-specific logic local.

## Server/client boundaries

In an RSC-capable app, server components are the default and may await data;
client components opt in with `"use client"` for interactivity. Pass only
serializable props across the boundary. Compose a server component through a
client component's `children`; do not import a server component from a client
module. Invoke server actions through the framework's supported form/action
boundary and validate their input on the server.

Place Suspense boundaries near the data that can reveal progressively. An error
boundary catches render/lifecycle/constructor failures in its children, but it
does not catch an event handler or arbitrary async rejection, so handle those
paths explicitly.

## Forms and accessibility

- In a framework that supports React 19 server actions, use its supported form
  action and `useActionState` pattern for server mutations, returning a typed
  field/form error state and disabling submission while pending. In a client
  app backed by REST or GraphQL, keep mutations in that existing API/data layer
  and use the corresponding pending/error state instead.
- Use controlled inputs when the value drives other UI, formatting, or live
  validation. For dynamic arrays, cross-field rules, or multi-step forms, use
  the established form library instead of growing ad hoc state machinery.
- Associate labels and errors with fields, expose async errors with an
  appropriate live region, preserve keyboard operation, and keep focus after
  validation or route changes.

## Practical review

Check the component's state owner, effect dependencies and cleanup, server/client
imports, loading/error/empty states, abort or stale-response behavior, and the
actual keyboard/screen-reader semantics. Run the project's TypeScript and UI
tests when the change crosses a public component or hook seam.

Source: ECC `react-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
