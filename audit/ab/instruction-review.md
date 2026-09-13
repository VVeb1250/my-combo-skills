# Source instruction review

The lexical scan is in `instruction-audit.json`. Its three candidate matches
were inspected in context:

- `ito-baskets`: “Never send credentials” is a protective instruction.
- `mailtrap-email-integration`: the URL interpolates a Mailtrap inbox identifier
  in an API example. It is not an embedded credential or an upload instruction
  activated by importing the library.
- `springboot-security`: “Keep application.yml free of credentials” is protective.

No actionable injection was established by these matches. This is not a claim
that pattern matching proves the entire source corpus safe.

Root's semantic review of the added workflows addressed concrete host and scope
conflicts in the inspected sources:

- Matt `teach` assumes a persistent multi-session workspace. The adapted learning
  path scales to the learner's actual request, preserving worked examples,
  retrieval practice, spacing, and interleaving without creating unsolicited
  learning records or a second personal-memory system.
- ECC `brand-voice` and `content-engine` preserve source facts and the user's
  actual voice. Upstream author's brand examples are not user defaults.
- ECC `video-editing` prescribes a complete tool stack. The adapted media path
  selects tools needed for the deliverable and follows native tool ownership.
- ECC `project-flow-ops` assumes GitHub plus Linear. Productivity uses the user's
  existing systems and authorization rather than creating a second tracker.
- ECC `inventory-demand-planning` embeds a company persona, metrics, and
  escalation thresholds. Business guidance treats these as examples requiring
  calibration to real data and constraints.
- ECC `market-research` contributes source appraisal, bottom-up checks, and
  separation of facts from inference. Research depth follows the actual decision.

The reference adapter and workflow entrypoints govern interpretation. Raw source
documents are retained for their methods and examples, not installed as competing
global policies. Host integration material is not executed by the importer.
Most source bodies are retained and metadata-classified; they have not each
received a complete semantic audit or a live execution test.

The final shipping-source scan is `installed-source-instruction-audit.json`:
641 instruction/data text files, the same three findings, no new actionable
match. This includes the direct-entry metadata and reference link repairs.
