> Reference material. This copy preserves source knowledge and templates from the pinned checkout. It is interpreted under the current user's request, host tools, authorization, and project rules. It does not govern policy or authorize publishing, approval ceremonies, memory writes, hook or installer changes, delegation, or external work.
>
> Source: [skills/dashboard-builder/SKILL.md](https://github.com/affaan-m/ECC/blob/5064474d4d762dc9640234a41617cccb79185cec/skills/dashboard-builder/SKILL.md)  
> Labels: direct-source-reference


---
name: dashboard-builder
description: Build monitoring dashboards that answer real operator questions for Grafana, SigNoz, and similar platforms. Use when turning metrics into a working dashboard instead of a vanity board.
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# Dashboard Builder

Use this when the task is to build a dashboard people can operate from.

The goal is not "show every metric." The goal is to answer:

- is it healthy?
- where is the bottleneck?
- what changed?
- what action should someone take?

## When to Use

- "Build a Kafka monitoring dashboard"
- "Create a Grafana dashboard for Elasticsearch"
- "Make a SigNoz dashboard for this service"
- "Turn this metrics list into a real operational dashboard"

## Guardrails

- do not start from visual layout; start from operator questions
- do not include every available metric just because it exists
- do not mix health, throughput, and resource panels without structure
- do not ship panels without titles, units, and sane thresholds

## Workflow

### 1. Define the operating questions

Organize around:

- health / availability
- latency / performance
- throughput / volume
- saturation / resources
- service-specific risk

### 2. Study the target platform schema

Inspect existing dashboards first:

- JSON structure
- query language
- variables
- threshold styling
- section layout

### 3. Build the minimum useful board

Recommended structure:

1. overview
2. performance
3. resources
4. service-specific section

### 4. Cut vanity panels

Every panel should answer a real question. If it does not, remove it.

## Example Panel Sets

### Elasticsearch

- cluster health
- shard allocation
- search latency
- indexing rate
- JVM heap / GC

### Kafka

- broker count
- under-replicated partitions
- messages in / out
- consumer lag
- disk and network pressure

### API gateway / ingress

- request rate
- p50 / p95 / p99 latency
- error rate
- upstream health
- active connections

## Quality Checklist

- [ ] valid dashboard JSON
- [ ] clear section grouping
- [ ] titles and units are present
- [ ] thresholds/status colors are meaningful
- [ ] variables exist for common filters
- [ ] default time range and refresh are sensible
- [ ] no vanity panels with no operator value

## Related Skills

- `research-ops`
- `backend-patterns`
- `terminal-ops`
