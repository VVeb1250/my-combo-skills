---
name: ecc-python
description: Implement Python logic where typing, resource management, iterators, exceptions, or async behavior matters. Use for substantive Python changes and Python-specific design questions. เขียน Python. Skip formatting, generic planning, and non-Python work.
metadata:
  owner: ecc
---

# Use Python's existing mechanisms

Check the supported Python version, packaging, and nearby code. Prefer stdlib
and existing types over a new framework. Use context managers for resources,
explicit exception boundaries, and typed public interfaces where the repo uses them.

Watch mutable defaults, truthiness that confuses valid zero/empty values with
absence, exhausted iterators, timezone assumptions, and encoding/path boundaries.
For async code, avoid blocking the event loop and preserve cancellation cleanup.
Do not introduce protocols/dataclasses merely because an example contains one.

Test behavior with independent expected results using the existing runner.
Read `references/upstream.md` only for a relevant idiom or worked example;
repo constraints and the combo policy govern its application.
