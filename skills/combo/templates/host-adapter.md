# Host adapter checklist

Keep the workflow, practice, and reference body shared. The adapter owns only
what actually differs by host.

## Declare

- Host name and supported version.
- Entrypoint files and their frontmatter.
- Invocation policy: implicit, explicit-only, or user-invocable.
- Runtime path variable and relative link form.
- Model and worker configuration, if the host supports it.
- Settings, plugin disables, and policy markers.
- Install manifest, ownership index, receipt, and rollback command.

## Codex

- `agents/openai.yaml` per entry; `allow_implicit_invocation` is explicit.
- Use `$combo-*` for explicit invocation.
- Keep worker model config in the adapter, not the shared workflow.

## Claude Code

- `disable-model-invocation` and `user-invocable` in frontmatter.
- Use `/combo-*` for explicit invocation.
- Use `${CLAUDE_SKILL_DIR}` for runtime links; keep a normal relative link for
  validation.
- Use a native subagent with `model: inherit` when delegation is configured.

## Verify

- [ ] Every entrypoint has a valid name and description.
- [ ] Every relative link resolves in the installed package.
- [ ] Discovery shows the expected entries.
- [ ] Explicit-only entries do not appear as implicit routes.
- [ ] The plan touches only declared ownership.
- [ ] Apply produces a receipt; rollback restores the previous state.
- [ ] A representative task still completes.
