# Outcome comparison

| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude | full | 24 | 23/24 | 17 | 9 | 327877 | 47 | 5.69 |
| claude | no-claude-md | 24 | 24/24 | 7 | 8 | 250134 | 50 | 4.98 |

| host | case | claude/full | claude/no-claude-md |
| --- | --- | --- | --- |
| | bug-zero | 3/3 | 3/3 |
| | diagnose-only | 3/3 | 3/3 |
| | inventory-feature | 3/3 | 3/3 |
| | plan-adapters | 2/3 | 3/3 |
| | security-review | 3/3 | 3/3 |
| | shared-root-cause | 3/3 | 3/3 |
| | translation-negative | 3/3 | 3/3 |
| | trivial-label | 3/3 | 3/3 |

Failures:
- claude/full plan-adapters r2: answer lacks planning intent

Tokens are host-specific counters and not comparable across hosts; cost is only reported by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result.
