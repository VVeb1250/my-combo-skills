# State and lifetime

For conflicting state, races, leaks or invalid transitions, identify the authoritative writer, resource owner, lifetime and readers. Trace acquisition -> use -> release across success, error, cancellation and restart. Look for duplicate ownership, derived state synchronized by side effects, check-then-act gaps and callbacks that outlive their owner.

Write the invariant as an observable outcome. Construct an adversarial ordering (duplicate request, cancellation between acquisition and registration, stale response arriving last, concurrent writer) that would violate it. Pin scheduling or use barriers when possible; verify the resource/state after the operation, not only its return value. For transactions identify the actual isolation/locking semantics, retries and external side effects. Never retry a non-idempotent effect blindly.

Prefer one responsible boundary and native lifecycle/transaction primitives. Choose a fix based on the failed invariant, not a blanket lock or new wrapper. Check version-specific APIs in the installed runtime. Preserve valid caller ordering and error contracts.
