# End-to-end journeys

Use this practice for a real browser, UI, API-to-UI, or multi-service journey.
It supplements unit and integration checks; it does not replace them.

- Name the actor, starting state, user actions, and observable outcome. Use a
  stable fixture or seeded account and avoid relying on unrelated live data.
- Confirm that the served app and revision belong to the current task before
  interpreting results. A responding URL can be another process or a stale
  build. After edits, use the host's reload/rebuild path and verify a changed
  behavior or visible marker; do not terminate unrelated servers to claim a port.
- For stateful journeys, continue from a meaningful intermediate state through
  relevant filtering, editing, navigation, or reload. Check what must persist
  and what must be recalculated. Compare linked views of the same value, such
  as a changed quantity in both the summary and its detailed instructions.
  Choose transitions from the actual feature, not an exhaustive generic matrix.
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
