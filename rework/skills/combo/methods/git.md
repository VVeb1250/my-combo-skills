# Local recoverability

Native Git is the harness. Permission from the user and host both apply; no automatic remote writes. Local operations can also trigger hooks, filters or shared runtime effects. Check relevant repository policy and do not bypass required gates.

## Baseline and checkpoint

Before consequential edits inspect branch/HEAD, `git status --short --branch`, staged and unstaged diffs, relevant untracked files and in-progress Git operations. Existing changes are not yours. Record the baseline in working context and preserve ownership/transition evidence durably if needed across reset. A clean HEAD is already a baseline. Do not silently stash or move user changes.

With standing local authorization, checkpoint meaningful separable progress during work, especially before a risky next action, unrelated changes or focus switch. Stage explicit owned paths/hunks and inspect the complete staged set (`git diff --cached`), including pre-existing staged work. If ownership cannot be separated, use isolation or preserve the state without committing and report the gap; never accidentally include someone else's index. Include related contracts/tests/docs. WIP is an honest local checkpoint when allowed; not a verified claim. Follow branch conventions (e.g. no broken commits on protected branches). Do not force empty commits, per-file commits or blanket staging. Inspect commit and remaining status.

## Choose the operation from the need

| Need | Technique and boundary |
|---|---|
| Risky experiment | Create an owned branch/worktree from the intended committed baseline. Worktree at HEAD does not include dirty changes; do not silently copy them. |
| Historical rationale | Targeted `log -- path`, `show`, `blame`, `log -S/-G/-L`; history is evidence, not accepted intent. |
| Regression | `bisect` in an isolated tree using good/bad revisions and an applicable deterministic probe; skip untestable commits correctly, inspect cause. |
| Integrate partial candidate | `cherry-pick` or local merge of compatible owned commits; include dependencies and reverify. |
| Compare revisions | `range-diff` for patch series, normal diff for state; neither proves behavior. |
| Recover | Inspect target and changes; prefer scoped revert or proven owned hunk restoration. Preserve a recovery ref before safe authorized history edits. |
| Lost reference | Reflog may locate old commits; preserve with branch. Not a backup for untracked files; expiry applies. |
| Pause | WIP checkpoint if allowed; stash only with explicit ownership and discoverable recovery pointer. |
| High-risk committed-history backup | `bundle` when justified; uncommitted/ignored data is not included. |

Local integration/recovery requires ownership, recoverability and repository permission. Do not reset hard, clean unknown files, delete unique unpreserved work, force-update shared refs or rewrite history just to tidy. Never auto-push/publish/open PR/merge remotely. A hard stop overrides checkpoint duty. After recovery inspect actual state, reverify affected behavior and reconcile [wiki](wiki.md); reverting code does not revoke accepted intent. See [continuity](continuity.md) on compaction or unknown ownership.
