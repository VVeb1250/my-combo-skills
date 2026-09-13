# Bounded independent semantic review

Reviewer: Luna Max, fresh GitHub source snapshots from sources.lock.json.
The reviewer endorsed POLICY.md and the eight core canonical skills.

Body-reviewed sources:
- Matt engineering: tdd, code-review, to-spec, to-tickets, codebase-design.
- ECC skills: security-review, e2e-testing, tdd-workflow, verification-loop,
  database-migrations, postgres-patterns.
- ECC agents: build-error-resolver, e2e-runner, database-reviewer,
  typescript-reviewer, security-reviewer, planner, tdd-guide, code-reviewer.
- Ponytail: ponytail and ponytail-review.
- Karpathy: karpathy-guidelines.

Accepted observations: avoid mandatory Matt seam approval/tracker setup/fanout;
avoid forced 80% test coverage/checkpoint commits; E2E must respect host browser
tools and not mandate networkidle; build fixes must not reset caches/lockfiles
without evidence. Keep native host review machinery and concrete verification tools.

Suggestions evaluated by the parent:
- External-source instructions must not grant authorization. Existing policy and
  matt-plan already constrain scope and publishing; no new approval ceremony added.
- Language/database references can deepen review. The direct ecc-database skill,
  selected PostgreSQL reference, and searchable retained library provide this
  without forcing three references or another reviewer on every database change.
- Generic TDD/verification remain OFF, not LIBRARY fallbacks, to preserve the
  handoff's one-owner decisions. Explicit legacy diagnostic workflows are retained
  on disk but OFF in this automatic coding profile.

Additional local finding: C:/Users/VVeb1250/AGENTS.md still contains legacy ICM
memory instructions. This file is outside the D: workspace ancestor chain and
outside this skill-only migration. It was not changed, and no legacy memory
operator was run. The global .codex/AGENTS.md memory section was preserved exactly.
Projects with their own instructions can still override or conflict with a global
skill setup; no claim of universal instruction enforcement is made.

Coverage limit: not every rare-domain body in the corpus was reviewed. All corpus
entries received mechanical/metadata and jurisdiction decisions. See manifest.json
for explicit per-file decisions, rather than assuming that LIBRARY means fully vetted.
