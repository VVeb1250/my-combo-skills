# Outcome comparison

| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude | full | 12 | 11/12 | 10 | 8 | 150731 | 27 | 1.53 |

| host | case | claude/full |
| --- | --- | --- |
| | bug-zero | 3/3 |
| | inventory-feature | 3/3 |
| | security-review | 3/3 |
| | plan-adapters | 2/3 |

Failures:
- claude/full plan-adapters r2: answer lacks planning intent

Tokens are host-specific counters and not comparable across hosts; cost is only reported by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result.
