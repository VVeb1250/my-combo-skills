# Authoring and adapting a Combo-like system

This guide is for two audiences:

- **Combo users** who want to add, revise, or remove a workflow, practice,
  entry, or host adapter without breaking discovery, installation, or rollback.
- **Builders** who want the transferable pattern, not a copy of this repository's
  full library, installer, or evaluation harness.

The agent-facing decision procedure is
[`skills/combo/practices/authoring.md`](../skills/combo/practices/authoring.md).
Use the explicit `/combo-author` or `$combo-author` entry when you want an agent
to apply it. Use `combo-maintain` for installation updates, verification, and
rollback.

## The pattern in this repository

### 1. Thin entries, shared bodies

The pack ships twelve task entries plus `combo`, `combo-maintain`, and the
explicit-only `combo-author`. Each task
entry is a small frontmatter block and a pointer to a shared workflow. For
example, [`combo-deliver`](../skills/combo-deliver/SKILL.md) exists so discovery
can find the job; [`workflows/deliver.md`](../skills/combo/workflows/deliver.md)
owns the procedure and conditional reads.

Do not duplicate a workflow body into an entry or a second host package. Entry
metadata is cheap to discover; workflow content should load only after selection.

### 2. Progressive disclosure with triggers

The router ([`skills/combo/SKILL.md`](../skills/combo/SKILL.md)) chooses one
primary path. The workflow then pulls in a practice only when a concrete
uncertainty remains. Practices open with a trigger such as “Use this practice
when…”, not a topic label. A topic file without a trigger is context bloat.

### 3. One owner per fact, generated copies, regression tests

[`practices/context.md`](../skills/combo/practices/context.md) owns the core
context rules. [`scripts/sync-context-core.py`](../scripts/sync-context-core.py)
copies the first three sections into every workflow inside a marked block, and
[`tests/test_context_core.py`](../tests/test_context_core.py) checks that every
workflow carries the current block and that `--check` detects staleness.

When a rule must appear in several places, generate it and test the generator.
Do not hand-copy it and hope the copies stay aligned.

### 4. Host boundary

Portable content lives under `skills/combo/`. Codex-specific and Claude-specific
entrypoints live under `adapters/`. The host adapter owns invocation flags,
runtime path variables, model and worker configuration, settings, and install
metadata. The shared workflow body stays host-neutral.

A stale override is a real defect: the Claude router override is tested against
the source practice links so a new practice cannot silently disappear from one
host.

### 5. Manifest ownership and transactional install

[`install-manifest.json`](../install-manifest.json) declares the owned package
roots, adapter files, config markers, worker role, disable entries, and preserve
roots. [`scripts/setup.py`](../scripts/setup.py) builds a plan, applies it with a
receipt and backups, verifies the result, and rolls back on request. Rollback
stops when an owned file has drifted.

The installer may touch only what the manifest declares. Preferences, hooks,
credentials, memory, and native skills stay outside that footprint.

### 6. Opt-in project knowledge

[`practices/project-ecosystem.md`](../skills/combo/practices/project-ecosystem.md)
is used only when a project has `.combo/` or the owner requests it. Accepted
specs, proposed deltas, evidence-linked retro, tested shortcuts, and a generated
index are separate from personal memory. Routine tasks do not scaffold it.

### 7. Stopping points and evidence

Every workflow states what it is allowed to do and where it stops. Review does
not edit; verification does not repair; investigation does not create files.
Completion claims need evidence that can detect the actual mismatch. A
successful install proves the package is present, not that the system produces
better work.

## What is specific to this repository

| Choice here | Transferable principle |
| --- | --- |
| Twelve task entries plus router, maintenance, and explicit-only authoring | Add an entry only when discovery earns its cost |
| 331-entry source library and A/B harness | Keep provenance and evaluate at the scale you need |
| `.combo/` schema and `project_kb.py` | Make project knowledge opt-in, evidence-linked, and generated |
| Python stdlib installer with receipts | Use a manifest, a transaction, and drift-aware rollback |
| Four adapted source packs | Record source ownership, adaptation decisions, and archived competitors |

Do not copy the scale. Copy the decisions that keep the system coherent.

## Smallest viable system

A useful Combo-like system can start much smaller than this repository:

| Component | Minimum | Evidence |
| --- | --- | --- |
| Router | One entrypoint that selects a primary path | A few positive, negative, and confusable requests |
| Workflows | One per distinct stopping point | Each workflow has a completion condition |
| Practice | One shared rule file for repeated decisions | A test or review check that catches drift |
| Entry | One thin skill per frequently discovered job | Discovery shows the expected entry |
| Host adapter | One adapter per host | Invocation, paths, and settings are host-specific |
| Install | A manifest and reversible apply | Plan, apply, verify, rollback |
| Project knowledge | Optional, opt-in | Accepted specs and evidence-linked lessons, not a diary |

Start with one workflow and one practice. Add entries only when a real request
fails to discover the existing path.

## Customization ladder

1. Clarify the existing workflow or practice.
2. Add a practice for a recurring decision.
3. Add a specialist or reference note for an unresolved mechanism.
4. Add a direct entry when discovery is the bottleneck.
5. Add a host adapter when the behavior is genuinely host-specific.

A new workflow is not the default answer. A technique usually belongs in a
practice or specialist note, not a new task path.

## Host adapter boundary

For Codex, the adapter supplies `agents/openai.yaml` per entry and the worker
configuration. For Claude Code, the adapter supplies frontmatter such as
`disable-model-invocation` and `user-invocable`, `${CLAUDE_SKILL_DIR}` runtime
paths, a native subagent with `model: inherit`, and host settings.

An explicit-only system entry needs both:

- Codex: `allow_implicit_invocation: false` in `agents/openai.yaml`.
- Claude: `disable-model-invocation: true` and `user-invocable: true`.

Keep the shared body free of host invocation markers. If an override copies a
shared index, test that the links still match the source.

## Installation and ownership

Work in a source checkout. Installed-package edits are not durable across
updates. A complete change includes:

1. The shared workflow or practice.
2. The thin entry and its host override.
3. The manifest entry for the new package or adapter file.
4. A plan that touches only declared ownership.
5. Apply with a receipt and backups.
6. Verify discovery and a representative task.
7. A rollback rehearsal on copies.

Do not rewrite unrelated config, hooks, memory, credentials, or native skills.

## Evaluation

Separate three questions:

- **Discovery:** does the right entry get selected for a natural request?
- **Structure:** do links resolve, files install, and ownership stay bounded?
- **Outcome:** does the work actually improve on a representative task?

A routing label is not an outcome. A successful install is not an outcome. A
repaired artifact is not proof that future sessions improve. Label behavioral
claims unverified until a fresh comparable task tests them.

## What not to copy

Treat upstream personas, thresholds, example companies, trackers, memory
systems, hooks, and installers as reference data. Do not enable a source system
because it is present in a library. Do not add a workflow engine, daemon,
global hook, or scoring service unless the user asks for that system and the
need is demonstrated.

## Templates and related files

- [Workflow template](../skills/combo/templates/workflow.md)
- [Practice template](../skills/combo/templates/practice.md)
- [Entry template](../skills/combo/templates/entry.md)
- [Host adapter checklist](../skills/combo/templates/host-adapter.md)
- [Authoring practice](../skills/combo/practices/authoring.md)
- [Maintenance entry](../skills/combo-maintain/SKILL.md)
- [Architecture decisions](../DESIGN.md)
- [A/B decision](../audit/ab/DECISION.md)
