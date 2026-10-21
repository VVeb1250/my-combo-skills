# Inline-workflow cost experiment: pre-registration (written before any session ran)

Date 2026-10-22. Owner approved ("ทำให้หน่อย"); session count and cost stated first: 2 smoke + 24 main
= 26 sessions, about $5 Sonnet plus up to about $3 advisor (Opus), reported not invoiced.

## Question
Does putting a workflow's text and `context.md` inside the entry skill (no separate Read calls) reduce
the cost of a workflow load, with the same text in context?

## Arms (same model `sonnet`, same CLAUDE.md, same installed Combo for everything else)
- `full`: the installed entry skills (stub, then Read workflow, then Read context.md).
- `inline`: `scripts/run-outcome-compare.py` arm; plugin `combo-lab` supplies `combo-debug`, `combo-deliver`,
  `combo-plan`, `combo-review` with identical descriptions and the workflow plus `context.md` text in the body;
  the four original entries are switched off with `skillOverrides`. Practices other than `context.md` stay lazy.

## Cases
bug-zero (debug), inventory-feature (deliver), plan-adapters (plan), security-review (review); 3 repeats.

## Smoke test (2 sessions: bug-zero and security-review, inline arm, 1 repeat)
Pass only if all hold: the Skill call is `combo-lab:...` (not the switched-off original); no Read of a file under
`skills/combo` workflows/ or practices/context.md; the run finishes. Fail twice after one fix: stop.

## Prediction
Per loaded run the inline arm makes about 2 fewer calls and saves about $0.015 of Sonnet cost (2 re-reads of a
~36k-token context at $0.20/Mtok); pass rates equal. Cost is noisy at n=3 per cell.

## Reading rules
- Structural result (Reads of Combo files, calls per run) is deterministic and reported first.
- Cost: paired by case, Sonnet-only from `modelUsage` (advisor spend reported separately); claim a cost effect only
  if the per-case differences all point the same way; otherwise report it as a lead.
- Quality: pass rate per arm from the harness scorer; any drop is reported even if cost improves.
