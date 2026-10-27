# Review

Review the requested code, diff, branch, or security concern without editing or
publishing unless authorized. Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

1. Resolve the target, revision and requested scope. For an unspecified change review, inspect the current diff and state the safe assumption; an explicitly repository-wide audit is not a diff review. Confirm the target exists and has reviewable material.
2. Read the originating requirement and affected callers, tests, configuration,
   and conventions. Cover the requested scope even when early files look clean.
   For repository-wide audits, map entrypoints, important data/trust paths and existing checks; investigate highest-consequence paths first. Disclose any risk-sampled areas instead of claiming exhaustive file coverage.
3. If `.combo/` exists, use accepted specs and authorized changes as the contract and retro as hypotheses, not proof of a live defect. Evaluate requirement fidelity (missing, incompatible, partial, or extra
   behavior) and implementation quality (correctness, error boundaries, data,
   concurrency, security, and maintainability) in one impact ranking. When
   volume or concurrency matters, state the load assumed (from the README or
   deploy config) and judge scale against it.
4. For each candidate finding, establish location -> reachable trigger ->
   consequence -> evidence -> smallest remedy. Inspect guards and callers that
   could invalidate it; use a focused non-mutating probe when useful.
5. Consolidate symptoms of the same cause while preserving distinct impacts.
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
