# Context and resumption

Use a state snapshot when work spans phases, sessions, or executors. Keep it
small enough to read and concrete enough to resume:

```text
Goal / stopping point:
Acceptance:
Done and evidence:
Current phase:
Changed areas:
Next action:
Blocker or decision needed:
Checks and verdicts:
```

- Continue when the next step needs the current reasoning or closely coupled
  work. Clear when the context is disposable and a fresh start is cheaper.
- Compact at a meaningful milestone or phase boundary when the window is large;
  there is no blanket ban on compaction. Do not compact merely to follow a
  ceremony or while an active debugging loop would lose its evidence.
- Handoff when portability is the purpose, such as a new harness, directory,
  colleague, or side task. Include conclusions, evidence, unresolved questions,
  and an exact resume action.
- On resume, recover the user's current goal and constraints, verify stale facts
  that matter, and begin at the unresolved action. Do not repeat discovery or
  re-ask an already answered authorization.
- Keep artifacts in an existing repository convention when they will be used by
  another executor. Do not create a custom state engine for a one-shot task.

The primary agent owns final interpretation and acceptance even when another
executor performs a bounded slice.
