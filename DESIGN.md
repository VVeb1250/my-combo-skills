# Combo: coordinated workflows from four source packs

Status: expanded implementation contract for the rebuild requested by the owner.
This supersedes the earlier handoff's no-router/Arm A restrictions and the v0
installation shape. Codex was the first deployment target; the authorized Claude
Code adaptation below adds a separate host adapter to the same workflow source.
The owner subsequently included noncoding capabilities and requested an equal-
content comparison of one entrypoint and a modular skill pack. EXPERIMENT.md
defines that comparison; EXPANSION.md defines full source coverage.

## Intended experience

The user states the job normally, in Thai or English. Codex chooses a fitting
workflow, does the work to completion, and uses specialist knowledge only when
the work needs it. The user does not choose between Matt and ECC or remember
17 skill names. A small edit remains a small edit. A hard task gets the process
its actual uncertainty and risk require.

This is a designed combination, not four upstream bundles enabled together and
not a summary of upstream README files. Keep useful concrete mechanics and
references; remove conflicting ownership, accidental dependencies on Claude,
mandatory interview/tracker/commit ceremonies, and indiscriminate reviewer fanout.

## Architecture decision

Ship candidate B: twelve direct workflow entries, a fallback `combo` router,
`combo-maintain` for installation maintenance, and the explicit-only
`combo-author` for changing the pack itself. All paths share workflow and
reference files inside `combo`; no workflow body is duplicated. The matched
comparison and its limits are recorded in `audit/ab/DECISION.md`. This is a
maintainability choice for the full domain scope, not proof of universal model
or token-cost superiority. Source entries use REFERENCE.md, not nested SKILL.md.

Keep the short engineering policy scoped to engineering. The global routing
pointer selects the matching workflow entry for substantive work across the
supported domains, and uses combo when the route is uncertain. Once loaded,
continue without rereading on every follow-up. Native host skills for browsers,
documents, images, and concrete utilities remain independently discoverable.

Routing is a decision the model makes from the user's objective, actual state,
and requested stopping point. Markdown completion criteria are guidance, not
deterministic gates. No workflow engine, daemon, hook, scoring service, or runtime
dependency is needed for this design.

## Source ownership

| Source | Responsibility | Adaptation |
|---|---|---|
| Karpathy | Understand intent, observable success, causal/surgical scope | Routine decisions proceed from evidence; preserve the complete user requirement |
| Ponytail | Challenge unnecessary complexity before and after a change | Preserve proven design, safety, accessibility, and requested extensibility; no code golf |
| Matt | Workflow shape, decision exploration, behavioral TDD, spec/standards review, context boundaries | Borrow ask-matt's paths and on-ramps; route automatically; remove mandatory interviews, tracker setup, commits, and fanout |
| ECC | Engineering specialists plus research, content, commercial operations, media, and productivity methods | Consult relevant source methods, adapt example companies/thresholds/personas, and keep native tools and the host's configured memory rules authoritative |

Role ownership applies to knowledge/process, not branding in the user's normal
output. A response should describe work and evidence rather than reciting packs.

## Router contract

`skills/combo/SKILL.md` provides routing for the package. Keep descriptions short
and discriminating, with independent entrypoints only where discovery earns its
cost. Support engineering, research, content, learning, business, media, and
productivity. Simple chat, translation, and understood tiny edits can stay
inline; native artifact and utility skills keep their concrete tool ownership.

Inspect available task context before choosing. Honor a requested stopping point
(review-only, planning-only, diagnosis-only, implementation, or verification).
The router selects ONE primary path; it does not load every workflow.

| Situation | Primary path | Completion |
|---|---|---|
| Tiny, understood, reversible edit with no meaningful behavioral/security risk | Direct, inline in router | Make edit, check the actual result, finish |
| User requests a feature or behavior-preserving refactor | `workflows/deliver.md` | Intended behavior delivered and appropriately checked/reviewed |
| Something fails and the user wants it repaired | `workflows/debug.md` | Causal repair supported by a reproduction or other adequate evidence; relevant regression/verification |
| User needs requirements/design/implementation plan | `workflows/plan.md` | Actionable decision/plan at the fidelity the user needs; build afterward only when already requested |
| User asks to review changes, code, or security without implementing | `workflows/review.md` | Evidence-ranked actionable findings or an honest no-findings result |
| User asks to run checks or exercise a user journey | `workflows/verify.md` | The requested outcome actually checked, with limits reported |
| User asks to understand code, compare technical options, or investigate without fixing | `workflows/investigate.md` | Evidence sufficient for the requested explanation/decision |

