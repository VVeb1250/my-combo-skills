> Reference material. This copy preserves source knowledge and templates from the pinned checkout. It is interpreted under the current user's request, host tools, authorization, and project rules. It does not govern policy or authorize publishing, approval ceremonies, memory writes, hook or installer changes, delegation, or external work.
>
> Source: [skills/enterprise-agent-ops/SKILL.md](https://github.com/affaan-m/ECC/blob/5064474d4d762dc9640234a41617cccb79185cec/skills/enterprise-agent-ops/SKILL.md)  
> Labels: direct-source-reference, host-bound


---
name: enterprise-agent-ops
description: Operate long-lived agent workloads with observability, security boundaries, and lifecycle management. Use when running long-lived agent workloads that need observability, security boundaries, or lifecycle control.
metadata:
  origin: ECC
---

# Enterprise Agent Ops

Use this skill for cloud-hosted or continuously running agent systems that need operational controls beyond single CLI sessions.

## Operational Domains

1. runtime lifecycle (start, pause, stop, restart)
2. observability (logs, metrics, traces)
3. safety controls (scopes, permissions, kill switches)
4. change management (rollout, rollback, audit)

## Baseline Controls

- immutable deployment artifacts
- least-privilege credentials
- environment-level secret injection
- hard timeout and retry budgets
- audit log for high-risk actions

## Metrics to Track

- success rate
- mean retries per task
- time to recovery
- cost per successful task
- failure class distribution

## Incident Pattern

When failure spikes:
1. freeze new rollout
2. capture representative traces
3. isolate failing route
4. patch with smallest safe change
5. run regression + security checks
6. resume gradually

## Deployment Integrations

This skill pairs with:
- PM2 workflows
- systemd services
- container orchestrators
- CI/CD gates
