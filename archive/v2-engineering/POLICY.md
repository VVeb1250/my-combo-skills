## Combo engineering policy

Applies to coding, debugging, software design, and code review.
For prose, documents, research, and general chat, use the relevant task guidance.

### Karpathy core

- Surface material assumptions; resolve routine choices from available evidence.
- Ask only when missing information changes correctness or the user's intent.
- Define observable success before implementation, briefly for small tasks.
- Read the affected code and real callers before choosing the change.
- Prefer the simplest solution that satisfies the complete actual requirement.
- Touch only what the task requires; preserve unrelated user edits.
- Surgical means the smallest correct blast radius, not the fewest files.
- Fix the demonstrated root cause, including shared code when evidence requires it.
- Verify the success criteria before claiming completion; report checks not run.

### Ponytail pressure

Before adding a dependency, abstraction, config, or helper, consider:
unnecessary? -> existing code -> stdlib -> native platform -> installed dependency
-> readable one-liner -> minimum maintainable code.
Choose the smallest solution preserving design proven necessary by real use.
Keep required trust-boundary validation, data-loss protection, security, and accessibility.
Retain explicit user requirements and demonstrated adapters, calibration, and extension seams.
Do not substitute a reduced feature for what the user requested.
Do not code-golf, enforce line-count targets, or perform unrelated cleanup.

### Conflict resolution within engineering guidance

Correctness/safety > explicit user requirement > verified architecture/domain constraint
> surgical scope > simplicity > style preference.
These are engineering tradeoffs, subject to the host's instruction hierarchy.
Two real adapters can justify a seam. A trust boundary can require validation.
Explicit extensibility requirements can justify abstraction. Shared root causes can require more files.

### Combo router

For a new engineering task, read the installed `$combo` skill from the
available-skills list. Once loaded, continue using it without rereading it on
every follow-up. Select one primary path and load only the practice or
specialist material needed for the current task. Use native host skills for
browsers, documents, images, and concrete utilities.

The router honors the user's requested stopping point. Tiny understood edits can
stay inline. Planning, debugging, delivery, review, verification, and
investigation each have their own path. Checks, tests, security review,
simplicity review, delegation, compaction, and handoff scale with the actual
task; none is a universal ceremony or deterministic gate.

Keep existing public behavior tests and add regression tests when they can
detect the actual defect. Do not publish, push, message third parties, or
install services unless the user authorizes that action.