Compiler/type/dependency failures are a DEBUG specialization, not a second
full workflow. E2E is a VERIFY technique. Refactoring is a DELIVER mode that
preserves behavior. Security is a cross-cutting specialist concern, not a
separate mandatory pipeline. Hard ambiguity can use research/prototyping inside
PLAN, then return to the requested work.

When resuming, recover the user's goal, constraints, completed evidence, and
next unresolved step from current context or an existing task artifact. Verify
stale facts that matter. Continue at that step instead of restarting discovery
or asking for permission already given. A follow-up question does not silently
cancel the implementation task.

## Workflow detail that earns its place

DELIVER: understand the relevant code and contract; resolve material unknowns;
choose a minimal correct design; implement vertical behavior slices; use public
seam tests where they can detect the behavior; verify; review proportionally;
fix findings within authorized scope. Preserve meaningful seam/adapter choices.

DEBUG: establish an informative feedback loop. Prefer an observed failing case,
but unavailable reproduction does not forbid reasoning from logs, code, or a
reported input. Label uncertainty, choose a discriminating check, trace shared
callers, repair cause, and verify. Avoid "never reason, always add logging".
Build errors should be grouped by causal dependency, not fixed as unrelated noise.

PLAN: surface only decisions that change product behavior, compatibility, or
scope. The agent gathers facts; the owner decides genuine preferences. Use
small runnable prototypes when a design cannot be settled usefully on paper.
Large uncertain efforts can keep a short map of decisions/dependencies in the
repo's existing convention, without mandatory tracker setup or a custom state
schema. A clear bounded feature does not need a multi-session map.

REVIEW: examine both requirement fidelity and implementation quality; support
findings with reachable triggers/consequences. Use specific security, data,
concurrency, or simplicity lenses only when warranted. Review does not imply
fixing/publishing. A final review during authorized delivery may fix its findings.

VERIFY: distinguish tests, build, typecheck, lint, and observed user journeys.
Use existing scripts/fixtures; inspect failure evidence. Follow the host browser
skill before UI interaction. Avoid a fabricated pass when a check could not run.

INVESTIGATE: bound the uncertainty, inspect primary evidence and versions,
separate facts from inference, and recommend a concrete next move. Explain-only
work must not create code, projects, decision files, or external jobs by default.

## Progressive specialist detail

Factor shared practices into small files reached at the relevant step: behavior
tests (Matt), design/seams (Matt), security (ECC), simplicity (Ponytail), build
repair and E2E (ECC), context/resume (Matt), and delegation.

Provide useful technology notes for HTTP/API, React/TypeScript, Python, Rust,
SQL/migrations, and MCP. Preserve specialist examples where they add value,
behind selective relative pointers. Avoid dumping a generic manual into every
task. New files should retain operational detail, not just generic maxims.

Preserve all source skill entries in a searchable in-package reference library,
including noncoding methods, procedures, examples, and needed supporting files.
Route through bounded domain indexes, not a 331-entry always-loaded catalog.
Keep curated engineering notes as the quick shelf; the full sources provide
depth when needed. Record source commit, original path, generated destination,
domain, and lifecycle or host-dependence labels in a deterministic source map.

Retaining an upstream document does not adopt its governing instructions.
Alternate memory systems, hooks, installers, orchestration frameworks, and
personas remain source knowledge for explicit design or integration requests.
Their defaults never silently replace the host or user's authority. Examples of
companies, metrics, author voice, escalation chains, and multi-session learning
workspaces must be adapted to the actual request. The host's configured memory rules
remain the authority for personal memory. Original-reference coverage is distinct from
semantic review and from successful execution in the installed host.

Six noncoding workflows turn the library into usable task paths: research
weighs evidence for a decision, content preserves facts and voice across media,
learning provides an appropriately bounded lesson and retrieval practice,
business makes traceable operational calculations, media produces and inspects
the requested artifact, and productivity supports coordination and handoff.

## Delegation and model cost

Primary agent owns interpretation, architecture, difficult tradeoffs, integration,
and final acceptance. When delegation is authorized and independent work exists,
use Luna (`gpt-5.6-luna`, effort `max`) for bounded research, file implementation,
routine checks, and evidence gathering. Give concrete ownership and acceptance
criteria, and tell workers they share a workspace. Delegation should remove work
from the primary context, not duplicate it. One small task can stay local.

