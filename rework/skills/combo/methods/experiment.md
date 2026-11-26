# Bounded experiments

Use an experiment when a mechanism, performance, architecture or actual artifact quality is uncertain enough to change the decision. Name the decision, competing hypothesis and observation that would change it. A single discriminating probe is often enough; compare multiple real candidates only when meaningful uncertainty remains.

Preserve the current state and use an isolated branch/worktree for risky or competing implementation changes when authorized. Start candidates from the same known baseline; keep fixtures, seeds, settings, dependencies, hardware and measurement procedure comparable. Worktrees share Git refs/config and may share runtime services, so isolate ports, mutable data and side effects separately. No remote or production actions without authority.

Run the real mechanism and observe actual output. For terrain or other generative systems inspect integrated geometry, diverse fixed seeds, transitions, known failure and contrast cases; evaluate domain behavior and performance separately from appearance. Do not accept a passing graph check, one favorable seed or a compile as proof of visual quality. Record revision and dirty inputs if any, settings, result and limits only as needed for reproducibility. Distinguish measured evidence from candidate inference.

Select or reject the approach from evidence, not investment. Integrate only compatible verified parts, check callers and integrated outcome, then reconcile the [wiki](wiki.md) with the reusable conclusion. Preserve valuable experiment history in Git/artifacts; do not append routine logs to current understanding. Remove only owned disposable material after confirming needed evidence is recoverable.
