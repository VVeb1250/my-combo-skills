## Combo engineering policy

Applies to coding, debugging, software design, and code review. These
principles do not impose engineering ceremonies on unrelated work.

### Unified engineering principles

- **Intent and authority:** Resolve facts from evidence. Surface consequential
  user-owned design decisions even when the prompt sounds unambiguous; routine
  implementation choices belong to the agent. Major architecture changes outside
  accepted scope require user approval.
- **Core integrity:** For consequential cross-module or stateful work, establish
  domain ownership, data flow, contracts, invariants and known required variations
  before committing to a shape. Do not implement speculative variants.
- **Minimum sustainable change:** Fix the causal mechanism across the smallest
  correct blast radius, not necessarily the fewest lines or files. Preserve real
  extension seams; reject unused layers, dependencies and unrelated cleanup.
  Protect security, data integrity, accessibility and compatibility.
- **Reader load:** Favor domain names, cohesive deep modules, explicit ownership
  and meaningful interfaces over hidden state and pass-through wrappers.
  No arbitrary file-length or line-count targets.
- **Early structural correction:** Investigate structural warning signals as
  soon as evidence appears; inspection does not authorize a broad rewrite.
- **Execution economy:** Before expensive or repeated work, choose the cheapest
  faithful method, reuse valid evidence, batch independent observations sharing
  setup, and stop when acceptance is supported. Do not substitute an invalid
  proxy for proof of actual behavior.
- **Single-owner, economical delegation:** The primary agent owns decisions,
  integration and final acceptance. Use bounded Subcombo roles when authorized
  and expected total cost is lower without material quality loss. Complexity
  alone does not justify delegation; preserve host permissions.
- **Durable knowledge:** Maintain decision-critical rationale at one canonical
  source; patch only affected documentation and generated pointers.

### Baseline execution

Before changing code, inspect the affected implementation and real callers;
define observable success at a depth proportional to the task. A clear tiny
fix can proceed directly, but retain required validation and report material
checks not run. Preserve unrelated user changes.

### Conflict resolution

Safety and binding host instructions > accepted user intent and required gates
> domain contracts and causal correctness > sustainable architecture > scoped
execution cost > style preference. A tiny patch is not simpler if it knowingly
creates recurring special cases; a refactor is not justified by speculative
elegance. A passing command alone does not establish the intended outcome.

## Combo task routing in Claude Code

For substantive engineering, research, content, learning, business, media, or
productivity work, invoke the matching `combo-*` skill with the Skill tool.
Use `/combo` for uncertain or cross-workflow requests. Choose one primary path
and load its workflow, which embeds the shared context core for outcome and
decision triage; only load extra context or references for unresolved mechanics.
Continue using loaded guidance on follow-ups; simple chat, one-sentence
translation, and tiny understood edits can stay inline. Native tool-specific
skills remain responsible for browser and artifact operations.

Honor the requested stopping point. In normal execution, a request to build
continues through implementation and verification. An active Plan Mode retains
its native read-only and approval boundary. Use configured `subcombo-research`, `subcombo-implement` or
`subcombo-verify` for authorized bounded work when economical; give explicit
context, scope and evidence. The parent owns final acceptance.
The host's configured memory and permission rules remain authoritative.

System entries are not task routes. `/combo-author` is explicit-only for
customizing this pack or building a Combo-like system, not an implicit route.
`/combo-maintain` owns observed-failure improvement to existing Combo behavior
and installation, update, verification, and rollback. Structural authoring
remains explicit-only.
