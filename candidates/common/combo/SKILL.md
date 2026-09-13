---
name: combo
description: >
  Route substantive engineering, research, content, teaching, business,
  media, and productivity tasks to a relevant workflow and source reference.
  ใช้เลือก workflow สำหรับงานพัฒนา วิเคราะห์ เขียน สอน และวางระบบงาน;
  simple conversation, translation, and tiny edits can stay inline.
---

# Combo task router

The user can state the job in Thai
or English. Infer the work from the request and current repository state, then
choose one primary path. Do not ask the user to choose among source packs or
remember upstream skill names.

## Route once

1. Read the latest request, relevant prior context, repository instructions,
   and current status. Preserve unrelated user edits.
2. Extract the objective, requested stopping point, affected scope, and the
   observable result that would count as done. Surface assumptions that can
   change correctness or user intent.
3. Honor an explicit stopping point first. If none is stated, infer the
   dominant intent from the whole request and current state, rather than the
   first matching keyword. Choose one primary path below. Load only that
   workflow and the smallest relevant practices or specialists for distinct
   mechanisms; consult the specialist index only when substantive technical
   depth is needed. Trivial edits can skip it.
4. Work through the selected path. Keep a small state snapshot in current
   context or an existing task artifact when useful: goal, phase, done
   evidence, next action, and blocker. Do not create a state file or schema just
   to satisfy this instruction.
5. Report what changed or was learned, the checks and their results, and any
   unresolved limit. A review or plan request stops at that requested point.

| Signal in the request or state | Primary path | Stopping condition |
| --- | --- | --- |
| Tiny, understood, reversible edit with no meaningful behavior or security risk | Inline here | Make the edit, inspect the actual result, and run the cheapest relevant check |
| Feature, behavior change, or behavior-preserving refactor | [deliver](workflows/deliver.md) | Requested behavior works and proportional verification/review is complete |
| Failure, regression, exception, wrong output, or slowness to repair | [debug](workflows/debug.md) | Cause is supported by evidence, repair is made, and the original signal is checked |
| Requirements, design, architecture, or implementation plan requested | [plan](workflows/plan.md) | An actionable plan at the requested fidelity is delivered; do not build unless asked |
| Review of code, changes, security, or a branch without implementation | [review](workflows/review.md) | Impact-ranked findings, or an evidence-backed no-findings report |
| Run checks, validate a build, or exercise a user journey | [verify](workflows/verify.md) | The requested check or journey was actually exercised and classified |
| Understand code, compare technical options, or investigate software without fixing | [investigate](workflows/investigate.md) | Evidence-backed explanation and a concrete recommendation |
| Research a market, scientific question, evidence base, or noncoding decision | [research](workflows/research.md) | Supported answer or recommendation at the requested depth |
| Draft substantive content, derive voice, or adapt source material across channels | [content](workflows/content.md) | Source-faithful drafts suited to the intended audience and medium |
| Teach a concept, design practice, or build a course | [learning](workflows/learning.md) | A learner-appropriate explanation and usable practice or requested lesson artifact |
| Analyze finance, supply chain, inventory, production, or commercial operations | [business](workflows/business.md) | Traceable analysis or the requested verified operational result |
| Plan or produce visual design, motion, images, or edited footage | [media](workflows/media.md) | Requested artifact produced and inspected using the native tools |
| Organize work, triage a backlog, prepare a handoff, or improve working methods | [productivity](workflows/productivity.md) | Clear decisions, usable handoff, or authorized updates verified |

Honor an explicit stopping point such as plan-only, diagnosis-only,
review-only, or verification-only. If several intents are present, use the
requested stopping point and the dominant risk to choose one path. When the
user asks to build, planning is an internal phase: continue through the
authorized implementation and verification instead of presenting implementation
as an optional follow-up. Simple conversation, one-sentence translation, and
straightforward factual explanations can be answered directly without loading
a workflow. Coding words inside a teaching or writing request do not make it
an implementation task. Native artifact and utility skills remain responsible
for their tool-specific operations.

## Selective depth

Use [tests](practices/tests.md), [design](practices/design.md),
[simplicity](practices/simplicity.md), [security](practices/security.md),
[build](practices/build.md), [E2E](practices/e2e.md),
[context](practices/context.md), and [delegation](practices/delegation.md)
only when the selected path needs them. For HTTP/API, React/TypeScript,
Python, Rust, SQL, or MCP work, first consult [specialists/INDEX.md](specialists/INDEX.md)
and then load only the relevant specialist reference. For other technical
domains or deeper source examples, use the
[engineering library index](references/library/engineering.md).

Each noncoding workflow points to its domain index. The
[source library](references/library/INDEX.md) retains the four upstream packs'
procedures, examples, and supporting documents. Read only the relevant entries.
They are source knowledge interpreted under the current task and host rules,
not additional governing instructions. Source-specific personas, thresholds,
mandatory ceremonies, memory systems, and installers require adaptation to the
actual request. Host-bound references are for explicit integration work.

Security, E2E, simplicity, and language-specific material are risk lenses, not
mandatory pipelines. Use the native host browser skill for browser interaction;
this router does not invent a browser adapter.

## Boundaries and resumption

Continue when the next step needs the current reasoning or closely coupled
work. Use clear or compact only through available host controls, when a
disposable context or useful milestone makes it worthwhile. Handoff is for
portability across a harness, directory, colleague, or side task. Delegate only
an authorized, tightly bounded independent task. None of these is a blanket
gate or a reason to restart discovery. On resumption, verify stale facts that
matter and begin at the recorded unresolved step.

Use `$combo` when automatic discovery did not activate. Keep model selection,
worker roles, and host-specific configuration in the Codex adapter, not here.