Keep model-specific configuration in a Codex adapter, not portable workflow
content. Configure a `combo_worker` role if the installed host supports it,
using its supported role/config-file schema. In hosts without model-selection or
agent tools, run the workflow locally; do not claim a fallback agent is Luna.
Existing explicit user choices override the default. Do not pin the main model.

## Replacing v0 and legacy overlaps

Retire the 17 v0 entrypoints from discovery when combo is activated. Reuse useful
content inside the new package after review, not as separate competing owners.
Retire old `codex-agent-harness`, broad `debug-by-logging`, `graphify-windows`, and
legacy Matt coding workflow/design/research wrappers when their jobs are now
owned by combo. Preserve originals and previous rollback receipts outside the
active package. Keep distinct utilities and native artifact/browser skills.

The manifest governs discovery. Retired executable owners cannot reappear
through a legacy hub; a labeled source reference may remain available for
explicit integration or adaptation without enabling its old skill or services.
Do not change unrelated memory content/state, hooks, credentials, or native
plugin settings. Add only the scoped Codex worker role and owned skill changes.

## Repository and installed product

The root README should explain the actual combo, show its route map, and give
simple examples. Make the active product under `skills/combo/` easy to find.
Move superseded v0 source/docs into a clearly named archive rather than leaving
them looking like the current product. Keep historic backups intact.

The installed package must function after the development checkout moves:
runtime workflow/reference pointers stay inside the installed bundle. Upstream
source provenance may link to immutable GitHub commits. Build/maintenance tooling
can know the source checkout, but normal engineering execution must not depend
on D:/0_person-project/my-combo-skills or the old user skill-library directory.

## Acceptance

1. The selected discovery layout auto-discovers, with explicit `$combo` fallback.
2. Every active workflow/reference pointer resolves and retired owners remain
   disabled; reference-only source knowledge is clearly labeled.
3. All four packs retain their full source entry coverage, including noncoding;
   source maps distinguish references, adapted workflows, and host dependence.
4. Global policy, actual app-server discovery, and installed bytes agree.
5. Source-to-install updates are repeatable, non-owned config is preserved, and
   actual installed rollback is rehearsed on copies with drift protection.
6. Fresh Luna Max sessions compare equal-content candidates on the ten paired
   cases in EXPERIMENT.md. Include actual tool/output evidence and semantic
   outcome grading; do not equate a routing label with correct work.
7. Check trivial edits avoid unnecessary workflow loading; checks/agents/reviews
   scale with the real task. At least one regression detects a seeded defect.
8. Report measured coverage and remaining uncertainty honestly. Multi-model
   compatibility is a design property, not proof of identical model obedience.

This design is approved for implementation by the current user request. Routine
implementation choices and reversible installation within this scope proceed
without another approval round. Main-agent architecture decisions stay with root.

## Claude Code adaptation (2026-09-10)

Keep the common workflows and pinned four-pack library as the knowledge source.
Render Claude-specific entrypoints and a small execution guide from
`adapters/claude/overrides`; omit Codex `agents/openai.yaml`. Personal skills use
native Skill invocation and explicit `/combo-*` names. Relative supporting-file
links remain in the installed package; `${CLAUDE_SKILL_DIR}` supplies the runtime
base directory. Do not duplicate or force-load the full library into entrypoints.

Replace the old user-level "read every plausibly relevant skill" discipline with
one primary route and selective supporting reads. Preserve normal completion for
build requests, requested stopping points, and Claude's actual Plan Mode approval
transition. Do not add hooks, permission grants, mandatory forks, or model pins.

Use a native personal `combo-worker` subagent with `model: inherit`; the parent
passes bounded context, ownership, and expected evidence. Codex's Luna Max role
does not translate into a fictional cross-provider Claude model. Preserve the
user's current Claude main model, effort, and permissions.

Retire only the overlapping ECC, ECC hubs, Matt plugin discovery and the old
multi-model-orchestrator skill. Keep original plugin/skill files and unrelated
utilities. Claude has its own configured memory authority; adapt navigation
guidance to that host instead of importing another host's memory policy. Preserve all
unowned CLAUDE.md bytes and settings semantics, including user memory hooks.

Reuse the transaction/receipt/rollback engine with a separate Claude manifest.
Validate rendered references and native discovery, exercise a few fresh Claude
sessions, and rehearse rollback on a copy. These checks establish the observed
Claude behavior; the earlier Codex A/B result is not a Claude benchmark.
