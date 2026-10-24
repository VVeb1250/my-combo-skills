# Authoring and adapting a Combo-like system

Use this practice only when the user explicitly asks to customize this Combo
pack, add or revise a workflow, practice, entry, template, or adapter, or build
a Combo-like system from scratch. It is not a task workflow; use the task
entries for ordinary work. For installation, update, verification, or rollback
of an existing install, use `combo-maintain`.

## Start from observed work

Begin with a representative request the current system handled poorly: the
prompt, the chosen route, the observed result, and the instruction that would
have changed the decision. A taxonomy of topics is not evidence. If the user
has no concrete case, pick one bounded real deliverable and run it through the
current system first.

Separate an implementation mistake, an environment failure, and an instruction
gap. A bad answer alone does not prove the skill caused it.

## Choose the smallest change

Use this ladder; stop at the first rung that fixes the observed problem:

1. Clarify an existing workflow or practice.
2. Add a practice that owns a recurring decision.
3. Add a specialist or reference note for an unresolved mechanism.
4. Add a direct entry only when implicit discovery is the bottleneck.
5. Add a host adapter when the behavior is genuinely host-specific.

A new workflow is not the default answer. A technique usually belongs in a
practice or specialist note, not a new task path. Add an entry only when a
user would otherwise fail to discover the right workflow.

## Define the contract

Every new or changed file needs:

- a trigger: the situation that makes it relevant;
- the decision it changes;
- a stopping point and the evidence that closes it;
- the smallest supporting read, not a catalog.

For an entry, the description must discriminate the job from neighboring
entries. For an explicit-only system entry, also declare the invocation policy
in the host adapter. Keep the entry body thin: point to the shared workflow or
practice instead of copying its content.

## Keep one owner per fact

Put the editable rule in one file. If it must appear in several places, generate
the copies and test the generator. This pack's example is
`scripts/sync-context-core.py`: `practices/context.md` owns the core, and the
script writes a marked block into every workflow; `tests/test_context_core.py`
guards it. Do not hand-copy a rule into many workflows.

When a source index and a host override both exist, test that the override still
carries the source links. A stale copy silently hides a new practice.

## Respect the host boundary

Keep workflow, practice, and reference bodies host-neutral. Put host-specific
entrypoints, invocation flags, runtime path variables, model and worker
settings, and installer details in an adapter. Do not fork a workflow body per
host. When an override copies a shared index, test that the links still match
the source.

## Declare ownership and install transactionally

Work in a source checkout when possible; installed-package edits are not
durable across updates. In this pack, `install-manifest.json` declares the owned
package roots and adapter files. A change is complete only when:

- the manifest includes the new package or file;
- the installer plan is reviewable;
- apply produces a receipt and backups;
- verify checks discovery and behavior;
- rollback still works and stops on drift.

Preserve unrelated host state: preferences, hooks, credentials, memory, and
native skills are not yours to rewrite.

## Verify structurally and behaviorally

Structural checks (links resolve, files install, discovery shows the entry) are
necessary but not sufficient. Exercise a representative task and compare the
result with the previous behavior. Label behavioral improvement unverified until
a fresh comparable task tests it. A routing label or a successful install is not
quality evidence.

## Do not copy

Treat upstream personas, thresholds, example companies, trackers, memory
systems, hooks, and installers as reference data, not defaults. Do not enable a
source system merely because it is in the library. Do not add a workflow engine,
daemon, global hook, or scoring service unless the user asks for that system and
the need is demonstrated.

## Templates

- [workflow](../templates/workflow.md)
- [practice](../templates/practice.md)
- [entry](../templates/entry.md)
- [host adapter](../templates/host-adapter.md)

For the human-facing rationale and a smallest-viable-system walkthrough, see
`docs/authoring.md` in the source repository.
