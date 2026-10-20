# Routing probe

- **policy**: 27/31 routed acceptably
  - negative: 6/6
  - positive: 17/18
  - confusable: 4/7
- **description-only**: 19/31 routed acceptably
  - negative: 6/6
  - positive: 11/18
  - confusable: 2/7

| case | expected | policy | description-only |
| --- | --- | --- | --- |
| neg-translate-th | `none` | ok `none` | ok `none` |
| neg-typo-inline | `none` | ok `none` | ok `none` |
| neg-fact-http | `none` | ok `none` | ok `none` |
| neg-chat-th | `none` | ok `none` | ok `none` |
| neg-regex | `none` | ok `none` | ok `none` |
| neg-concept-brief | `none` | ok `none` | ok `none` |
| pos-debug-en | `combo-debug` | ok `combo-debug` | MISS `none` |
| pos-debug-th | `combo-debug` | ok `combo-debug` | MISS `none` |
| pos-deliver-en | `combo-deliver` | ok `combo-deliver` | MISS `none` |
| pos-plan-en | `combo-plan` | ok `combo-plan` | ok `combo-plan` |
| pos-plan-th | `combo-plan` | ok `combo-plan` | ok `combo-plan` |
| pos-review-en | `combo-review` | ok `combo-review` | MISS `none` |
| pos-review-th | `combo-review` | ok `combo-review` | ok `combo-review` |
| pos-verify-en | `combo-verify` | ok `combo-verify` | ok `combo-verify` |
| pos-verify-th | `combo-verify` | ok `combo-verify` | ok `combo-verify` |
| pos-investigate-en | `combo-investigate` | ok `combo-investigate` | MISS `none` |
| pos-research-en | `combo-research` | ok `combo-research` | ok `combo-research` |
| pos-content-en | `combo-content` | ok `combo-content` | MISS `none` |
| pos-learning-en | `combo-learning` | ok `combo-learning` | ok `combo-learning` |
| pos-learning-th | `combo-learning` | ok `combo-learning` | ok `combo-learning` |
| pos-business-en | `combo-business` | ok `combo-business` | ok `combo-business` |
| pos-media-en | `combo-media` | ok `combo-media` | ok `combo-media` |
| pos-productivity-en | `combo-productivity` | MISS `agent-handoff-spec` | MISS `agent-handoff-spec` |
| pos-maintain | `combo-maintain` | ok `combo-maintain` | ok `combo-maintain` |
| conf-investigate-research | `combo-investigate` | ok `combo-investigate` | MISS `none` |
| conf-review-verify | `combo-review` | MISS `none` | MISS `none` |
| conf-plan-deliver | `combo-deliver` | MISS `none` | MISS `none` |
| conf-debug-investigate | `combo-debug` | MISS `none` | MISS `none` |
| conf-learning-code | `combo-learning` | ok `none` | ok `none` |
| conf-security-review | `combo-review` | ok `combo-review` | MISS `none` |
| conf-cross | `combo` | ok `combo` | ok `combo` |

Reported cost (not an invoice): $3.11. One sample per case and arm; a miss is a lead for repeats, not a verdict.
