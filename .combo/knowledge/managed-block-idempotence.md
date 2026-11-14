+++
id = "knowledge.managed-block-idempotence"
domains = ["host-integration"]
summary = "Managed policy replacement must not add separators when its surrounding prefix is empty."
status = "tested"
kinds = ["lesson", "technique"]
topics = ["idempotence", "migration", "rollback"]
evidence = ["tests/test_setup.py"]
+++
# Managed block idempotence

**Observation:** The Codex legacy-worker migration/rollback regression failed because a policy file beginning with the owned marker acquired leading blank lines on the next render. The plan was nonempty even after an exact rollback.

**Mechanism:** Insert the separator before a managed block only when the retained prefix is nonempty. Apply the same rule for initial insertion and replacement. Check first render, repeated render and migration rollback against the actual fake-home files, including unrelated user agents.

**Evidence:** [Installer regression](../../tests/test_setup.py), `test_subcombo_migration_and_rollback_preserve_other_agents`; [implementation](../../scripts/setup.py), `render_agents`. The [CI run](https://github.com/VVeb1250/my-combo-skills/actions/runs/43654075702) passed this regression after the fix.

**Limits:** Applies to the owned Markdown policy block and its tested installer lifecycle; do not infer correctness for other configuration formats or host runtimes without their own checks.
