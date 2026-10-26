# Combo maintenance contract (shared across hosts)

Use for requested Combo audits, rule simplification, skill improvements, routing
changes, and package updates. Not for routine task execution. Inspection-only
may stop with findings; do not require an install plan or a model benchmark.

## Diagnose before changing behavior

- Start with the actual task, user intent and stopping point, the failing action,
  observed result, and evidence for any implicated instruction. Separate a real
  implementation defect, environment failure, host/tool behavior, and a reusable
  Combo instruction gap. A failed task alone does not prove a skill caused it.
- Use existing evals, task traces, and documentation before inventing a new
  harness. For a purely structural defect (broken link, host drift, duplicate
  owner), a focused static check may be enough.
- Evaluate a proposed rule by its expected change to accepted task outcomes, not
  by how persuasive it sounds, how many skills were read, or how many steps run.

## One owner, conditional use

- `context.md` owns intent, stopping point, and acceptance/evidence sufficiency.
- The selected workflow owns task-specific actions and authorization boundary.
- `tests.md` owns technical test seams and appropriate functional checks.
- `outcome-evidence.md` owns outcome comparisons where a build, command, or
  saved file cannot show fidelity (for example rendered UI or 3D references).
- `verification-economy.md` owns escalation to an additional expensive browser,
  broad check, or reviewer pass when a consequential criterion is still uncovered.
- `simplicity.md` owns structural complexity and justified refactoring.
- `project-ecosystem.md` owns optional project-local records. Neither a
  maintained package nor an installed skill calls for a per-task knowledge record.

References and checks are choices, not a sequence of mandatory review stages.
Keep existing verified coverage, explicit repository/user gates, security and
data-loss boundaries. Do not merge away a distinct permission or stopping point.
Keep the current entrypoint count unchanged unless a separate routing decision
and compatible host manifest change is authorized.

## Validate, report, and release

1. Make the smallest causal change to the canonical owner; avoid duplicating
   the rule in host overrides, workflows, and project records. Respect generated
   files and existing user edits.
2. Check relevant links, manifest/source mappings, generated content, and
   existing static tests. Use one bounded behavioral reproduction for a
   consequential behavior change when feasible; no universal per-rule A/B,
   automatic reviewer fanout, or new global gate.
3. Label outcomes precisely: `structurally-verified`, `behavior-observed`, or
   `behavior-unverified`. A clean install or test suite cannot establish
   better future task quality. If comparative benefit matters and is unknown,
   record the open hypothesis instead of claiming improvement.
4. For installation, use the invoking host's plan, apply, verify, receipt, and
   drift-aware rollback procedure. Never change another host's preferences,
   hooks, credentials, model, or memory through a Combo maintenance shortcut.
