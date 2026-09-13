# Context and output distillation, 2026-09-14 JST

Installed the revised Combo pack in Codex and Claude Code. The change improves
decision rules and reduces repeated instructions; it does not establish a
measured output-token saving or equivalence to Astra.

## What changed

- All twelve workflows load one shared context practice once. It defines the
  unresolved question, direct evidence, bounded search, dependency expansion,
  counterevidence, provenance, stale-state checks, and stopping conditions.
- Direct entries no longer require a router reread or a specialist lookup merely
  because the project uses a listed language. Domain methods load for a concrete
  unresolved need; the full source library and provenance remain intact.
- Each workflow has actionable acceptance and completion criteria. Valid checks
  can be reused; explicit full-suite, systematic research, and user-requested
  artifact depth remain binding. Routine completion favors one short paragraph
  with the result and decisive evidence.
- Both host routers and worker instructions carry the same scope/evidence intent.
  No new skill entry, dependency, model setting, service, or memory system was added.

Router + context + twelve workflow bodies changed from 4,840 to 3,654
whitespace-separated words, approximately 24.5% less aggregate text. This is
not a token metric. Some direct first-load paths grow because context is now
explicitly loaded; the intended runtime saving is fewer unnecessary reads,
repeated checks, and process narration. See `instruction-size.json`.

## Verification and limits

- Repository tests: 45 passed before and after the changes.
- Package validator: 14 packages, 649 files, no errors. Pinned source and full
  library checks passed; 330 upstream entries remain present.
- Native skill-creator Python validator was attempted but could not run because
  PyYAML is absent in both available Python runtimes. No dependency was installed;
  the repository's Node validator checked package frontmatter and links instead.
- New probe runner: Ruff lint/format and Pyright passed.
- Both installers verify bytes match source. Codex app-server discovery retains
  all 14 active Combo entries and unrelated skill metadata. No fresh Claude model
  session was run; Claude checks cover rendering, installed bytes, and rollback.
- Actual two-transaction rollback chains passed on temporary copies: 31 Codex
  paths and 19 Claude paths returned to pre-change hashes.

Two fresh Luna Max probes exercised the shared context practice. Diagnosis
completed correctly, used the live caller contract, and changed no fixture
files. Repair changed only the authorized source/test files, failed independent
acceptance before and passed all four acceptance tests afterward. Its own
five tests, lint, and scoped type check passed. However, the account usage limit
ended the repair session before its final answer. It remains an incomplete
session, not a full task pass. See `behavioral-review.json`.

The initial sandbox attempt could not enter its temporary Windows workspace.
Its timeout is retained separately. The recovered probes use the existing A/B
approach: a dedicated D-drive fixture with process-only full access and trust,
plus before/after scope checks. These probes are not filesystem-isolated.
Raw logs are retained locally under `live-probes/` and `live-probes-recovered/`,
excluded from new Git commits. The compact review is versioned.

The successful diagnosis also read a small unrelated gallery note. This is
evidence of correct bounded behavior, not optimal context filtering. There is
no matched old/new output comparison, broad domain coverage, or all-model claim.

## Preservation

The reviewed install plans and receipts touch only Combo package files, ownership
indexes, and worker adapters. Global instructions, hooks, Claude settings, and
the canonical memory-rules file retain their pre-install hashes.

The Codex config hash changed during the evaluation interval. Neither install
plan nor applied receipt includes config.toml, and no pre-change content copy
was captured to identify the difference. Its cause is unverified; it was not
overwritten. This report therefore does not claim byte-identical global config.
See `protected-verification.json` and the receipt pointers.

## Git backup and recovery

Created a project-local repository on `codex/context-distillation`, without
changing the parent repository or adding a remote. Backup commit: `624f16d`.
Tag: `backup/pre-context-distillation-20260914`. The pre-edit source tree is also
tagged as `backup/pre-context-source-tree-20260914`.

The initial normal commit encountered credential-shaped historical log content
in the global pre-commit scan and was interrupted. The existing snapshot was
archived locally with Git plumbing; the hook configuration was preserved.
The new change commit uses the normal hook on its incremental diff. No push was
performed. Ignored upstream checkouts/backups are not part of the Git snapshot;
the shipped library, source pins, and separate installer backups are preserved.

To undo installed changes using receipts, roll back the refinement transaction
before the initial transaction, with the matching host's setup script:

| Host | First rollback | Second rollback |
| --- | --- | --- |
| Codex | `backups/20260913-175922-355400/receipt.json` | `backups/20260913-175241-839300/receipt.json` |
| Claude | `backups/claude-20260913-175926-582400/receipt.json` | `backups/claude-20260913-175245-247400/receipt.json` |

The source backup tag allows a separate Git restore of selected package files.
Preserve later user edits and inspect the plan before applying a restored source.
