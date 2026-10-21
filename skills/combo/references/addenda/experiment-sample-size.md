# Experiment sample size

Use this note when a decision rests on an A/B or controlled test of a rate (conversion,
click-through, retention) and the question is how many observations are needed or whether
a finished test is big enough. Compute the number; do not quote a table from memory or from
a skill. Published tables disagree with the formula and with each other.

**Fixed-horizon, two groups, two-sided test of a rate.** With baseline rate `p1`, target rate
`p2 = p1 * (1 + relative lift)`, significance `alpha`, and power `1 - beta`:

    n per group = (z(1 - alpha/2) + z(1 - beta))^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2

For `alpha = 0.05` and power 0.80, exact normal quantiles give a squared z-sum of 7.8489
(rounding the z-scores to 1.96 and 0.84 gives 7.84 and results about 0.1% lower).
Computed with exact quantiles, rounded up:

| Baseline | Relative lift | n per group |
| ---: | ---: | ---: |
| 5% | 10% (5% to 5.5%) | 31,231 |
| 1% | 10% (1% to 1.1%) | 163,092 |
| 10% | 10% (10% to 11%) | 14,749 |

Run the formula in code (any language, exact quantiles such as Python's
`statistics.NormalDist().inv_cdf`) and print the inputs with the result. Check your own run
against the rows above when the inputs match.

- State `alpha`, power, the minimum detectable effect, the baseline and where it came from,
  and whether the test is one- or two-sided. A baseline guessed without data is an
  assumption, not an input; say so.
- Duration is `n * groups / (daily eligible traffic * share exposed)`. Compare it with the
  period the baseline was measured over: weekly cycles need whole weeks.
- Name one primary metric before the test. Secondary metrics are descriptive, and each
  extra tested comparison raises the false-positive rate unless the test corrects for it.
  Add guardrail metrics (latency, errors, unsubscribes, refunds) with a harm threshold.
- This formula assumes one analysis at the planned sample size. Checking results
  repeatedly and stopping at the first significant result inflates false positives; use a
  sequential method designed for it, or fix the horizon and do not decide earlier.
- A continuous metric needs its standard deviation: in the formula above, replace
  `p1(1-p1) + p2(1-p2)` with `2 * sigma^2` and `(p2 - p1)^2` with the squared difference in
  means, and keep the squared z-sum.
- The formula is an approximation. For very small counts, rates near 0 or 1, clustered
  units (users with many sessions), or ratio metrics, say the approximation is weak and
  use a method suited to the design.

Source: the standard normal-approximation sample-size formula for two proportions. The
values above were computed by Combo with it on 2026-10-21; they are not copied from any
skill. Written to replace lookup tables that disagree: the two files of one third-party
marketing skill (`coreyhaines31/marketingskills`, `ab-testing`, read 2026-10-21) give
150,000 and 380,000 per group for 1% to 1.1%, against 163,092 from the formula.
