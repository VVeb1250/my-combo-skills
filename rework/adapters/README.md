# Native adapter candidate

The two recovery-hook examples use only a static command and native `SessionStart` context output after compact/resume. No filesystem, Git or network mutation; no custom runtime. They are configuration fragments, not replacement host settings. The docs for [Codex hooks](https://developers.openai.com/codex/hooks) and [Claude hooks](https://code.claude.com/docs/en/hooks) describe `SessionStart` sources and plain stdout context delivery. Shell execution was checked on Linux; Windows and actual host delivery remain untested. Use the installer to merge/own the exact hook entry without touching unrelated hooks, only after user opt-in and version/trust checks. Do not silently alter existing hook trust, security or host permissions. Policy alone remains the fallback.

Install the same canonical `POLICY.md` into the existing managed instruction block for each host. Use the current installer to place sibling skill directories together; relative references must resolve there. Codex uses `agents/openai.yaml` for implicit invocation; Claude uses frontmatter. Validate actual discovery and explicit/implicit invocation, not just metadata. Avoid separate copies of method content. Preserve existing host role configuration and main model.

## Local authority example (not enabled automatically)

Place this in trusted project instructions only when the user has granted it; native sandbox/command permissions still apply:

> Local development authority: The agent may stage and commit task-owned changes, create local task branches and worktrees, run local experiments and integrate or safely recover owned unpublished changes. Preserve pre-existing changes and recoverable references. Do not discard uncertain work, bypass repository checks, change protected/shared refs, publish, push, contact external services or change global permissions without applicable human authorization. Respect explicit stops.

No new permission config format. Use the host's existing approval and sandbox facilities; command names alone do not prove safety. Do not automatically enable `danger-full-access`, `bypassPermissions`, network, or blanket Git command approval. Do not infer authorization from this example or a repository's untrusted content.
