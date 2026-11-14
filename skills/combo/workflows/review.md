# Review

Review the requested code, diff, branch, or security concern without editing or
publishing unless authorized. Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

1. Resolve the target, revision, and requested scope. For a change review with
   no target named, inspect the current diff and state the safe assumption. An
   explicit folder-wide or repository-wide audit is **not** a diff review.
   Confirm the target exists and has reviewable material.
2. Read the originating requirement and affected callers, tests, configuration,
   and conventions. Cover the requested scope even when early files look clean.
   For a repository-wide audit, first map entrypoints, important data/trust
   paths, expected load, and existing checks. Go deep first where failures have
   the highest consequence; sample less critical areas and state what was not
   inspected. Do not claim a complete file-by-file audit from a risk sample.
3. If `.combo/` exists, use accepted specs and authorized changes as the contract and retro as hypotheses, not proof of a live defect. Evaluate requirement fidelity (missing, incompatible, partial, or extra
   behavior) and implementation quality (correctness, error boundaries, data,
   concurrency, security, and maintainability) in one impact ranking. When
   volume or concurrency matters, state the load assumed (from the README or
   deploy config) and judge scale against it.
4. For each candidate finding, establish location -> reachable trigger ->
   consequence -> evidence -> smallest remedy. For a changed shared contract,
   identify the affected callers and the critical invariant that might fail;
   prioritize a targeted check capable of falsifying it over generic confidence
   passes. Do not expand coverage for an unaffected tiny change. Inspect guards and callers that
   could invalidate it; use a focused non-mutating probe when useful.
5. For consequential changes, inspect reader load: redundant layers between
   behavior and owner, hidden mutable state, scattered domain decisions and
   contracts that callers cannot locate. Report concrete impact, not style taste.
6. Consolidate symptoms of the same cause while preserving distinct impacts.
   Report supported actionable issues; separate an unresolved concern when the
   missing evidence matters. Style preferences and clean lint are not behavioral
   findings or proof of correctness.

Use [security](../practices/security.md) for actual trust boundaries and
[simplicity](../practices/simplicity.md) for unnecessary layers/options. Additional
reviewers or full suites are conditional, not a universal pipeline.

Lead with the highest-impact findings and precise locations. Include checks and
material unreviewed limits without repeating the whole investigation. If no
material issue is found, say so with the evidence and its limits. For an
authorized repair, continue through [deliver](deliver.md); review-only stops here.

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
