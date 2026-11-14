# Evidence for the intended outcome

Use for reference fidelity, rendered artifacts, or a completion signal that does
not establish the user's result. Select only applicable checks; a tiny edit can
need inspection alone. Keep the acceptance-to-evidence mapping in context unless
the deliverable needs a report. Native skills own concrete tool operations.

| Work | Evidence that can expose the mismatch |
| --- | --- |
| 3D/anime hair/Blender | Compare required rendered views and silhouette/volume against supplied reference at consistent framing. Scene validity does not prove visual fidelity. For conditional silhouette IoU and camera checks, see [optional tool validation](../references/addenda/conditional-tool-validation.md). |
| UX/UI from reference | Compare the current served revision with reference across relevant viewports and exercise meaningful states. A build or screenshot alone does not establish interaction. For optional generic-UI detectors, see [optional tool validation](../references/addenda/conditional-tool-validation.md). |
| Generated environments, procedural assets, game systems | Generate the actual integrated artifact from the current implementation. Inspect relevant scales, transitions/junctions and diverse fixed inputs/seeds, including a known failure and a contrasting case when available. Compare visible/spatial quality against the target and baseline; check domain behavior (e.g. vehicle mobility, LOS, counterplay) and performance when they are acceptance constraints. A valid graph, feature count, one favorable seed, or attractive render alone cannot prove the intended outcome. |
| Coding/debugging | Exercise behavior through real callers or the reproduced symptom; include affected contracts and rejection paths where material. Run required repository gates. A test mirroring implementation or a changed expected value cannot justify changing the contract. |
| Research | Trace consequential claims to direct sources and check applicability, contradictions, date, and inference. A completed search or several repetitions of one claim cannot establish correctness. |
| Writing/documents | Compare source facts, voice samples, audience, requested depth, and constraints with the delivered text. Render when pagination/layout matters. File creation or spellcheck cannot establish factual or stylistic fidelity. |

Before expensive browser/manual checks consider faithful headless/direct render
from the actual scene or generation pipeline. Batch independent seeds/views
and structural invariants when shared setup makes this cheaper. A separate
mock renderer does not establish product fidelity; real UI journeys still need
interactive verification when state transitions or persistence are acceptance.

Inspect the actual resulting artifact, not a cached preview, earlier revision, or
tool's claim that it saved successfully. When a check fails, preserve the symptom,
distinguish artifact, fixture, and environment causes, and make a causal repair
within scope. Recheck what the repair could change. Stop after acceptance passes;
broaden only for a new change, failure, uncovered criterion, or explicit coverage.
When tools or references are missing, state the gap and the next useful check.
Keep technical validation separate from human taste approval. For uncertain
quality, compare a bounded real candidate against the intended result before
expanding implementation. Use an alternative method or change the representation
when the evidence indicates a quality ceiling, not repeated cosmetic patches.
Keep failure examples and still-valid evidence. Report objective checks, observed
quality gaps, and any pending user judgment separately; an unverified or rejected
material quality criterion prevents an overall completion claim. Do not require
new user approval for routine, objectively verifiable work.

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
