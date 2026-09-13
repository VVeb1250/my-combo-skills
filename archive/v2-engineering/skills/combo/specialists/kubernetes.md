# Kubernetes workloads

Use this note for Kubernetes manifests, rollouts, probes, resources, RBAC, HPA,
or pod diagnosis. Match the cluster API versions and admission policies before
copying a manifest.

## Workload defaults

- Pin an image tag or digest and use a rolling strategy that preserves the
  service's availability requirement. Define requests and limits from measured
  behavior, then revisit them when telemetry changes.
- Run as non-root, drop capabilities, disallow privilege escalation, and use a
  read-only root filesystem when the process permits it. Mount only the paths
  that need writes.
- Use a `startupProbe` for slow initialization, `readinessProbe` for traffic
  eligibility, and `livenessProbe` for a genuinely stuck process. A liveness
  probe that fires during startup can create a restart loop.
- Keep ConfigMaps for non-secret configuration and use Secrets or an approved
  external secret mechanism for credentials. Scope ServiceAccounts and RBAC to
  the verbs and resources the workload needs.
- HPA scales from meaningful metrics; PDB protects voluntary disruption. Neither
  replaces capacity planning or a correct readiness signal.

## Diagnosis

Start with `kubectl get pods`, `describe`, and logs, then inspect events,
resource pressure, image pull credentials, probe endpoints, and the rendered
manifest. Use `kubectl rollout status/history/undo` for controlled deployment
recovery and a temporary port-forward for a local protocol check. Redact Secret
values from captured output.

Source: ECC `kubernetes-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
