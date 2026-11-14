# Plan

Produce an actionable requirements, design, or implementation plan. Plan-only
ends with the plan; building or prototyping requires applicable authorization.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

1. Identify the outcome, constraints, compatibility obligations, and requested
   fidelity. Inspect relevant code, real callers, tests, domain terms, and ADRs.
2. Resolve facts from evidence and front-load the context design interview for
   consequential unresolved user-owned choices before committing dependent
   design. Ask the complete ready frontier and settle prerequisites in rounds. Do not ask about clear routine choices or repeat accepted decisions.
   Use primary sources with version/date for changing external facts.
3. Compare viable approaches against these constraints and recommend one.
   Keep an alternative only when its tradeoff affects the decision.
4. Preserve required adapters and public seams. For consequential cross-module
   design, known required variations or state-ownership risk, consult
   [design](../practices/design.md) even if the prompt sounds clear.
   Use [tests](../practices/tests.md) for acceptance.
   If an uncertainty needs a runnable prototype, run it only within the requested
   scope and host mode; otherwise specify the bounded experiment in the plan.
5. Express implementation as vertical slices with observable done conditions and
   genuine dependencies. For broad migrations, use expand/migrate/contract to
   keep callers working between steps where feasible.

The plan is ready when an executor can identify affected areas, required contract
behavior, the chosen approach, acceptance checks, and the first action, with
decision-changing unknowns resolved or explicitly assigned. Stop exploring
equivalent alternatives at that point.

For an opt-in `.combo/` project, read [project ecosystem](../practices/project-ecosystem.md): write observable capability requirements using RFC 2119/8174 and proposed change deltas without duplicating Matt and OpenSpec planning pipelines. Tiny fixes do not need new docs.

A bounded plan can live in the response. Use existing artifact conventions for
multi-session or independent execution when useful. Include rationale and risks
that change execution; create trackers or additional specs only when requested
or necessary for the agreed deliverable. Ask only the smallest unresolved
question that changes the plan.

For an effort too large for one session whose route is not yet visible, borrow the
idea of [wayfinder](../references/library/matt/skills/engineering/wayfinder/REFERENCE.md):
name the destination, resolve decisions rather than build, record each decision once
and index it, and keep a question you cannot yet state precisely as unspecified
instead of ticketing it. Keep that state in one file or the tracker the repository
already uses. Take its tracker, label, claim, and subagent mechanics only when
sessions run in parallel and applicable authorization exists.

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
