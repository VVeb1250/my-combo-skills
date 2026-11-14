# Debug

Use for a failure, regression, wrong result, flaky behavior, or performance
problem. For diagnosis-only, stop with evidence and a repair proposal.
Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved.

Where `.combo/` exists, retrieve only relevant accepted specs, retro and tested shortcuts using [project ecosystem](../practices/project-ecosystem.md). Check applicability and primary evidence before relying on an old lesson.

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

When evidence already points to wrong ownership, invalid domain states,
scattered special cases or a shared false premise, investigate that structural
cause immediately; the two-repair threshold is only a fallback. Inspection
is not authorization for an out-of-scope rewrite.

For risky Git-backed repairs, establish HEAD, branch and pre-existing dirty paths
before making a change. If the task authorizes local commits, use
[Git checkpoints](../practices/git-checkpoints.md) for recoverable WIP slices;
otherwise keep read-only baseline/diff evidence. Revert only proven agent-owned
commits or changes; never use a destructive whole-tree reset to erase a failed
hypothesis, and do not treat a successful revert as behavior verification.

For prolonged failures, keep a compact record of hypotheses, attempts, observations
and eliminated causes in working context or an existing task artifact. Before a
retry, identify what new evidence will distinguish competing explanations;
otherwise instrument the uncertain boundary rather than guessing at another
patch. If two cause-directed repairs leave the same symptom, or the next patch
would add no distinguishing evidence, reset the premise: identify what the
attempts assumed in common and probe the nearest boundary that could falsify it.
Prefer scoped state snapshots or structured logs over broad verbose logs.

Use [security](../practices/security.md) when the failing path crosses a real
trust or sensitive-data boundary. Lack of reproduction alone is not a blocker.

For a quality failure with technically valid output, reproduce the rejected
artifact and compare it with the intended result using
[outcome evidence](../practices/outcome-evidence.md). Distinguish a local defect
from a mechanism or representation whose output cannot reach the required
quality. A passing functional regression does not close that quality gap.
Reset the premise when evidence shows the current method's ceiling; explore
a bounded alternative within scope instead of accumulating cosmetic patches.

## Repair within authorization

- Convert the repro into a regression at the highest existing seam that detects
  this defect. If no suitable seam exists, keep integration/E2E evidence and
  identify the confidence gap. Use [tests](../practices/tests.md) for seam choices.
  If you forced the red by mutating code or a fixture, diff against a pristine
  copy to confirm the mutation landed before trusting the failure.
- Make the smallest causal repair, preserving real callers' contracts. Retries,
  catches, or refactors need evidence that they address the cause. For a recurring
  defect, prefer a durable enforcement at the responsible seam (state ownership,
  type/schema, lint/CI, or regression test) over another prose warning. Prove
  that the chosen enforcement detects the observed failure; do not add all layers
  by default.
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
