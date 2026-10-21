# Outcome comparison

| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude | inline | 2 | 2/2 | 1 | 8 | 160361 | 26 | 0.25 |

| host | case | claude/inline |
| --- | --- | --- |
| | bug-zero | 1/1 |
| | security-review | 1/1 |

Tokens are host-specific counters and not comparable across hosts; cost is only reported by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result.
