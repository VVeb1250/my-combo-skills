# River pilot, 15 November 2026

This is a bounded test of the synthetic river fixture, not proof of general
Combo quality or real RTS terrain and gameplay. A is no staged Combo; B is
baseline `2ec0e2033bdcc783ab021efa508eaf98d0c28786`; C is candidate
`0cce09648496f96d67abb3b2da80b77774d520c6`. Each used Codex CLI,
`gpt-6-luna` with high reasoning effort, a 300-second timeout, fixed seeds
17, 41, 83, 109 and 151, and the same synthetic fixture. Arm order rotated
across three rounds. The runner uses danger-full-access on trusted synthetic
workspaces; it is not filesystem isolation. Shared host effects may remain.

| Arm | Artifact passed mechanical acceptance | Completed and passed | Timed out |
| --- | ---: | ---: | ---: |
| A | 1/3 | 1/3 | 0/3 |
| B | 3/3 | 1/3 | 2/3 |
| C | 3/3 | 2/3 | 1/3 |

Mechanical acceptance of an artifact retained after timeout is reported
separately from a completed session. No round had three completed sessions,
so these observations do not establish relative superiority. Structured tool
image payloads were not observed in any session; this is an evidence gap, not
proof that an agent never viewed an image.

Before revealing arm identities, the assistant compared all five seeds at a
consistent scale and enlarged seed 17. All nine outputs failed the reviewer's
confluence threshold because joins remained acute or abrupt. See the
[blind review](blind-review.md) and the images for
[round 1](river-round-1.png), [round 2](river-round-2.png), and
[round 3](river-round-3.png). This is an assistant visual review of a 2D
proxy, not human art approval or validation of vehicle behavior.

The independent oracle was corrected before this pilot: the contract requires
the main river to widen downstream, not the downstream width to exceed the
combined widths of both upstream branches. Rechecking the earlier pilot with
the corrected oracle changed arm A from fail to pass; B remained pass and C
remained fail because seeds 17, 83 and 109 merged before the middle third.
The [sanitized summary](summary.json) records individual results, seed failure
messages, usage, the blind key revealed after review, and SHA-256 hashes of the
modified evaluator. Raw event logs and host-specific artifacts were not
published.
