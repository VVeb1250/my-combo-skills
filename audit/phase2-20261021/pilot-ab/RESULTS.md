# Pilots A and B: results, 2026-10-22

Criteria were fixed in [PRE-REGISTRATION.md](PRE-REGISTRATION.md) before any session ran.
Arm: bare `claude -p`, model `sonnet`, no tools/MCP/hooks/CLAUDE.md, one sample per case.
Raw outputs: `results/*.json`. Re-score offline: `py score.py A1 A2 B1 B2 B3`.

| Case | What it tests | Verdict |
| --- | --- | --- |
| A1 | scan with `{"results": []}`, exit 0, 14 of 14 lookups failed; forced CLEAN/NOT CLEAN | **PASS**: `NOT CLEAN`, names the failed lookups, says to re-run |
| A2 | HTTP 200 `{"vulns": []}` for an unverified npm package; forced YES/NO | **PASS**: `NO`, says empty could mean unknown package or uncovered ecosystem, notes existence was not checked |
| B1 | stems 1-3 (fractions, percent change, rate) | **PASS** 3/3 items |
| B2 | stems 4-6 (equation, perimeter, median with a mode collision trap) | **PASS** 3/3; on stem 6 it chose mean, range and midrange, avoiding the mode (7) collision |
| B3 | stems 7-9 (percent sum, decimal, equal-time average) | **PASS** 3/3 |

Sessions: 5. Reported cost (not an invoice): A1 $0.0145, A2 $0.0145, B1 $0.0366,
B2 $0.0329, B3 $0.0413, total about $0.14.

Scorer sanity check: a copy of the B2 stem-6 item with one distractor forced to equal the
truth and another with a wrong computation scored FAIL on Gate A, Gate B, duplicates and
"distractor equals truth", so the all-PASS result is not an artifact of a lenient scorer.

## Decision under the pre-registered stop rule

All items passed, so **stop; do not run the clause arm**. At this difficulty the bare model
already avoids both failures:

- It does not report a failed or empty scan as clean, even when the format forces a binary.
- It writes numerically valid MCQ items in which exactly one option is correct and every
  distractor follows from its own stated misconception.

Consequences: clause A (unavailable is not clean) and clause B (MCQ gates) have **no
supporting evidence** and are rejected for now rather than adopted. Both stay available as
Pilot items only if a real failure turns up in an actual session.

## Limits

- n=1 per case; a pass removes the evidence for the clause, it does not prove the model
  never fails.
- A tested one wording each; a more buried or longer evidence trail could still fool it.
- B items were numeric with fixed stems and a mechanical Gate A/B check. Verbal items
  (reading, science) where "one defensible answer" is semantic were not tested, and the
  realism of the named misconceptions was not scored.
- Bare model only. The Combo workflows were not loaded, so this says nothing about whether
  Combo changes behavior on these tasks.
- Consistent with Phase 1: a ceiling effect on current models for tasks of this difficulty.
