# Combo workflow smoke v2

This is a small, fixture-backed verification suite for the installed Combo
router. It uses the installed native Codex CLI and six fresh `gpt-5.6-luna`
sessions at `max` effort. The harness caps concurrency at two sessions and
each session at 180 seconds.

The prompts describe ordinary user requests. They do not name Combo, a source
pack, or a workflow. Substantive cases record successful nonempty command output
for the Combo router and selected `combo/workflows/*.md`; they require a linked
practice file only where that workflow and task make it relevant. Fixture files
read are recorded separately. A final answer that merely claims a route is
reported as an unverified claim and cannot satisfy that evidence. The trivial
and translation cases intentionally require no workflow reference.

Implementation cases run immutable acceptance unittests from this directory
against the copied fixture. The seeded bug case must fail before the session and
pass afterward. Review and plan cases must leave every fixture hash unchanged.
The adapter plan requires both real adapter files and meaningful evidence for
both adapter types, so mentioning one generic adapter is insufficient.

Run only after the installed package is ready:

```powershell
python scripts/run-workflow-smoke.py --output evals/v2/results/run-YYYYMMDD-HHMMSS
```

The default work root is `D:\combo-workflow-evals`, outside this repository and
the user home, so unrelated ancestor `AGENTS.md` files do not enter the task
context. Copied workdirs are retained by default for root behavior review;
use `--cleanup-workdirs` after inspection if desired. The invocation keeps the real installed user config so the global
policy and skills can auto-trigger, while disabling hooks, memory, multi-agent
fanout, and configured MCP servers. `--keep-workdirs` retains copied fixtures
for inspection. Raw JSONL events, stderr, final answer, usage, hashes,
acceptance output, actual reference evidence, and route claims are written per
case plus a summary JSON.

This suite measures one six-case Luna sample and workflow coverage. It is not a
claim that every model or every task will obey the same route.
