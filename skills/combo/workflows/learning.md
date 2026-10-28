# Teaching and learning

Choose a tangible learning outcome from the learner's goal, prior knowledge,
and time. Apply the context rules at the end of this file; read
[context](../practices/context.md) only for evidence-selection or reporting
mechanics that are unresolved. Ask about prerequisites only when they change correctness.

HOW/WHY teaching questions seek mechanism, causal explanation, and a useful
mental model, not necessarily project archaeology. Keep learning as the primary
workflow when the user asks to be taught, even if the example is from their
codebase; retrieve specific accepted decisions through the investigation method
only when necessary for factual accuracy. Do not run two full workflows.

Explain the concept needed for that outcome, then work a concrete example with
useful reasoning visible. Check example mechanics, including executable behavior
and type consistency for code. Include a small recall or transfer exercise when the user requests practice,
interactive instruction, or a course designed for active recall. For read-only
teaching, use worked examples and contrastive cases without requiring a learner
response or ending with a quiz. Avoid recognition-only questions when they would
hide misunderstanding.

Give feedback from the learner's actual response and adjust the next step.
Keep solutions separate when early disclosure spoils practice. For a bounded
one-response lesson, provide the requested usable practice within that response;
a course does not need to be invented.

For sustained courses or an unresolved teaching method, consult the
[learning index](../references/library/learning.md) for spacing, interleaving, or
course structure. When a course schedules reviews, compute the due dates from actual
review times with a scheduling library such as FSRS (`py-fsrs`,
`Scheduler(enable_fuzzing=False)`) instead of estimating intervals; its defaults are
population parameters, not fitted to this learner. Use authoritative references for
changing or uncertain facts and native visuals/artifacts when they clarify the
mechanism or are requested.

Finish with the explanation and any practice actually requested. Reduce
redundant framing, not the examples or reasoning the learner needs. Create course records only for
a requested workspace; durable personal information follows host memory rules.

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
