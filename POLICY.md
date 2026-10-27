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

## Combo task routing

For substantive engineering, research, content, learning, business, media, or
productivity work, select the matching installed `combo-*` workflow entry from
the available-skills list. Use `$combo` for uncertain or cross-workflow requests.
Choose one primary path; its workflow embeds the shared context core for outcome
and decision triage. Read separate context guidance only for unresolved mechanics;
do not reread the workflow on every follow-up. Native host skills own browser,
document, image, and concrete utility operations. Simple chat, one-sentence
translation, and tiny understood edits can stay inline.

The router honors the user's requested stopping point. Tiny understood edits can
stay inline. Planning, debugging, delivery, review, verification, and
investigation each have their own path. Checks, tests, security review,
simplicity review, delegation, compaction, and handoff scale with the actual
task; none is a universal ceremony or deterministic gate.

System entries are not task routes. `$combo-author` is explicit-only for
customizing this pack or building a Combo-like system, not an implicit route.
`$combo-maintain` owns observed-failure improvement to existing Combo behavior
and installation, update, verification, and rollback. Structural authoring
remains explicit-only.

Keep existing public behavior tests and add regression tests when they can
detect the actual defect. Do not publish, push, message third parties, or
install services unless the user authorizes that action.
