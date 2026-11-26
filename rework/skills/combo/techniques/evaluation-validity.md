# Evaluation validity

For comparing agents, models, algorithms or noisy outputs, name the decision, independent acceptance oracle, population/inputs and major confounders. Use a common baseline, comparable versions/settings/budgets, representative positive and negative cases, and repeated runs when variance matters. Isolate mutable state; Git worktrees isolate files but not necessarily runtime services. Alternate run order when environment drift could favor an arm.

Separate judge validity from candidate quality: demonstrate that the check accepts a known valid result and rejects a plausible invalid one. Do not give the subject hidden answers or tune the oracle to the winning implementation. For data-driven models check split integrity, duplicated samples and leakage from features or preprocessing. Compare quality at the relevant distribution and disclose failed/incomplete runs; do not reduce distinct acceptance dimensions to a flattering average.

Use existing native runners and measurements. Keep revision, inputs, settings and decisive artifacts for reproducibility, and record limits. Treat a small pilot as evidence about its tested conditions, not proof of general superiority.
