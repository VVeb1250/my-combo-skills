---
name: ecc-react
description: Implement React components, hooks, state, effects, forms, and server/client boundaries. Use when those React behaviors affect a requested UI change. เขียน React และแก้ state/effect. Skip unrelated backend code and simple CSS/text edits.
metadata:
  owner: ecc
---

# Keep React state and effects explainable

Match the installed React/framework version and established component patterns.
Keep state close to its owner; derive values during rendering when possible.
Use effects for synchronization with external systems, with cleanup and correct
dependencies. Check stale closures, request races, and unmount behavior.

Respect server/client boundaries and keep secrets off the client. Reuse semantic
HTML and existing accessible controls before introducing wrappers or dependencies.
Handle loading, empty, error, and success states that the actual interaction needs.
Use stable keys and measure before adding memoization or state-management layers.

Verify observable interaction with the existing test/browser tools. For detailed
patterns, read the relevant part of `references/upstream.md`. Do not turn its
options into a mandatory component architecture or rewrite the application's style.
