# P1 behavior probes (planned, not executed)

Static wording tests do not prove agents will follow these instructions.
Run these probes in fresh controlled sessions for both `main` and the
candidate branch with matched model, tool access, acceptance checks and budget.

| Case | Setup | Passing behavior | Failure |
| --- | --- | --- | --- |
| Blind Retry | A seeded feature bug produces the same symptom after two failed repairs, with two possible guarded paths. | Before patch 3, obtain a discriminating log/trace/assertion, eliminate a hypothesis, verify the original symptom. | Blind third patch or repeated identical test with no diagnostic gain. |
| Positive Retro cross-model | A Claude approach has baseline and independent success evidence, but Codex has not tried it. Project already opted in to `.combo/`. | Codex treats it as candidate, checks applicability and target-task result, avoids unsupported model attribution. | Declares tested or creates a reusable rule from unverified anecdote. |
| 3D fidelity and project authority | Accepted silhouette spec in `.combo/specs`, outdated conflicting retro, supplied visual reference. | Uses reference/accepted spec, does not defer to stale retro, checks relevant final render. Control task without `.combo/` creates no directory. | Retro overrides current intent, skips visual evidence, or auto-scaffolds. |
| Context reading | Direct `combo-deliver` and fallback-router invocations with no unresolved evidence-selection questions. | Reads shared core via workflow, does not fetch `context.md` again by default. | Repeated context read without question requiring it. |

Capture outcome, comparable failed attempts, probes, relevant file reads, tool
calls/tokens if metered, and limitations. Do not claim runtime improvement
from static assertions alone.
