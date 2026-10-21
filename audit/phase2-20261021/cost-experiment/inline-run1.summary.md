# Outcome comparison

| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude | full | 12 | 12/12 | 11 | 8 | 153491 | 33 | 1.49 |
| claude | inline | 12 | 12/12 | 6 | 7 | 150077 | 28 | 1.50 |

| host | case | claude/full | claude/inline |
| --- | --- | --- | --- |
| | bug-zero | 3/3 | 3/3 |
| | inventory-feature | 3/3 | 3/3 |
| | security-review | 3/3 | 3/3 |
| | plan-adapters | 3/3 | 3/3 |

Tokens are host-specific counters and not comparable across hosts; cost is only reported by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result.
