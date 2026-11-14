# Delegation

The main agent is the single owner of intent, architecture, integration,
outcome quality and final acceptance. Within user and host authorization,
delegate bounded work when expected total cost (worker, handoff, review and
rework) is lower than doing it directly without material quality loss. No
per-task permission ceremony for an already authorized worker; explicit
restrictions and host permissions always apply. Complexity alone does not
justify spawning agents.

Use the host's configured Subcombo role for the actual job:
- `subcombo-research`: factual discovery, large-context reading, extraction,
  source mapping and counterevidence. Return source pointers and decisive facts.
- `subcombo-implement`: bounded execution under an agreed contract and file
  ownership. Return changes, relevant checks and unresolved defects.
- `subcombo-verify`: focused independent checks and actual-output evidence.
  Return commands, inputs, failures and limits; parent decides acceptance.

Select the least expensive sufficiently capable configured model/effort for the
subtask; do not change the main model. For tiny or tightly coupled work, use
the main agent. Prefer deterministic tools for mechanical work. Do not duplicate
exploration, spawn advisors by default, or create overlapping edits. A worker
cannot own product decisions or final acceptance.

Give one objective, scope, accepted constraints, relevant context, and evidence
to return. In design alignment, independent factual discovery may run while the
main agent asks unrelated frontier questions; only dependent questions wait.
Read the worker's decisive source evidence and verify material claims as needed;
do not reread every source or rerun every check without a reason. Inspect
implementation diffs and verify affected acceptance before integration. Preserve
user and other worker changes. Workers do not recursively delegate, publish,
message third parties or change unrelated configuration.

If delegation is unavailable, unsuitable or uneconomical, do the work locally.
Do not invent a worker or claim an independent check that did not occur.
