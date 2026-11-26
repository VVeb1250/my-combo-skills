# Contract migration

When independently deployed consumers or persisted data must survive a change, inspect the authoritative schema/interface, actual callers, deployment order, data size, lock behavior and rollback compatibility. Avoid a second contract artifact if a shared type already suffices. Do not edit migrations already applied to shared environments.

For mixed-version compatibility, consider expand -> migrate/backfill -> switch readers/writers -> contract. Confirm each phase tolerates old/new combinations before removal. For data backfill, prove bounded work, restart/idempotence and completeness; check partial failures and concurrent writes. Measure lock duration, transaction size and representative runtime on authorized isolated data, not a tiny empty schema. Verify the installed engine's DDL and transaction semantics rather than assuming online operations are lock-free.

Recovery may require a forward migration or retained data, not merely reverting code. Preserve valid compatibility until actual consumers are migrated. No production rollout or irreversible data changes without applicable authorization. Record accepted constraints and transition in the existing wiki owner.
