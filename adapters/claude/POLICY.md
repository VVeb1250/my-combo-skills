## Combo engineering policy

Applies to coding, debugging, software design, and code review.
The engineering principles below do not impose coding ceremonies on other work.

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

## Combo task routing in Claude Code

For substantive engineering, research, content, learning, business, media, or
productivity work, invoke the matching `combo-*` skill with the Skill tool.
Use `/combo` for uncertain or cross-workflow requests. Choose one primary path
and load its workflow and shared context for outcome and decision triage, then relevant references.
Continue using loaded guidance on follow-ups; simple chat, one-sentence
translation, and tiny understood edits can stay inline. Native tool-specific
skills remain responsible for browser and artifact operations.

Honor the requested stopping point. In normal execution, a request to build
continues through implementation and verification. An active Plan Mode retains
its native read-only and approval boundary. When authorized independent work
benefits from delegation, give `combo-worker` explicit context and file ownership.
The host's configured memory and permission rules remain authoritative.
