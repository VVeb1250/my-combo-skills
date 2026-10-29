# Evidence for the intended outcome

Use for reference fidelity, rendered artifacts, or a completion signal that does
not establish the user's result. Select only applicable checks; a tiny edit can
need inspection alone. Keep the acceptance-to-evidence mapping in context unless
the deliverable needs a report. Native skills own concrete tool operations.

| Work | Evidence that can expose the mismatch |
| --- | --- |
| 3D/anime hair/Blender | Compare required rendered views and silhouette/volume against supplied reference at consistent framing. Scene validity does not prove visual fidelity. For conditional silhouette IoU and camera checks, see [optional tool validation](../references/addenda/conditional-tool-validation.md). |
| UX/UI from reference | Compare the current served revision with reference across relevant viewports and exercise meaningful states. A build or screenshot alone does not establish interaction. For optional generic-UI detectors, see [optional tool validation](../references/addenda/conditional-tool-validation.md). |
| Coding/debugging | Exercise behavior through real callers or the reproduced symptom; include affected contracts and rejection paths where material. Run required repository gates. A test mirroring implementation or a changed expected value cannot justify changing the contract. |
| Research | Trace consequential claims to direct sources and check applicability, contradictions, date, and inference. A completed search or several repetitions of one claim cannot establish correctness. |
| Writing/documents | Compare source facts, voice samples, audience, requested depth, and constraints with the delivered text. Render when pagination/layout matters. File creation or spellcheck cannot establish factual or stylistic fidelity. |

Inspect the actual resulting artifact, not a cached preview, earlier revision, or
tool's claim that it saved successfully. When a check fails, preserve the symptom,
distinguish artifact, fixture, and environment causes, and make a causal repair
within scope. Recheck what the repair could change. Stop after acceptance passes;
broaden only for a new change, failure, uncovered criterion, or explicit coverage.
When tools or references are missing, state the gap and the next useful check.
Keep technical validation separate from human taste approval.

## Mechanical gates

Prefer an existing project test/CI gate for machine-checkable invariants. A
reference hash, output freshness check, or independent behavioral acceptance can
reject stale/missing evidence and spec drift; it cannot certify taste or semantic
truth. Keep acceptance outside the implementation being evaluated where practical.
Treat self-reported checklists as claims requiring evidence.

Consider a task-scoped gate only when its input, failure condition, recovery, and
host support are concrete. Hooks follow the host's ownership, trust, and explicit
authorization rules. Do not install a global stop/retry loop as part of ordinary
work. The default is the bounded comparison above, not a new service or ledger.
