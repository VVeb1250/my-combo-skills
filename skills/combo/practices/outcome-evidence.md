# Evidence for the intended outcome

Use for reference fidelity, rendered artifacts, or a completion signal that does
not establish the user's result. Select only applicable checks; a tiny edit can
need inspection alone. Keep the acceptance-to-evidence mapping in context unless
the deliverable needs a report. Native skills own concrete tool operations.

| Work | Evidence that can expose the mismatch |
| --- | --- |
| 3D/anime hair/Blender | Inspect the reference's intended role. Compare relevant front, side, back, or three-quarter renders at comparable camera, scale, and lighting. Check silhouette, bang divisions, mass, volume, and occlusion as applicable; preserve approved pose, materials, and passing views. Scene validity, polygon count, and script exit status cannot establish resemblance. A single reference may leave hidden geometry genuinely undecided. |
| UX/UI from reference | Compare the served current revision with the reference at relevant viewports, then exercise the primary journey and meaningful states. Check hierarchy, spacing, crop, responsive behavior, and accessibility where affected. A build or screenshot alone cannot establish interaction correctness. Use the existing E2E practice for state transitions. |
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
