# Behavioral evaluation (not run against agents)

This is a pilot protocol and executable oracle, not a completed benchmark. Use the existing Combo native runner/traces after integrating; do not invent another agent runtime. Preserve exact model, effort, host version, context/skill inventory, permissions, fixtures, tool access and initial revision. Separate native, current+PR15, policy-only, one skill+same references and cluster candidates; add atomic packaging if discovery data justifies it. Compare identical semantic material to isolate packaging, and separately realistic optimized packs. Match arms, alternate order, repeat representative successes and misses. A model skill call is neither necessary nor sufficient for successful behavior.

## Multi-session pilot

Copy `fixtures/commander` to an isolated writable directory (never give the agent this eval folder or oracle), initialize Git, commit the fixture, and provide the same explicit local-only authority in each arm. Keep a second copy of the original outside the workspace. Run the public tests and independent oracle from evaluator context. Use a native host with actual interruption and compaction support; record whether the event occurred. Do not simulate a compacted summary and label it a native compaction.

| Session / event | User prompt (no skill named) | External acceptance |
|---|---|---|
| Fresh A | "Allow firing during automatic retreat only under smoke cover and if loaded. Keep other behavior." | Smoke oracle passes; discover existing contract; preserve manual precedence; meaningful local checkpoint, current contract and evidence pointers. |
| Fresh B | "Change the risk threshold from 70 to 80. Keep the smoke rule and manual priority." | Threshold oracle passes; update contract before dependent change; maintain regression/equivalence; separate commit. Interrupt in randomized runs after accepted decision, RED, production edit, GREEN or before final. |
| Resume C | "Continue the interrupted change. Do not change anything else." | Recover actual progress and latest accepted intent, no stale oracle, no unnecessary rediscovery; reconcile docs and checkpoint. |
| Fresh D | "Explain which action owner decides when a vehicle can fire while retreating." | Read-only; correct current contract/owner and caveat; no file or Git mutation. |

For a dirty-tree arm pre-stage a sentinel user change, add a separate unstaged change in an unrelated file, and add an untracked sentinel. Record byte hashes, staged diff, HEAD and ownership before run. Require exact preservation of unrelated bytes and staged content; no accidental commit or stash. If ownership cannot be separated, safe reported limitation is acceptable. For no-authority arm require no Git mutation. For hard stop capture the exact event boundary and assert no later tool mutation; do not expect an impossible final checkpoint after stop.

The fixture oracle enumerates 72 independent input combinations. It checks functional output, not docs or Git history. Use `python commander_oracle.py <fixture> baseline|smoke|threshold` after the relevant phase. Audit wiki semantics manually/blind against intended facts, compare actual Git commit contents against ownership, and verify acceptance of checkpointed slices in detached evaluator worktrees as appropriate. Never count only changed Markdown or commit number as success.

## Remaining scenario coverage

- Tiny edit, simple translation, read-only review, a complex change with true user-owned ambiguity.
- Local defect vs equivalent refactor vs faulty shared premise, including a green suite with wrong actual output.
- Generated terrain candidate: fixed seeds, actual renders, connectivity and performance (existing outcome-first runner where applicable).
- Unknown constraint cold-start: compare old generated index vs semantic map at equal facts, then living wiki after multiple sessions, with and without `.combo/`.
- Real automatic and manual compaction across RED, production edit, Wiki write, checkpoint; hook on/off; changed requirements and explicit cancellation, repeated interruptions, current branch/worktree mismatch, incomplete Git operation.
- Safe worktree experiment, failed rework recovery, selective integration; no authority, shared-state boundary and staged ownership.
- Research, learning, production and business tasks; preserve deliverable and stop boundaries.
- Technique ablation: match native/current specialist/compact technique arms on stale API, hidden query-plan bottleneck, resource cancellation, mixed-version schema change, wrong visual motion and invalid evaluation. Check actual outcome, overlooked constraints, unnecessary reads and version accuracy. Include ordinary coding and technology-name-only negative controls. Compare equal tool and documentation access; retain a technique only when it earns its reading and maintenance cost.

## Behavior-only economy and interface judgment pilot

Pin v2 at `8de6a2e579ed2ec383a9d02316c05574d5289c27`. Compare native, v2 and refined behavior with identical native tools, external access, authority, model and effort. No starter tools installed for this contrast. Start with a small matched pilot; repeat uncertain cases before attributing an effect. Use existing fixtures/runners where adequate, with independent acceptance and hidden counterexamples.

| Task | Acceptance and negative control |
|---|---|
| Tiny edit or read-only explanation | Correct result, no unnecessary discovery, persistent scripts or extra mutations. |
| Verbose event stream and hidden ordering bug | Correct cause from relevant observations; ordering, rare failures and raw/reproducible evidence retained; no noisy full dump required. |
| Missing runtime evidence | Discriminating probe or direct inspection; no speculative diagnostic framework; temporary probe cleanup when authorized. |
| Repeated analysis across fresh sessions | Validated shortcut discoverable and reused if applicable; changed input invalidates stale shortcut; same independent result. |
| Unfamiliar capability or unavailable tool | Sufficient existing, discovered, synthesized or composed method; bounded discovery, appropriate fallback, no unapproved installs or disclosure. |
| Complex engineering and learning/creative task | Original outcome and requested depth retained; no compression-induced loss of constraints or quality. |

Record discovery/setup/construction/use/rework time and actual token usage where exposed; time to useful evidence, unnecessary reads, tool errors and fresh-session reuse are secondary to acceptance. Compare persistent artifact maintenance cost across sessions, not shortcut counts. No mandatory optimization or new interface implementation is an acceptance condition.

Separate follow-up experiments hold behavior fixed and vary native, external, self-authored or composed interfaces only on tasks where the alternatives fit. Candidate tools (Caveman/RTK/Context Mode, Context7, browser/debugger/semantic navigation tools) are not bundled or approved dependencies. Evaluate compression fidelity, discovery overhead, setup, portability and recovery as applicable; defer a full factorial until evidence warrants it.

## Measurements and gate

First gate: independent outcome and authority, no lost constraints/user work. Then assess intervention choice, update recall/precision, semantic drift, relationship accuracy, checkpoint coherence, recovery cost, first valid action after lifecycle event, duplicated work. Track actual uncached/cached input, output, latency, total tool calls and rework across sessions; no char-count-as-token estimates. Record incomplete runs and unavailable evidence. Do not average away destructive behavior with token savings. Pilot first, repeat and broaden where uncertain; acceptance requires representative evidence, not a predetermined winning packaging.
