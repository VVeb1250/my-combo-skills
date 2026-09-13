---
name: ecc-e2e
description: Verify a real user journey across UI and backend or diagnose a failing end-to-end test. Use for requested E2E coverage, browser regressions, checkout/login journeys, or cross-component integration risks. ทดสอบ flow จริงและ E2E. Skip isolated logic and cosmetic edits unless browser evidence is needed.
metadata:
  owner: ecc
---

# Verify a meaningful user journey

Identify the observable user outcome, existing runner, test environment, and
required data. Reuse project fixtures and configuration. For browser interaction,
follow the host's browser skill and its supported tools before selecting a runner.

Exercise the actual critical journey with user-facing locators, deterministic
test data, and state/response-based waits. Assert the user-visible outcome and
relevant persistence; a click without an outcome assertion proves little.

Avoid fixed sleeps, brittle generated CSS selectors, test order dependence, and
mocking away the integration this test is meant to verify. Mock only irrelevant
external services. Keep browser/project selection explicit.

On failure, inspect traces, screenshots, console/network errors, and the earliest
divergence. Rerun a relevant failing case after a causal change; retries alone
are not a fix. Quarantine only with an explained temporary reason and repair path.

Use disposable local/test data. Do not create real purchases, send messages,
or alter production accounts without authorization for those actions.
Report the journey exercised, outcome, environment, and unverified boundaries.
