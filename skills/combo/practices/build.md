# Build and dependency checks

Use this practice for compiler, typecheck, dependency-resolution, packaging, or
CI failures. The first useful result is a causal error, not a long transcript.

1. Read the repository's package and build scripts, then reproduce with the
   narrowest existing command. Capture the revision, environment, and first
   actionable error.
2. Group errors by dependency. Repair the earliest failure that can explain the
   downstream cascade before touching unrelated messages.
3. Check imports, versions, generated artifacts, configuration, platform
   assumptions, and clean-install behavior only when the error points there.
   Preserve lockfiles and existing dependency policy.
4. Re-run the focused command after each causal change. Broaden to typecheck,
   lint, package, integration, or full CI checks according to the blast radius.
5. Classify failures as product, test, tooling, or environment. Report checks
   that were not run and the exact evidence behind the classification.

Avoid speculative dependency upgrades, broad formatting, and fixing every
secondary error before the root is understood. Route an unresolved causal bug
to debug when build mechanics alone no longer explain it.
