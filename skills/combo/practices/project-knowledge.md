# Project knowledge

Use when writing or reviewing project Markdown or code comments and deciding
what rationale to retain, where it belongs, or how to update it. Work within the
requested scope; a review reports findings unless edits are authorized.

## Retain reasoning where it is needed

Record decisions a future maintainer cannot cheaply reconstruct: the constraint,
why the chosen approach satisfies it, and any consequential rejected alternative.
Keep qualifications and evidence that prevent the same mistake from recurring.
Code, configuration, and tests remain the source for directly observable behavior.

Keep a comment beside code when its reason is needed to change that code safely.
For example: "Probe writability after changing permissions; a success exit code
does not establish that access was granted." Keep the detailed incident and its
measurements in the relevant report if they matter for audit or later decisions.
Comment length alone is not a defect; preserve a longer explanation when splitting
it would hide a necessary invariant or condition.

For decisions spanning modules, use the existing design document or decision
record and link from affected code. Create a separate record only when the
decision needs independent discovery or maintenance. Link an existing record
rather than copying its rationale into the task list and every caller.

## Make Markdown navigable

Lead with the document's purpose and the information its reader needs to act.
Use descriptive headings, one topic per section, short connected paragraphs,
lists for steps or parallel items, and tables for genuine comparisons. Put blank
lines around lists and fences; label links with the decision or evidence they open.
Keep scope and qualifications beside the claims they constrain.

Separate current contracts, pending work, and historical results when their
mixture obscures which information applies. An accepted design and its unfinished
implementation are distinct states. A task list points to rationale and results;
it need not duplicate them. Reuse an existing entrypoint instead of adding another
index. Maintain a summary together with its source, or omit duplicate counts and
status tables that cannot be kept current.

## Update without losing evidence

When changing behavior or a decision, inspect and update the explanations directly
affected by that change. Replace obsolete current claims; keep necessary history
in its existing evidence record, clearly marked as superseded with a pointer to
the replacement. Preserve immutable experiment results and correct interpretation
through an identified erratum, not by rewriting the original evidence.

For handoff, update the existing task or checkpoint only with the goal, verified
state, binding decisions, unresolved work, and next action that cannot be cheaply
recovered. Coordinate ownership before restructuring a file other sessions edit.
For a long setup or debug flow driven by CLI or tool commands, include the commands
that worked and the state already changed, so a reset does not repeat discovery.
Routine work does not require a new Markdown artifact or transcript summary.

## Optional project ecosystem

When a project already has `.combo/` or the owner requests it, consult [project ecosystem](project-ecosystem.md) for canonical accepted specs, proposed change deltas, evidence-linked retro, tested shortcuts and a generated index. Do not duplicate existing ADRs, OpenSpec sources, raw experiment artifacts, or personal memory.

## Memory boundary and completion

Project documentation must remain understandable to collaborators without access
to the author's personal memory. Capture, lesson distillation, recall, and export
follow the configured memory system's authority and authorization rules. If a
memory export is later supplied, retain its source and update route; keep generated
views distinguishable from hand-maintained text and do not overwrite the latter.

Finish when affected explanations match the verified state, relevant links resolve,
current decisions are distinguishable from proposals and history, and the rationale
needed for the next safe change is discoverable. Report substantive documentation
defects in review; do not turn formatting preferences into correctness findings.
