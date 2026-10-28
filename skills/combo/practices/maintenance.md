# Combo maintenance

Maintain existing Combo behavior and installation from observed failures, positive evidence, routing drift, and user feedback. This is not an installation-only skill.

- `combo-maintain` owns diagnosis, targeted repair of existing rules, regression evidence, install/verify/rollback, and host parity. It must not add new skill entries or redesign ownership implicitly.
- `combo-author` owns explicitly requested new workflows, practices, entries, templates, host adapters, major restructuring, and reusable Combo-like pack design. Explicit-only invocation must remain enforced on each host.
- On an observed instruction failure, maintain may update the canonical existing rule, referencing authoring guidance where relevant, without creating a duplicate owner or invoking author automatically. For structural redesign, propose the change and use explicit authoring authorization.

Diagnosis: record user intent, expected/observed behavior, trace or repro, competing explanations, and the instruction at issue. Separate code defects, environment/tool faults, and real Combo gaps. Preserve supported positive retros as candidates, never as guaranteed gains. Use existing fixtures and the least costly discriminating verification; do not require new model benchmarks per edit. Distinguish structurally verified, behavior observed, and behavior unverified.

Correction ownership: a repeated *project* defect should normally be prevented in
that project's architecture, contract, static check, or regression test; record a
project retro only when a lesson is reusable. Change Combo instructions only when
an observed failure shows its workflow or decision guidance contributed to the
mistake. When that is proven, change the existing canonical instruction, replay
the failing task, and check an unaffected small-task case for added overhead.
Do not promote a historical retro directly into a global rule.

Rule ownership: `context.md` owns intent and stopping point; the selected workflow owns task actions; `tests.md` owns test seams; `outcome-evidence.md` owns user-visible fidelity; `verification-economy.md` owns escalation to expensive checks; `simplicity.md` owns structural refactoring; `project-ecosystem.md` owns optional project records.

For installing or updating: inspect the verified source checkout, read the invoking host's manifest, plan before apply, verify discovery, save receipts/backups and stop rollback on drift. An inspection-only task may conclude without an install plan. Never alter unrelated preferences, models, hooks, permissions, credentials, native skills or memory.