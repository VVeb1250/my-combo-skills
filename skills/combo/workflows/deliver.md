# Deliver

Deliver working code for a feature, behavior change, known-cause fix, or refactor.
Honor the requested stopping point; a request to build includes verification.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

## Choose the slice

1. Identify user-visible behavior and an observable acceptance condition for
   each requirement, including actual compatibility, security, performance,
   accessibility, and data-loss constraints.
2. Inspect status, relevant repository instructions, affected code, real callers,
   and nearby tests. Preserve unrelated edits. Resolve routine choices from
   evidence; ask only when missing input changes correctness or intended scope.
3. Reuse existing public seams. Read [design](../practices/design.md) for unresolved
   ownership, adapter, or invariant decisions. Choose the smallest design that
   meets the complete requirement, retaining demonstrated extension needs.

Implement independently verifiable vertical slices. For mechanical migration,
use expand/migrate/contract when it preserves working callers. Keep validation
and error handling at trust boundaries; use [security](../practices/security.md)
when those boundaries change. Add dependencies, flexibility, or adjacent changes
only when the requirement or causal evidence needs them.

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
- Inspect the final diff for scope, missed requirements, error paths, and coupling.
  Apply [simplicity](../practices/simplicity.md) when new layers or options appear.
  Repair actionable in-scope findings and verify the affected behavior again.

For failed checks, retain the command and first useful symptom, distinguish
change-caused from pre-existing/environment failures, and fix the causal issue.
Use [build](../practices/build.md) for compiler/dependency chains or
[debug](debug.md) when diagnosis becomes the main task.

Return the result, useful file links, check verdicts, and material unchecked
limits. Commit, publish, or hand off only when existing authorization includes it.

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
