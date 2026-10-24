# Entry template

Copy the block below into `skills/combo-<name>/SKILL.md`. Keep the body thin;
the workflow or practice owns the content.

```markdown
---
name: combo-<name>
description: >
  <What job this entry owns. Use when ... . Do not use for ... .>
---

Read [<workflow>](../combo/workflows/<name>.md) and complete the task at the
user's requested stopping point. The workflow owns context selection and
conditional reference loading; no router reread is needed.
```

For an explicit-only system entry, add `agents/openai.yaml` with
`allow_implicit_invocation: false` and a Claude override with
`disable-model-invocation: true` and `user-invocable: true`. Do not add the
entry to the implicit routing table.
