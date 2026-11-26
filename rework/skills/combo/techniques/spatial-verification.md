# Spatial verification

For geometry, rigs and motion, pair visual evidence with structured state from the actual tool/runtime. Identify coordinate systems, units, local/world transforms, hierarchy, orientation and bounds. For animated characters inspect rest/pose axes, constraints and sample frames where contact, rotation, deformation or retargeting can fail. Compare measured contact and facing to the intended ground/pose, not just the apparent silhouette. Use native inspection/export or an existing script before writing a custom tool.

For generated environments inspect authoritative geometry, connected features, reachability and relevant interactions (e.g. traversal or occlusion), plus actual renders at meaningful scales. Use known failure, contrasting and representative seeded cases. Distinguish invalid representation from a rendering or camera artifact. A valid mesh/graph or attractive image alone cannot establish domain behavior.

Compare against the user's actual references and constraints, preserve framing/settings for fair comparisons, and separate objective discrepancies from taste. Report unavailable structured/visual evidence rather than inferring a pass.
