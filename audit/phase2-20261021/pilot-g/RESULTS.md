# Pilot G: py-fsrs scheduling, 2026-10-22

`open-spaced-repetition/py-fsrs` @ `9446cb06605c597a063aeee49f7d188d42e34dc2` (MIT, version 6.3.2).
Installed into a scratch venv from PyPI with `--only-binary :all:` (`fsrs` 6.3.2, `pytest`,
`typing_extensions`). 0 model sessions.

- The repo's own `tests/test_basic.py` (read first: imports only `fsrs`, stdlib, pytest; no
  network or file writes) ran against the installed wheel: **42 passed** [O].
- All-"Good" reviews on a new card at the due time, fuzzing off, desired retention 0.9: step
  gaps 0.007 d (learning step), 2, 11, 46, 163, 498, 1348 days. This matches the history the
  repo's test asserts (0, 2, 11, 46, 163, 498) [O].
- Independent check: at desired retention 0.9 the interval should equal the stability.
  A review-state card shows stability 497.877 d, interval 498.000 d (whole days), and
  retrievability 0.9997 one day after the review [O].
- `Scheduler(enable_fuzzing=False)` gave identical results twice; the default `Scheduler()`
  has fuzzing **on**, so schedules vary unless it is turned off [O].
- Defaults are the 21 published FSRS-6 parameters (decay 0.1542), not fitted to a learner [O].

Integration: one sentence in `workflows/learning.md` (compute due dates with a scheduling
library instead of estimating; fuzzing off; defaults are population parameters). No install
into Combo and no dependency.
