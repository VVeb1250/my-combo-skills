# Git checkpoints and safe recovery

Use this practice for a Git-backed coding task when the change is risky, spans
meaningful slices, involves structural moves, or needs a recoverable experiment.
Tiny, well-understood edits do not need a commit ceremony. Git read operations
are useful even when writes are not authorized.

## Establish the actual baseline

- Before consequential edits, inspect `git status --short`, the current branch,
  `git rev-parse HEAD`, staged changes, and relevant untracked files. Record the
  baseline revision and which paths were dirty *before* the agent touched them.
- Review both staged and unstaged diff; `git diff` alone omits staged edits.
  A baseline commit is not required just to compute a diff.
- Do not mistake a dirty working tree, another agent's changes, or untracked
  files for agent-owned work. Never silently stash, stage, commit, or discard them.
- When isolation is needed, prefer an explicitly authorized task branch or
  separate worktree. A worktree created at HEAD does not move pre-existing dirty
  edits from the original worktree. Do not switch branches over unresolved edits.
- Local commits need authorization from the current request or an explicit
  repository-level instruction. Reading Git status/history needs no such grant.
  Publishing/pushing, opening a PR, merging, or rewriting shared history each
  need their own authorization; local checkpoint permission alone does not grant it.

## Draft checkpoints

- Git has no draft-commit object. An unpublished task-owned commit such as
  `wip(combat): isolate reload state` is a *checkpoint*, not a verified outcome.
  A failing experiment may be captured as WIP if its incomplete status is clear.
- Create one after a meaningful recoverable slice or before a risky next step,
  **not** after every tool call, file edit, or debugging guess. For a fresh clean
  branch, its initial HEAD is already a baseline; do not make an empty commit.
- Stage explicit task-owned paths/hunks; inspect `git diff --cached --stat`
  and `git diff --cached` before committing. Avoid blanket `git add -A`.
  Do not stage secrets, generated junk, or unrelated changes.
- Keep mechanical file moves separate from behavior changes when that makes
  diffs, regressions, and recovery easier. Reuse the same task branch rather than
  creating a branch or checkpoint for every small edit.

## Validate and finalize

- A checkpoint is not a test verdict. Verify the relevant behavior, callers,
  interface compatibility, and changed documentation before calling work final.
- Preserve separate meaningful commits where they help review or selective
  reversal; squash/amend only **local, unpublished, exclusively task-owned**
  history when safe. If publication or ownership is uncertain, keep history
  intact. No forced push as a cleanup technique.
- Never auto-push, open a PR, or merge merely because checks pass. Final output
  should identify the actual changed paths, tests, checkpoint SHA(s) when any,
  and publication state without implying Git operations that did not occur.

## Safe recovery

- First inspect the current state and a targeted diff from the selected
  checkpoint. Decide whether the aim is to reverse a commit, restore a particular
  path/hunk, or simply repair forward.
- Prefer a scoped revert for already-committed agent-owned changes, or a
  targeted patch/restore for *proven* agent-owned uncommitted changes. A revert
  may conflict with later edits and must be checked. A path-level restore may
  discard mixed ownership, so do not use it if the file contains user changes.
- Never default to `git reset --hard`, `git clean -fd`, force-updating a
  shared ref, or deleting a dirty worktree. Stop before an irreversible operation
  when ownership is unclear; preserve and report the uncertain changes.
- After recovery, inspect the diff and run the smallest check capable of
  showing the intended state was restored. A successful Git command is not proof
  of functional recovery.

## Documentation-diff relationship

For opted-in `.combo/` projects, compare task-owned paths against the recorded
baseline, including committed/staged/unstaged work and relevant untracked files.
Use the existing `project_kb.py route --path <changed-path>` to locate *candidate*
area/spec/decision records, then inspect the real code and its contracts. Mapping
by path is not proof that a document is current, and missing mapping is not proof
that nothing needs updating. Update only changed canonical claims and regenerate
the project index when its Markdown inputs change.
