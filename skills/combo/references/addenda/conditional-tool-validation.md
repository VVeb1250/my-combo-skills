# Optional tool-specific validation recipes

These examples are reference data. Read only the relevant section for an actual
rendered, browser or dependency-risk task. Generic acceptance, test selection,
and user/host authorization remain in the practices and selected workflow.

## Accessibility rule engine (axe-core)

- For an accessibility claim, a rule engine gives a signal that the browser's
  accessibility snapshot does not. If axe-core is already installed in the project (or at
  `~/.combo-tools/axe-core`), or installing it is authorized, run it on the rendered page and report `violations` as
  findings. Report `incomplete` as needs review, never as a pass. Run it in a viewport
  with a real size: at 0x0 it moved a genuinely failing contrast ratio into `incomplete`
  instead of `violations`. A clean run is not WCAG conformance, since automated rules
  cover only part of it: still check keyboard operation and labels on the affected controls.

## Dependency risk collector

- For dependency risk beyond known advisories (existence, publishers, install scripts,
  maintenance), a registry-metadata collector such as Trail of Bits'
  `supply-chain-risk-auditor` (pinned copy at `~/.combo-tools/supply-chain-risk-auditor`) reports each signal as assessed-clean, assessed-flagged, or
  unassessable and refuses to report when nothing could be measured. It calls registry
  and advisory hosts and reads the GitHub CLI token when `gh` is on PATH, so run it only
  with that authorized, or with `gh` absent. A package never confirmed to exist in its
  registry is unassessable even when an advisory lookup returns nothing.

## 3D/Blender reference checks

Inspect the reference's intended role. Compare relevant front, side, back, or three-quarter renders at comparable camera, scale, and lighting. Check silhouette, bang divisions, mass, volume, and occlusion as applicable; preserve approved pose, materials, and passing views. When the reference has a clean silhouette or matte and a fixed orthographic camera can match its framing, compute silhouette IoU and report the reference-only and model-only areas; aligning bounding boxes first hides scale and offset error, and a threshold is a working target to calibrate on known good and bad models, not a standard. IoU says nothing about style, material, or interior form. Scene validity, polygon count, and script exit status cannot establish resemblance. A single reference may leave hidden geometry genuinely undecided.

## UX/UI reference checks and Impeccable

Compare the served current revision with the reference at relevant viewports, then exercise the primary journey and meaningful states. Check hierarchy, spacing, crop, responsive behavior, and accessibility where affected. A build or screenshot alone cannot establish interaction correctness. Use the existing E2E practice for state transitions. If the Impeccable engine is installed (`~/.combo-tools/impeccable`), `impeccable detect <file> --json` with `DO_NOT_TRACK=1` is a free, repeatable pre-check for generic-UI patterns (exit 2 means findings); it adds repeatability, not detection a careful review misses, and rules such as `cream-palette` encode taste, so treat those as opinion.
