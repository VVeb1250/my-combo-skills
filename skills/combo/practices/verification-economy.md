# Evidence-efficient verification

Use only when deciding whether an additional expensive browser journey, broad test suite, external review, or other costly check is necessary. Acceptance and stopping rules belong to [context](context.md), test seams to [tests](tests.md), rendered/reference fidelity to [outcome evidence](outcome-evidence.md), and structural refactoring to [simplicity](simplicity.md). This practice is not a mandatory review stage.

Escalate when an acceptance criterion remains unobserved, a relevant input or boundary changed, a focused check failed, or an explicit user/repository gate requires it. Prefer the cheapest independent evidence capable of detecting the mismatch. Use Browser only for behavior or appearance that cheaper evidence cannot establish; follow native host rules.

Reuse still-valid results when relevant revision, code, inputs and environment are unchanged. Do not repeat a costly journey for subjective reassurance or treat a second model's agreement as independent proof. Preserve security and data-loss checks. Stop when the requested acceptance is covered, and report exactly what remains unverified if access is blocked.
