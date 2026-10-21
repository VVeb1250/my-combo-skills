# Debug

Use for a failure, regression, wrong result, flaky behavior, or performance
problem. For diagnosis-only, stop with evidence and a repair proposal.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

## Establish and distinguish

1. Identify the reported input, environment, expected result, and exact symptom.
   Inspect affected code, real callers, relevant instructions, and recent changes.
   Choose the cheapest check that distinguishes fixed from unfixed.
2. Prefer a deterministic repro, request, journey, trace replay, or timing
   harness. If reproduction is unavailable, use logs, the reported input, and
   known-good comparisons; distinguish observed, inferred, and unknown claims.
   Verify that any reproduced failure is the user's symptom.
3. For performance, measure a baseline. For build/type failures, group dependent
   errors and inspect the earliest causal one using [build](../practices/build.md).
4. When causes compete, use a short hypothesis -> distinguishing probe ->
   observation -> next action loop. Change one relevant variable. If a probe
   cannot separate explanations, choose another boundary instead of repeating
   it. Trace shared transformations, configuration, lifecycle, or concurrency
   only as the signal requires. Prefer a debugger/REPL or targeted instrumentation;
   tag temporary logs and keep secrets out.

Use [security](../practices/security.md) when the failing path crosses a real
trust or sensitive-data boundary. Lack of reproduction alone is not a blocker.

## Repair within authorization

- Convert the repro into a regression at the highest existing seam that detects
  this defect. If no suitable seam exists, keep integration/E2E evidence and
  identify the confidence gap. Use [tests](../practices/tests.md) for seam choices.
  If you forced the red by mutating code or a fixture, diff against a pristine
  copy to confirm the mutation landed before trusting the failure.
- Make the smallest causal repair, preserving real callers' contracts. Retries,
  catches, or refactors need evidence that they address the cause.
- Check the regression and original unminimized symptom; one run can cover both.
  Broaden for affected callers, contracts, dependencies, or required gates.
- Remove diagnostic-only instrumentation; retain durable regression fixtures.
  After relevant checks pass, finish unless new changes or evidence require more.

Report the cause with its evidence/confidence, repair if authorized, and observed
verification. Distinguish fixed, reproduced, not reproduced, inconclusive, and
blocked outcomes. If decisive access is missing, state the exact gap and next
discriminating check while completing independent authorized work.

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
