---
name: ecc-build-fix
description: Diagnose and repair failing builds, compiler errors, typecheck errors, imports, and dependency resolution using existing project commands. Use when build, CI compilation, or type checking fails. แก้ build พังและ type error. Runtime behavior bugs use behavioral diagnosis/tests.
metadata:
  owner: ecc
---

# Restore a working build

Read project scripts, lockfiles, toolchain versions, and CI configuration. Run
the failing configured command and retain the relevant error. Compilation, lint,
type checking, and tests are distinct checks; do not substitute one for another.

Group cascades by root cause. Inspect import/type definitions and affected callers.
Fix the earliest causal error or a small coherent group, then rerun the failing
command. Avoid changing unrelated logic to silence diagnostics.

Check installed versions and the existing package manager before adding/upgrading
dependencies. Prefer the lockfile's normal install when restoring a missing local
environment is necessary and authorized. Do not disable strict checking, replace
types with any, skip tests, or rewrite architecture just to turn the build green.

If an attempt adds errors or repeats without new evidence, stop that approach,
reassess the cause, and try an evidence-supported correction. Ask for input only
when a real missing requirement or external dependency blocks progress.

Verify the original command, then affected behavior if the repair changed logic.
Report remaining failures and environment limitations separately from fixes.
