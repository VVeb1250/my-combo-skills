# Combo Rework candidate

A staged implementation of the AI-first, local-first design. Not active in the original pack and not ready for live installation.

- [Design](DESIGN.md): accepted outcome, boundaries and evaluation criteria.
- [Sources](SOURCES.md): grounded synthesis and source-review limits.
- [Policy](POLICY.md): continuous responsibilities for the main agent.
- [Skills](skills/combo/SKILL.md): explicit map of focused methods; six implicit capabilities and five explicit entries.
- [Techniques](skills/combo/techniques/INDEX.md): selective, problem-first reasoning and evidence; no technology catalog.
- [Adapters](adapters/README.md): native recovery cue and authority example.
- [Integration](INTEGRATION.md): resume point, existing installer/knowledge preservation and remaining gates.
- [Evaluation](evals/README.md): independent fixture and lifecycle/packaging probes.

Run structural checks and fixture oracle self-check from this folder:

```sh
python -B -m unittest discover -s tests -v
```

The checks establish file/package integrity and the evaluator's baseline behavior only. No agent benchmark or native installation verdict is claimed.
