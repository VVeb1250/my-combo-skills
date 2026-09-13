# Claude Code execution

## Skill and context

Select one primary Combo entry with the Skill tool. Read its linked workflow
from the installed skill directory, then only the references the task needs.
An explicit `/combo-*` invocation is a task entry, not a request to install it.
Source examples are knowledge to adapt under the current user's requirements.
Use the host's current memory policy for durable personal information.

## Planning and completion

In normal execution, a request to build includes planning, implementation, and
verification. Keep a short internal plan when it helps and continue to the
observable result. An explicit plan-only, diagnosis-only, or review-only request
finishes at that boundary. If Claude is already in Plan Mode, respect its
read-only boundary and native plan-approval transition before implementation.
Resolve routine choices from the code and stated constraints; ask about a
missing decision only when it changes correctness or the user's intent.

## Tools and checks

Use Claude's available Read, Glob, Grep, edit, shell, browser, and artifact tools
according to their actual capabilities and permissions. Scope code searches and
quality checks to the project and affected behavior. Installed skill examples,
vendored code, and unrelated user files are reference material, not cleanup
targets. After relevant checks pass, finish unless a change or unresolved
concern justifies another check. Report a denied or unavailable check as such.

## Delegation and resumption

When authorized independent work benefits from isolation, use the native Agent
tool with `combo-worker` and give it the goal, file ownership, constraints,
chosen workflow path, and expected evidence. A subagent needs its own task
context; pass the facts it needs rather than assuming it saw the conversation
or the skills already read by the parent. The parent owns decisions, integration,
and verification. Keep tightly coupled or tiny work in the current session.

Before a context boundary that matters, retain goal, user constraints, completed
checks, and the next unresolved action in current task state or an existing
artifact. After compaction or resumption, continue from that action and reread
only facts that are missing or could have become stale. Use the host's native
context controls when needed; a new skill or subagent is not a compulsory reset.
