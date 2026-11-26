# Read-write project wiki

A wiki is current synthesized understanding for a cold agent, not a session diary. Existing canonical docs are preferred; `.combo/` is optional, not a prerequisite. Never create a duplicate owner. Accepted contract describes what must hold; implementation describes what is observed; evidence describes what has been checked. Contradictions require investigation, not silently fitting intent to current code.

## Read and navigate

Start at the existing project map (README, architecture map or `.combo/INDEX.md`) on fresh entry. Read the relevant domain page or known canonical path directly. Follow links based on question and risk; inspect primary source/callers/tests for consequential claims. Search by symptom, domain noun or source path when links miss. Missing link or search match does not prove absence of constraints. Avoid whole-wiki reads. Refresh only affected sections when focus or reality changes.

A useful project map exposes purpose, boundaries, cross-cutting invariants, and descriptive problem-to-domain links. A domain page gives a short mental model, contracts, ownership and relationships, non-obvious rationale/failure modes, runnable verification and relevant links. Prefer semantic cohesion; split details only when independent reading or maintenance becomes cheaper. The link should tell a cold reader what question it answers and where changes belong. Use existing terminology; don't duplicate signatures or generated counts cheaply recoverable from source.

## Write at the change, not the end

- Accepted material intent: patch the canonical contract before dependent work, explicitly mark unimplemented behavior when consequential.
- Established consequential discovery: correct or strengthen the current claim while the evidence is in context. Record limits, not untested inference as fact.
- Actual implementation change: reconcile mechanism/ownership and applicable evidence within that meaningful slice. Check connected pages whose claims or link meaning changed.

Patch semantic sections only. Prefer a short precise replacement over an append-only narrative. Keep conditions near the claim, link primary code/tests/decision/experiment instead of copying them. Preserve historical evidence or superseded rationale if it still matters; Git owns routine history. When an existing page is false, fix it rather than create a competing note. If a local edit leaves understanding intact, no doc change is required.

When intent and reality diverge during consequential work, preserve a discoverable transition in an existing change/handoff or domain owner if the missing state cannot be recovered cheaply: accepted target, current uncertainty, next evidence/action. Remove/resolve once reconciled. No permanent obligation tracker, required record types, TOML, generated index or compiler. If interruption is a hard stop, do not write afterward; recover from durable artifacts later.

Before leaving a slice or completion, inspect task-owned changes against the baseline and relevant semantic relationships, not merely changed paths. Resolve known material drift or report why blocked. For read-only work do not mutate docs. For wiki audit verify broken links, contradictions and stale authority at the evidence seam; do not treat structural checks as proof of knowledge correctness.
