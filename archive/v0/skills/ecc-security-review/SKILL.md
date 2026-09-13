---
name: ecc-security-review
description: Inspect concrete security risks in authentication, authorization, secrets, untrusted input, uploads, shell/SQL execution, or sensitive data changes. Use for security reviews and changes crossing a trust boundary. ตรวจ security และช่องโหว่. Skip ordinary presentation/style changes.
metadata:
  owner: ecc
---

# Review the affected trust boundaries

Trace attacker-controlled input to privileged operations and sensitive output.
Identify the relevant actor, asset, boundary, and enforcement point from real code.

Check applicable concerns only: authentication vs object-level authorization;
validation/canonicalization; SQL or command parameterization; path traversal and
upload limits; output encoding; SSRF destinations/redirects; credential handling;
sensitive logs; session/CSRF protection; error paths and fail-open behavior.

Preserve behavior required for security even when a shorter solution is proposed.
Reuse established security primitives. Do not introduce a validator dependency
or enterprise checklist just because the skill mentions one.

Demonstrate findings with a concrete reachable path and a harmless test where
practical. Redact secrets and avoid dumping credentials or private data.
Distinguish dependency scanner output from verified reachability/exploitability.
Use current primary documentation when framework defaults affect a conclusion.

Report severity, location, exploit preconditions, consequence, and the smallest
effective remediation. If fixing, add a focused negative/authorization regression
check. Never claim a clean scan proves the absence of vulnerabilities.
This is a modifier of the current task, not a separate orchestration workflow.
