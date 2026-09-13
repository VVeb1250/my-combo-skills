# Delegation

Delegate only when the task is authorized, independent, bounded, and cheaper to
run outside the primary context. The primary agent keeps ownership of intent,
architecture, difficult tradeoffs, integration, and final acceptance.

- Give the executor one clear objective, explicit file or responsibility scope,
  acceptance criteria, constraints about shared workspace edits, and the exact
  evidence to return.
- Use the host-configured execution role for worker work. If the host exposes no
  worker role, perform the bounded work locally and say so truthfully.
- Keep one small task local. Delegate research, routine implementation, or a
  focused check when it removes work; do not fan out overlapping edits or split
  a decision that needs shared context.
- A worker report should contain files changed, commands and verdicts, findings,
  assumptions, and blockers. It should not publish, message third parties, or
  modify unrelated configuration unless explicitly authorized.
- Before integrating, inspect the diff and rerun the relevant acceptance check.
  Resolve conflicts by intent and current requirements, preserving unrelated
  user changes.

Delegation is a context boundary, not a quality shortcut. Do not invent a
fallback agent or claim that work ran elsewhere when it ran locally.
