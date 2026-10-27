# Evidence-efficient verification

Use this practice **only** when deciding whether to escalate from adequate
focused checks to an additional expensive Browser journey, broad test suite,
external reviewer, or other costly verification. Acceptance and stopping point
are owned by [context](context.md); test seams and relevant checks by
[tests](tests.md); rendered/reference fidelity by
[outcome evidence](outcome-evidence.md). This practice does not add another
mandatory review stage.

Choose evidence capable of falsifying the uncovered criterion at the lowest
adequate cost. Prefer existing deterministic results, focused tests, type
checks, replay/simulation traces, or integration probes at the public seam.
Use the Browser for UI/cross-component journeys when observed interaction is
part of acceptance or cheaper evidence leaves a material gap. Follow native
host/browser requirements.

Reuse valid checks when the revision, relevant code, inputs and environment
are unchanged. Escalate for a failed check, changed behavior boundary, material
uncovered criterion, or explicitly required coverage, **not** for another
confidence pass on unchanged evidence. A model agreeing with itself is not
independent proof. Stop once acceptance has adequate support; disclose exact
unverified claims when access is blocked. Do not weaken explicitly requested
full suites, repository gates, security or data-loss requirements.

Structural refactoring belongs to [simplicity](simplicity.md).
Project-local shortcut preconditions, validation and fallback belong to
[project ecosystem](project-ecosystem.md); neither is a required part of
verification escalation.
