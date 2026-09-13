# End-to-end journeys

Use this practice for a real browser, UI, API-to-UI, or multi-service journey.
It supplements unit and integration checks; it does not replace them.

- Name the actor, starting state, user actions, and observable outcome. Use a
  stable fixture or seeded account and avoid relying on unrelated live data.
- Use the host's native browser skill and actual session capabilities for UI
  interaction. Do not invent a browser adapter or claim a screenshot proves a
  backend invariant it cannot observe.
- Capture the smallest useful evidence: final UI state, screenshot when layout
  matters, console/network error when relevant, and the command or session
  context. Redact tokens, personal data, and authorization headers.
- Separate product failures from unavailable servers, stale fixtures, browser
  permissions, timing, and environment setup. Retry only to distinguish a
  transient condition, not to hide a failure.
- Keep destructive or external actions within the user's requested and
  authorized scope. Prefer disposable data and clean up data created by the
  journey when safe.

Report the exact path, observed verdict, artifacts, and any untested branches.
For a failing journey, preserve the symptom and route causal repair to debug.
