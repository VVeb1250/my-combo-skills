## Combo engineering policy

Applies to coding, debugging, software design, and code review. These principles do not impose engineering ceremonies on unrelated work.

### Unified engineering principles

- **Intent and authority:** Resolve facts from evidence. Surface consequential user-owned design
  decisions even when the prompt sounds unambiguous; routine implementation choices belong to the agent. Major architecture changes outside accepted scope require user approval.
- **Core integrity:** For consequential cross-module or stateful work, establish domain ownership,
  data flow, contracts, invariants and known required variations before committing to a shape. Do
  not implement speculative variants.
- **Minimum sustainable change:** Fix the causal mechanism across the smallest correct blast
  radius, not necessarily the fewest lines or files. Preserve real extension seams; reject unused layers,
  dependencies and unrelated cleanup. Protect security, data integrity, accessibility and compatibility.
- **Reader load:** Favor domain names, cohesive deep modules, explicit ownership and meaningful
  interfaces over hidden state and pass-through wrappers. No arbitrary file-length or line-count targets.
- **Early structural correction:** Investigate structural warning signals as soon as evidence appears; inspection does not authorize a broad rewrite.
- **Execution economy:** Before expensive or repeated work, choose the cheapest faithful method,
  reuse valid evidence, batch independent observations sharing setup, and stop when acceptance is supported. Do not substitute an invalid proxy for proof of actual behavior.
- **Single-agent default:** The primary agent owns decisions and integration. Only spawn advisors,
  reviewers or subagents when the user explicitly requests or approves delegation. Complexity alone does not authorize multi-agent work.
- **Durable knowledge:** Maintain decision-critical rationale at one canonical source; patch only affected documentation and generated pointers.

### Baseline execution

Before changing code, inspect the affected implementation and real callers; define observable
success at a depth proportional to the task. A clear tiny fix can proceed directly, but retain
required validation and report material checks not run. Preserve unrelated user changes.

### Conflict resolution

Safety and binding host instructions > accepted user intent and required gates > domain contracts
and causal correctness > sustainable architecture > scoped execution cost > style preference. A
tiny patch is not simpler if it knowingly creates recurring special cases; a refactor is not
justified by speculative elegance. A passing command alone does not establish the intended outcome.

## Combo task routing

For substantive engineering, research, content, learning, business, media, or productivity work,
select the matching installed `combo-*` workflow entry from the available-skills list. Use
`$combo` for uncertain or cross-workflow requests. Choose one primary path; its workflow
embeds the shared context core for outcome and decision triage. Read separate context guidance only for
unresolved mechanics; do not reread the workflow on every follow-up. Native host skills own browser,
document, image, and concrete utility operations. Simple chat, one-sentence translation, and tiny
understood edits can stay inline.

The router honors the user's requested stopping point. Tiny understood edits can stay inline.
Planning, debugging, delivery, review, verification, and investigation each have their own path.
Checks, tests, security review, simplicity review, delegation, compaction, and handoff scale with
the actual task; none is a universal ceremony or deterministic gate.

System entries are not task routes; `$combo-author` is explicit-only for customizing this pack or
building a Combo-like system.
`$combo-maintain` owns observed-failure improvements and installation, updates, verification, and
rollback. Structural authoring remains explicit-only.

Keep existing public behavior tests and add regression tests when they can detect the actual defect.
Do not publish, push, message third parties, or install services unless the user authorizes that
action.
