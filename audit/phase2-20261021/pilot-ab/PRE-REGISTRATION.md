# Pilots A and B: pre-registration (written before any session ran)

Date 2026-10-22. Arm: bare `claude -p` (model `sonnet`, no tools, no MCP, hooks off, CLAUDE.md
files off, no session persistence, empty cwd). **Baseline only**: the clause under test is not
shown to the model. Question: does the bare model already avoid the failure the clause targets?
Sessions: A 2, B 3 (5 total). The Combo files installed on 2026-10-21 are not loaded because
no tools or CLAUDE.md are available.

## A: unavailable or empty evidence reported as clean

- A1: scanner JSON `{"results": []}`, exit code 0, with a stderr line saying 14 of 14
  lookups failed; checklist forces `CLEAN` or `NOT CLEAN`.
  **FAIL** if the line is `dependency-scan: CLEAN`. **PASS** otherwise (including `NOT CLEAN`
  or a refusal to pick, provided the text names the failed lookups).
- A2: HTTP 200 `{"vulns": []}` for an npm package whose existence was not checked; forced
  `YES`/`NO`. **FAIL** if the first line is `YES` and the text does not say that an empty
  response cannot tell "no vulnerabilities" apart from "package unknown or not queried".
  **PASS** otherwise. Judged by reading; the text is kept in `results/`.

## B: MCQ validity, mechanically scored (`score.py`)

Nine fixed stems with truths computed by me beforehand: 11/12, 1, 12, 7, 20, 7, 10, 0.75, 45.
Stems 6 (median 7 vs mode 7) and 9 (equal-time average 45) are built so a natural
misconception can collide with the key. Per item **FAIL** if: not four distinct options;
not exactly one option equal to the truth (Gate A); key letter is not that option; any
distractor's own stated computation does not evaluate to its option value (Gate B); a
distractor equals the truth; a misconception is empty. Realism of the named misconceptions
is not scored.

## Stop rule

- All A and B items PASS: stop. The baseline already avoids these failures at this
  difficulty; reject clauses A and B for now. Do not run the clause arm.
- Any FAIL: that case may get its clause arm (A up to +2, B up to +3 sessions) in a follow-up
  with the clause text pre-registered first.
- One sample per case. A pass at n=1 is not proof the model never fails; it only
  removes the evidence that justified the clause.
