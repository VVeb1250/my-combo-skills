# Routing probe after installing audit items 1, 3-8 (2026-10-21)

Install: `setup-claude.py plan` (8 Combo-owned files) -> `apply` -> `verify` OK; receipt
`backups/claude-20261020-192315-626800/receipt.json`. The updated `combo-investigate`
and `combo-review` descriptions were visible in the next session's skill list.

Rerun: 5 cases x 2 arms x 3 repeats (30 sessions, $0.86 reported), same model and
fixture as run 1. `pos-debug-en` is a control whose description did not change.

| case | policy (3 reps) | description-only, new (3 reps) | description-only, baseline (1 rep) |
| --- | --- | --- | --- |
| pos-review-en | 3/3 | 1/3 | miss |
| pos-investigate-en | 3/3 | 1/3 | miss |
| conf-investigate-research | 3/3 | **3/3** | miss |
| conf-security-review | 3/3 | 0/3 (one went to the built-in `security-review` skill) | miss |
| pos-debug-en (control) | 3/3 | 0/3 | miss |

## Reading [O/I]
- Policy arm: 15/15, stable. The routing paragraph keeps these routes reliable.
- Description-only: 5/12 on the four changed cases vs 0/4 baseline; the control stayed
  0/3, so the lift is unlikely to be pure noise but the baseline is a single sample.
- The clearest gain is `conf-investigate-research` (3/3), which matches the new
  "compare technical options ... about this codebase" wording. `combo-review` gained
  at most one of three on a plain review prompt; the security prompt competes with the
  built-in `security-review` skill, a native overlap rather than a wording defect.
- Descriptions alone still do not carry routing for review and debug prompts. That
  supports keeping the Skill-tool pointer (audit item 11) until an outcome comparison
  says otherwise.

Limits: 3 repeats, one model, one tiny fixture; routing, not answer quality.
