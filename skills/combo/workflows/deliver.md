# Deliver

Deliver working code for a feature, behavior change, known-cause fix, or refactor.
Honor the requested stopping point; a request to build includes verification.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

For code whose intended output is a rendered, generated, spatial, interactive,
or emergent artifact, explicitly use [outcome evidence](../practices/outcome-evidence.md)
alongside functional checks. Keep the primary workflow; choose evidence by the
actual outcome, not the implementation medium.

## Choose the slice

1. Identify user-visible behavior and an observable acceptance condition for
   each requirement, including actual compatibility, security, performance,
   accessibility, and data-loss constraints.
2. Inspect status, relevant repository instructions, affected code, real callers,
   and nearby tests. Preserve unrelated edits. Resolve routine choices from
   evidence; ask only when missing input changes correctness or intended scope.
3. Reuse required existing public seams. For a consequential cross-module
   change, state ownership, or known required variation, consult
   [design](../practices/design.md) even when the request appears clear.
   Close unresolved design alignment before implementing dependent behavior.
   Accept an already agreed design as execution authority; choose methods and
   resolve technical unknowns without reopening the interview. Choose the minimum sustainable design,
   preserving necessary extension points without speculative features.

Reuse tools and evidence, batch independent work, and use bounded
[Subcombo delegation](../practices/delegation.md) when it reduces total cost
without quality loss. Keep necessary discovery and actual-output checks.

For risky or multi-slice Git-backed changes, follow [Git checkpoints](../practices/git-checkpoints.md):
record branch/HEAD and existing dirty paths before editing, and create meaningful
unpublished WIP checkpoints **only when authorized**. A clean initial HEAD is
already a baseline; no checkpoint is required for a tiny edit. Do not stage or
commit unrelated work.

Implement independently verifiable vertical slices. When quality depends on
composition or interaction among generators/features, make the slice a small
integrated outcome (not merely a feature that exists in isolation). For a
materially uncertain quality method, first produce and inspect a bounded real
candidate; carry the demonstrated method into the integrated slice. For mechanical migration,
use expand/migrate/contract when it preserves working callers. Keep validation
and error handling at trust boundaries; use [security](../practices/security.md)
when those boundaries change. Add dependencies, flexibility, or adjacent changes
only when the requirement or causal evidence needs them.

If the project has `.combo/`, consult [project ecosystem](../practices/project-ecosystem.md) for accepted requirements, task-scoped deltas, selective retro, and tested shortcuts. Never use an old lesson to override current code or approved intent.

## Verify and finish

- Select behavioral checks with [tests](../practices/tests.md). Use red-green
  when it clarifies new behavior or a regression. Tiny reversible edits need
  inspection and the cheapest relevant check, not an artificial suite.
- Check each meaningful slice. Map every acceptance condition to actual evidence;
  keep this mapping in context unless a report needs it.
- A shared contract change needs affected-caller coverage; dependency/config
  changes need the relevant build or integration check; trust-boundary changes
  need rejection-path evidence. Complete explicit repository/user gates.
  Reuse still-valid checks instead of automatically rerunning each phase.
- For interactive UI changes, exercise the primary journey using
  [e2e](../practices/e2e.md) when browser testing is within the authorized scope.
  Include the transitions that could invalidate saved or derived state, rather
  than treating successful individual controls as a completed journey.
- Inspect the changed area for repeated root causes, unclear state ownership, shotgun edits and duplicated transitions. Apply targeted behavior-preserving refactoring only when justified by actual friction and recheck affected behavior.
- Use [verification economy](../practices/verification-economy.md) to select adequate focused evidence before an expensive Browser/reviewer pass; never weaken explicit gates.
- Inspect the final result and diff along the separate outcome/spec and
  engineering/standards axes in [review](review.md). Keep their verdicts
  distinct when either has a material gap; neither substitutes for the other.
  Apply [simplicity](../practices/simplicity.md) when new layers or options appear.
  Repair actionable in-scope findings and verify the affected behavior again.
  Use a focused reviewer only if justified; no additional stage or formal
  report is required for a routine edit.

For failed checks, retain the command and first useful symptom, distinguish
change-caused from pre-existing/environment failures, and fix the causal issue.
If two meaningful repairs leave the same symptom, or the next patch would produce
no new diagnostic evidence, stop speculative retries. Follow [debug](debug.md):
collect a discriminating observation with a targeted log, trace, assertion,
replay or debugger before another patch. Preserve failed attempts in working
context or an existing task note, not a mandatory new log file. Use
[build](../practices/build.md) for compiler/dependency failures. Resume
relevant acceptance checks only after a cause-supported repair.

