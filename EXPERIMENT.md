# One entrypoint versus a skill pack

Status: completed, with candidate B selected and installed. See
[the decision](audit/ab/DECISION.md) for the original twenty sessions, four
diagnostic follow-ups, semantic grading, costs, and installation evidence.
The engineering baseline was expanded in both staged candidates. This experiment
supersedes the single-entry constraint in DESIGN.md while preserving its behavior,
scope, provenance, and rollback requirements.

## Question

Does one automatic task entrypoint work better than a modular pack with
direct workflow entrypoints and a router for cross-workflow requests?

Separate two questions: discovery granularity, and source capability coverage.
Do not let a smaller candidate appear efficient because it lost requirements or
useful capabilities. Audit omitted capabilities from all four upstream packs
separately. The owner confirmed that noncoding capabilities are included too.

## Candidates

**A: single entrypoint.** Extend the existing combo router with the agreed
noncoding capability routes. Keep its six engineering workflows, eight practices,
and specialist shelf. Both arms receive the same broader source library and
noncoding workflows before comparison. This is a package of multiple files,
not one giant prompt.

**B: modular pack.** Keep the same source content. Add six concise discoverable
entries: combo-deliver, combo-debug, combo-plan, combo-review, combo-verify, and
combo-investigate. Each points directly to its existing workflow in a sibling
combo package. Retain combo as the fallback router for uncertain or cross-workflow
requests and explicit invocation. Add direct noncoding entries matching the
agreed capability groups. Do not duplicate or rewrite workflow bodies or the
reference shelf between arms.

Both candidates retain identical Karpathy/Ponytail policy, native utilities,
user preferences, model, reasoning effort, permissions, memory exclusions, and
fixture content. The task discovery pointer must match the candidate:
A reads combo; B selects the narrow matching Combo entry or falls back to combo.
This pointer is part of the treatment and must be recorded.

Stage variants in isolated evaluation workspaces, with repo-local AGENTS guidance
overriding only the global Combo routing paragraph. Disable the globally installed
combo entry by exact path through per-process configuration, retaining all other
existing visibility overrides. Local copies provide candidate A or B. Do not
modify global skills, auth, memory, or the currently installed package to switch
arms. Preserve original fixture prompts without skill names. Per-process config
selects the arm. The Windows CLI was observed adding temporary project-trust
records to global config despite the process override. These are bookkeeping,
not treatment differences; remove only the exact experiment-owned trust records
after testing, with a backup and unrelated-setting preservation check.

## First comparison

Use gpt-5.6-luna at max effort for both arms, at most two concurrent sessions,
and a bounded per-session timeout. First run ten matched cases per arm:

Interleave the arms by case, alternating which arm starts first. Preserve prompt
and fixture hashes. Do not compare a cold all-A batch with a warm all-B batch and
attribute cache or time-of-run effects to architecture.

1. Repair zero-versus-missing bug, preserve None default.
2. Add inventory iterable/flag behavior, preserving result and stock rules.
3. Security/correctness review only, find seeded ownership and zero defects.
4. Plan a gateway using two existing adapters without implementing it.
5. Change a button label without unnecessary workflow or specialist loading.
6. Translate a noncoding sentence without engineering tools.
7. Thai mixed-intent request mentioning a bug and a repair but explicitly asking
   for diagnosis and a repair plan only; inspect a seeded defect, make no edits.
8. Thai complete-delivery request asking for a plan, implementation, and checking
   together; preserve the complete authorized task instead of stopping at a plan.
9. Repurpose a supplied product brief into distinct platform-appropriate content,
   retaining its facts and voice without invented claims or publication.
10. Teach a bounded concept using the supplied learner context, a worked example,
    and retrieval practice; do not turn a one-lesson request into unsolicited
    persistent learning infrastructure or global personal-memory writes.

Reuse existing fixture and immutable acceptance tests where they cover the actual
behavior. Independent tests must demonstrate the seeded failure before a repair
and pass afterward. Review and planning need semantic inspection of the actual
answer, cited code, and changed-file hashes. Do not grade solely by English words
or a claimed routing label. Relevant new regression tests are allowed within the
fixture's tests directory; unrelated changes are not.

The original six-case run interrupted by usage limits is environmental evidence,
not candidate failure. Resumed live-install checks are a smoke baseline, not a
substitute for the matched experiment. Preserve all prior attempts.

If a shared shell/runtime failure affects either arm, fix the isolated test
invocation consistently for both and disclose the accommodation. An environment
note may identify a working shell, but must not mention expected skills/routes.
Do not score access, usage, or harness failures as model architecture failures.

## Evidence and decision

Record outcome, requested stopping-point compliance, requirement coverage,
unrelated changes, actual source/workflow reads, extra process steps, latency,
and reported usage. Distinguish total input from cached input. Count catalog
description bytes and actually loaded instructions separately; neither equals
total billed tokens. Capture real discovery for each staged arm before runs.

Root owns semantic grading and the recommendation. Treat automatic text/path
checks as supporting evidence, not ground truth. Compare paired outcomes first,
then unnecessary work and context cost. A small one-model sample cannot establish
all-model reliability or statistical superiority. Repeat only cases with an
unresolved behavior difference or harness ambiguity, and report repetitions.

Choose the structure that preserves the desired capabilities and works best in
the observed tasks. If behavioral evidence is tied, prefer the more maintainable
layout for the clarified capability scope and state that the choice is an
engineering judgment. Update the actual installation, documentation, provenance,
and rollback only after the selected candidate is concrete and validated.
