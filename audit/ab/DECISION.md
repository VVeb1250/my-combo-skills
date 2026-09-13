# Decision: ship a modular Combo workflow pack

Root selects **B**, twelve direct task entries sharing the same workflow and
reference library, plus the `combo` fallback router and `combo-maintain`.
This is a maintainability decision for the requested breadth, not a claim that
more skills always produce better answers or lower token cost.

## What was compared

The frozen experiment at `D:/combo-ab-evals/staged-20260909-202834` supplies the
same full source content to both arms. A exposes one broad router. B exposes
the router plus twelve narrow workflow entries. The routing paragraph in the
fixture's AGENTS.md matches its arm; prompts do not name skills. Both arms use
Luna Max, the same user preferences and native utilities, two concurrent
sessions at most, and alternating first arms. Initial budgets were 180 seconds
for bug-zero and 240 seconds for the other cases.

Actual app-server discovery confirms one repo Combo entry in A and thirteen in
B. Global Combo is disabled in both experimental processes. Unrelated skill
metadata matches. This tests implicit selection under the configured routing
policy, not description-only discovery without that policy.

## Root review of the initial ten matched cases

| Case | A | B | Interpretation |
| --- | --- | --- | --- |
| Zero parser regression | Pass | Pass | Independent acceptance fails before and passes after; scope preserved |
| Iterable inventory feature | Pass | Pass | Generator, flag, stock rule, and return shape preserved |
| Security review only | Pass | Pass | Both identify ownership bypass and zero-value defect without repairs |
| Plan around two adapters | Deadline incomplete | Deadline incomplete | Both inspect the seam; neither delivers a final plan within 240 seconds |
| Tiny button label | Pass | Pass, extra entry reads | A uses no skill instructions; B reads two entry files, with no full workflow ceremony |
| One-sentence translation | Pass | Pass | Correct Thai answer, zero tools in both |
| Thai diagnosis only | Pass | Pass | Cause and repair plan provided; source remains unchanged |
| Thai complete delivery | Implementation passes, scope violation and deadline incomplete | Pass | A's acceptance passes, but it also reformats a library example and never sends a completed final answer |
| Repurpose product content | Pass | Pass | All source facts retained across three distinct formats, no publication |
| Bounded DI lesson | Pass | Usable, minor typing issue | Both explain DI and give practice; B passes FakeGateway to a concrete PaymentGateway annotation, valid at runtime but inconsistent for static typing |

These judgments inspect final responses, independent acceptance, tool records,
and file changes. They supersede automatic keyword classifications where those
classifications are wrong. In particular, B's security and content cases were
flagged for `2>$null`, which discards stderr and does not write a file. Their
file hashes did not change. The original raw classifications remain preserved.

A's initial Thai delivery also changed the local fixture copy of
`combo/references/library/ecc/skills/manim-video/assets/network_graph_scene.py`.
The before/after hash comparison confirms an actual out-of-scope modification,
not a generated cache file. The frozen staged source and the installed package
were unaffected. `final-evidence.json` records the path and the follow-up results.

The evaluator's `final-answer.txt` can contain the last progress message after
a timeout. That text is not accepted as a completed final answer. A timeout is
recorded as a deadline result, not automatically excused as an environment fault.

## Cost and tradeoffs

For the eight initial cases where both arms completed, reported uncached input
totals are **A 214,099** and **B 236,597** tokens, about 10.5% more for B. These
are observed cached/uncached usage counters, not a dollar invoice or a stable
architecture effect. Cache state, repeated context, and runtime variance matter.
Timeout arms lack complete usage reports and are not silently counted as zero.
Detailed latency, output tokens, and deduplicated calls are in `metrics.md`.

A is attractive for a narrower engineering setup and has a cheaper discovery
surface. B makes teaching, content, operations, media, and research visible as
distinct intents, supports explicit invocation by domain, and keeps changes to
each entry local while retaining one shared body of knowledge. The expanded
owner requirement makes that organization worth its metadata overhead. There
is no reason to squeeze all source procedures into one always-loaded SKILL.md.

## Shipping corrections and evidence limits

The shipping package keeps the tested workflow bodies and entry descriptions.
It adds explicit `allow_implicit_invocation: true` metadata to the twelve direct
entries; the tested entries used Codex's implicit-invocation default and were
verified as discoverable. Source packaging fixes the pinned Remotion chart
example's misspelled path, marks ECC-Tools as an external workspace reference,
and resolves existing asset links before treating a path as an example.
The frozen test copy is unchanged; these packaging corrections do not rewrite
the benchmark history. All navigable package links are checked. Markdown code
examples are not mistaken for installed-file links.

All 330 direct upstream source entries are retained with source commits and
labels. That is reference coverage, not 330 independently tested integrations.
Most source bodies are metadata-classified; selected procedures are distilled
into the active workflows and specialist notes. Native tools, credentials, and
user authorization still determine which operations are available at task time.

This is a small, one-model, synthetic comparison. Research, business, media,
productivity, and the long tail of specialists have source and routing checks,
but are not each covered by a live outcome case here. Other models can use the
same portable files; this experiment does not establish their trigger rates.
Repo-local skill copies also expose reference code to broad native quality
checks; those checks can add noise absent when the pack is installed globally.

## Diagnostic follow-up

Two matched cases were repeated with a 600-second limit in `diagnostic-repeat`.
They remain separate from the original results:

- Plan-adapters: A completed in 297.099 seconds and B in 360.200. Both preserve
  the existing adapter protocol, propose bounded retry with injectable waiting,
  specify meaningful tests, acknowledge duplicate-delivery risk, and make no
  file changes. A's proposal is simpler; B adds a separate policy/error contract.
- Thai-delivery: B completed in 265.054 seconds, with independent acceptance
  and scoped quality checks passing. A's code also passed independent acceptance,
  but the session failed at 272.670 seconds with an explicit account usage-limit
  error before a final answer. That follow-up failure is environmental evidence,
  not a second architecture failure. Its code and tests stayed in scope.

There were 24 model sessions in this matched comparison and diagnostic follow-up.
Earlier exploratory/runtime probes are separate and excluded from these counts.
No further model run is needed to make the bounded installation decision.

## Actual installation

Installed and verified on 2026-09-10 JST. Receipt:
`backups/20260909-163949-897900/receipt.json` (timestamp is UTC).
The source package has 649 files across fourteen entries. Installation changed
571 paths; rollback using that actual receipt passed on copies for all 571.
App-server discovery exposes all fourteen selected Combo entries and preserves
unrelated skill metadata. Preferences and M2D text outside the Combo block are
byte-identical; non-owned config is semantically identical and the main model
is unchanged. Evidence: `installation-verification.json` and `preservation.json`.

The CLI's 23 experiment-owned project trust records were removed with a backup
and an unrelated-config check (`trust-cleanup.json`). One existing usage-reset
credit was consumed with explicit owner authorization; the other was not used.
