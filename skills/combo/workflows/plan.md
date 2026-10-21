# Plan

Produce an actionable requirements, design, or implementation plan. Plan-only
ends with the plan; building or prototyping requires applicable authorization.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

1. Identify the outcome, constraints, compatibility obligations, and requested
   fidelity. Inspect relevant code, real callers, tests, domain terms, and ADRs.
2. Resolve routine details from evidence. Surface unknowns only when they change
   behavior, contracts, integrity, security, cost, or scope. Use primary sources
   with version/date for changing external facts.
3. Compare viable approaches against these constraints and recommend one.
   Keep an alternative only when its tradeoff affects the decision.
4. Preserve existing adapters and public seams. Use [design](../practices/design.md)
   for unresolved boundaries and [tests](../practices/tests.md) for acceptance.
   If an uncertainty needs a runnable prototype, run it only within the requested
   scope and host mode; otherwise specify the bounded experiment in the plan.
5. Express implementation as vertical slices with observable done conditions and
   genuine dependencies. For broad migrations, use expand/migrate/contract to
   keep callers working between steps where feasible.

The plan is ready when an executor can identify affected areas, required contract
behavior, the chosen approach, acceptance checks, and the first action, with
decision-changing unknowns resolved or explicitly assigned. Stop exploring
equivalent alternatives at that point.

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

Resolve facts from context, files, references, tools, or a bounded experiment before
asking. Choose routine methods from that evidence. Ask only about an unresolved
choice that materially changes outcome, taste, compatibility, risk, cost, or scope
and cannot be established from the available evidence. An unavailable reference
is a gap to resolve, not permission to guess its contents.

For a behavior change, current implementation establishes what exists, not the
requested new intent. If two plausible readings produce materially different
user-visible results and the evidence leaves both open, ask before committing
either. Keeping an existing default is a recommendation, not user assent.

Ask the smallest decision-changing question, with a recommended answer and the
tradeoff of a viable alternative. Settle prerequisites before dependent choices;
bundle only independent questions when useful. Wait for answers before dependent
work, while continuing independent authorized work. Prior user answers remain
binding. For reversible details with little effect, state a material assumption
when needed and proceed; do not turn every implementation choice into an interview.

When taste needs seeing, use a small prototype or visual alternatives within the
authorized scope, identify what the choice settles, and get the user's selection
before committing the disputed direction. A plan-only boundary still applies.
Stop questioning once remaining uncertainty cannot materially change the result.

### Verify against intent

Choose evidence capable of detecting the actual mismatch, proportional to the
task and risk. For reference fidelity, rendered artifacts, or uncertain success
signals, read [outcome evidence](../practices/outcome-evidence.md). A successful command proves
only that command's result, not task success. Compare the actual deliverable with
acceptance; diagnose an observed gap, refine the affected part, and recheck it and
anything the change could invalidate. Keep passing parts and still-valid evidence.
Finish when the agreed criteria are supported; if decisive access is unavailable,
deliver independent work and name the exact unverified criterion. Do not loop on
unchanged evidence or claim completion across that gap.
<!-- END CONTEXT CORE -->