For an opted-in `.combo/` project, use changed source paths to find candidate
owner/spec/decision records with the existing [project ecosystem](../practices/project-ecosystem.md)
routing. Update changed canonical contracts and regenerate a touched index; a
path miss does not prove no documentation impact.

Return the result, useful file links, check verdicts, and material unchecked
limits. Finalize an authorized draft only after appropriate verification;
commit, publish, or hand off only within the granted Git authorization.

<!-- BEGIN CONTEXT CORE (generated from practices/context.md by scripts/sync-context-core.py; edit there) -->
## Context rules

### Own the outcome

Translate the request into its intended result, binding constraints, and observable
acceptance. Discover necessary implicit work from real references, callers, and
delivery conditions: choose the method and carry authorized work through to that
result. Inferred implementation steps are not permission to expand scope or cross
the requested stopping point.

Keep quality, fidelity, and domain behavior in the acceptance target even when
they are harder to measure than functionality. Define checks from that target,
not from the first implementation or what is easiest to test. A working
mechanism, a complete feature list, or a passing proxy is not evidence of an
adequate outcome. When the method's ability to reach the target is materially
uncertain, use a bounded real-output probe before scaling it; compare the
observed result against the target and revise the method if needed. This is
conditional, not a new stage for routine work.

Keep the user's spec and design intent as the comparison target. Preserve approved
choices and parts that already pass. A proposed simplification, style direction,
or changed acceptance remains a proposal until the user agrees; silence, a tool
success, and an assistant summary are not assent. If the target is infeasible,
show the evidence and request the consequential tradeoff instead of quietly
substituting an easier result. Distinguish facts, inference, and testable hypotheses
where that distinction changes a decision or claim.

After a context reset or resumption, check the next plan against the user's own
binding instructions and decisions, latest first, before the first action; a
retained user instruction outranks your summary of the plan.

### Decision triage

Resolve facts from context, code, references, tools, and bounded experiments.
Do not ask the user to discover facts or choose routine implementation methods.
For consequential design, identify unresolved user-owned choices early; do not
treat the existence of multiple viable algorithms as missing user intent.

**Design alignment (before execution).** If the intended outcome, binding
constraints, or consequential user-owned design decisions are unresolved,
front-load a design interview before committing to dependent design. Map the
relevant decision tree; ask the whole frontier of independent decisions whose
prerequisites are settled, with a recommendation and meaningful tradeoff for
each. Recompute the frontier after answers. Research facts concurrently when
economical (see [delegation](../practices/delegation.md)); only dependent questions wait.
Use a bounded prototype when seeing an outcome is necessary to settle taste,
within the authorized stopping point. Close the interview when the material
decisions are settled and shared understanding is established. Confirm when
an actual approval boundary remains; an explicit authorization on an agreed
design already suffices. Do not impose a new interview or approval ceremony
on an already-aligned request, routine edit, or delegated design decision.

**Execution authority (after alignment).** Own the authorized outcome.
Independently choose implementation methods, investigate unknown mechanisms,
experiment, inspect integrated results, and refine fixable quality gaps.
Do not reopen settled decisions, stop for intermediate verification or require
approval for every slice. Progress updates do not request approval; continue
authorized work. Escalate only if new evidence exposes a consequential
user-owned choice outside existing authority, such as a necessary change to
binding intent, a material risk, or an infeasible accepted constraint.
Explain the evidence, viable tradeoff and recommendation; continue independent
authorized work. Preserve plan-only and explicit user checkpoints and host
permission boundaries. Record material assumptions or unresolved limits.
See [design](../practices/design.md) for technical probes.

### Verify against intent

Choose evidence capable of detecting the actual mismatch, proportional to the
task and risk. For reference fidelity, rendered artifacts, or uncertain success
signals, read [outcome evidence](../practices/outcome-evidence.md). A successful command proves
only that command's result, not task success. Compare the actual deliverable with
acceptance; diagnose an observed gap, refine the affected part, and recheck it and
anything the change could invalidate. Keep passing parts and still-valid evidence.
Finish when the agreed criteria are supported. Distinguish implementation,
technical checks, outcome quality, and any required user approval when their
verdicts differ. If quality is below target, refine within scope or report the
outcome as incomplete; if decisive access is unavailable, name the exact
unverified criterion and deliver independent work. Do not loop on unchanged
evidence, equate self-reported checks with acceptance, or claim completion across
a material gap.
<!-- END CONTEXT CORE -->
