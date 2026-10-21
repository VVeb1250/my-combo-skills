# Pilots C, D, E, F and the hunt: results, 2026-10-22

Owner approved running all pilots. Everything ran in the session scratch directory outside the
repo; only fixtures and outputs are kept here. Downloaded code was read before running; no
global install, no hooks, no config changes. Tags: **[O]** observed in this phase, **[I]**
inference.

## C. axe-core 4.14.0 (npm, MPL-2.0, `--ignore-scripts`), local fixture, built-in browser

Fixture `c-axe/page.html`: image without alt, empty button, text on a gradient, grey (#777) on
white paragraph (4.47:1, fails AA).

| Viewport | violations | incomplete |
| --- | --- | --- |
| pane default, `innerWidth` and `innerHeight` both 0 | `button-name`, `image-alt` | `color-contrast` on **h1, div and the failing p**, "Unable to determine contrast ratio" |
| 1280x800 | `button-name`, `color-contrast` (p, 4.47), `image-alt` | `color-contrast` on the gradient div only (`bgGradient`) |

Findings [O]: the tool works as documented and the documented meaning of `incomplete` holds.
New: at a zero-size viewport a genuinely failing text landed in `incomplete`, so a result
read as "2 violations, rest fine" would have missed it. The clause in `practices/e2e.md` now
says to run at a real viewport. Cost: 0 model sessions.

## D. Impeccable engine 0.1.16, Windows binary

Provenance checked before running [O]: SHA-256 equal in the sidecar, the release API digest
and the downloaded file (`c7dfa884...ccff2`); Authenticode `Valid`, signer
"Renaissance Geek, Inc." (the publisher the README names for its VS Code extension),
Microsoft ID Verified CA, Microsoft time-stamp. The release targets `main`, not the audited
SHA `dad8dbb`, so the binary may differ from the source I read. Run with `DO_NOT_TRACK=1`,
`detect` only, file targets, no browser engine.

| Fixture | Detector | Bare LLM review (1 session, $0.06) |
| --- | --- | --- |
| `sloppy.html`: 6 planted patterns | all 6 found plus Inter and two contrast failures: side-tab, gradient-text, low-contrast (3.4:1, 4.0:1), dark-glow, 9px text, overused-font, ai-color-palette, marketing-buzzword; some findings duplicated across engines | found all of them with the same contrast numbers (3.4:1, 4.0:1), plus things the detector does not check: viewport meta, copy quality, layout, missing CTA, em-dash cadence |
| `clean.html`: plain invoice table | **1 finding**, exit 2: `cream-palette` on my deliberately warm background | n/a |

Findings [O]: the detector runs, is deterministic, free, and fast; it found nothing the LLM
review missed on this fixture, and it flagged a legitimate design choice as slop
(taste-encoded rule, exit code 2 would fail automation). Benefit is repeatability and cost,
not extra detection. n=1 fixture, n=1 review.

## E. Trail of Bits supply-chain-risk-auditor @ a3131740 (CC BY-SA 4.0), run unmodified

Read before running [O]: all four modules grepped for dangerous constructs; the only
subprocess calls are `gh auth token` and optional `pip-audit`; stdlib imports only. Run with
`gh` removed from `PATH`, fixture lockfile with 3 direct dependencies, pre-registered in
`e-supply-chain/pilot-e-PREREG.md`.

| Expectation | Observed |
| --- | --- |
| `minimist@1.2.0` flagged | yes: `advisories: assessed_flagged`, 2 advisories (GHSA-vh95-rmgr-6w4m, GHSA-xvch-5gv4-984h) |
| nonexistent package not reported clean | yes: `advisories: unassessable` with the reason that an empty answer cannot distinguish "no advisories" from "unknown package"; all 13 signals unassessable |
| no clean without a datum | yes in every row inspected |
| `gh` absent noted | yes: "gh is not authenticated ... repository signals may be unassessable" |
| offline run with an empty cache refuses | yes: "this run measured nothing; every source was unavailable" |

Quirks [O]: a Scorecard Code-Review score of 1/10 is labelled `assessed_clean`; "no security
policy found" is labelled `assessed_clean`; an archived repo is `assessed_flagged`. The tri-state
guards against missing data, not against weak signals. Windows cache ownership is reported as
unverified in the notes, as documented. The token concern from the read-only check is
unchanged: urllib forwards `Authorization` on any redirect; nothing was sent because `gh` was
absent. The host's `osv-scanner` covers advisories only; this adds existence, publisher,
install-script, provenance and repository-health signals. Cost: 0 model sessions.

## F. Routing probe, 4 run-1 policy misses, 2 repeats each, 8 sessions, $0.18

| Case | run 1 | repeat 1 | repeat 2 |
| --- | --- | --- | --- |
| conf-review-verify | miss | combo-review | combo-review |
| conf-plan-deliver | miss | combo-deliver | combo-deliver |
| pos-productivity-en | miss (`agent-handoff-spec`) | same | same |
| conf-debug-investigate | miss (none) | none | none |

Two misses were noise; two are stable. The productivity miss is a native overlap with the
owner's own `agent-handoff-spec` skill, not a Combo wording defect. `conf-debug-investigate`
is a confusable prompt where loading nothing may be acceptable; not changed. n=3 per case.

## Hunt: areas not searched in the first pass (3 Haiku readers, read-only)

All three reports are leads, not recommendations; none was run. Details: audit section 7.

## Remotion

Current Remotion docs (Context7, main) keep `<Img>` as the standard component; `<CanvasImage>`
is the effects path that `<Img>` itself routes to. Combo's `Img` guidance is **not stale**; the
earlier "drift" flag was wrong. No local Remotion project exists to check a version against.

## Integration done from these results

- `practices/e2e.md`: viewport sentence added to the axe clause.
- `practices/security.md`: one conditional bullet naming the collector, its network and token
  behaviour, and the nonexistent-package rule.
- `practices/outcome-evidence.md`: one conditional sentence on the Impeccable pre-check with
  its taste caveat.
- Nothing vendored: the Trail of Bits scripts are CC BY-SA and the Impeccable binary is
  third-party, so Combo links to them by name and does not copy them. Tool installs are the
  owner's step (commands in the integration plan).
