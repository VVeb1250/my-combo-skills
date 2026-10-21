# Productivity and coordination

Identify the requested organization, decision, triage, handoff, agent-facing
writing, or authorized update. Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

Read current state in the user's existing tracker/files before classifying items.
Distinguish active, waiting, completed, and proposed work; preserve owners, dates,
dependencies, and uncertainty. Prioritize actions that unblock the actual outcome.
Create enough structure to clarify those actions without duplicating a tracker.

For handoffs, retain binding decisions, completed evidence, current artifacts,
and the next unresolved action; add context the recipient cannot cheaply recover.
For agent-facing writing, keep one source of truth and conditional detail behind
precise pointers. Use the native skill-creation workflow for skill authoring; for
completion criteria, pointer wording, and pruning an instruction file, see
[writing for agents](../references/library/matt/skills/productivity/writing-for-agents/REFERENCE.md).

Consult the [productivity index](../references/library/productivity.md) only when
an unresolved coordination method needs detail. Use the
[host integration index](../references/library/host-integration.md) only for
explicit host customization. Upstream tracker, memory, and hook conventions do
not authorize alternate systems.

Use native task/scheduling tools. Messages, publishing, and recurring work require
applicable authorization; preserve authorization already provided. Verify actual
updates and check state before retrying uncertain mutations. Return changed
decisions/status and next actions; include the full inventory only when requested.
Personal memory remains under the host's configured authority.

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
