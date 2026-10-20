# Outcome comparison

| host | arm | runs | outcome pass | workflow loaded | mean tool calls | mean tokens | mean seconds | cost USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | full | 24 | 24/24 | 18 | 12 | 137499 | 23 | 0.00 |

| host | case | codex/full |
| --- | --- | --- |
| | bug-zero | 3/3 |
| | diagnose-only | 3/3 |
| | inventory-feature | 3/3 |
| | plan-adapters | 3/3 |
| | security-review | 3/3 |
| | shared-root-cause | 3/3 |
| | translation-negative | 3/3 |
| | trivial-label | 3/3 |

Tokens are host-specific counters and not comparable across hosts; cost is only reported by Claude and is not an invoice. Small samples: a difference needs repeats before it is a result.
