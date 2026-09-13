# Context selection probes

Run explicitly after installing the candidate:

```powershell
python evals/context/run.py --output backups/context-probes
```

This reuses the existing smoke harness and its configured Luna Max model. Two
fresh sessions run sequentially against copies of one new catalog fixture:
diagnosis-only and authorized repair. The fixture includes a current caller
contract, a retired conflicting CLI contract, and unrelated rendering notes.
The independent acceptance stays outside the copied fixture. It exercises empty
selection through the caller, initial defaults, filtering, order, duplicates,
input preservation, and iterators.

The native CLI uses process-only disables for hooks, memory, multi-agent tools,
and configured MCP servers; it does not change the configured main model.
Windows uses a dedicated workspace outside the user profile and process-only
`danger-full-access`, matching the older A/B harness: sandboxed PowerShell could
not enter the temporary fixture. Read-only intent and allowed edits are checked
by prompts and before/after hashes, not enforced by filesystem isolation. These
are local synthetic fixtures, not suitable for untrusted or production tasks.
Project trust is overridden only for the fixture process. Existing installed
skills and global host instructions remain available, so this is a host smoke
probe, not an isolated causal measurement of Combo alone.

Inspect actual tool outputs, final-channel completion, and changes, not just the
harness status. Its read-only command heuristic can flag harmless redirection,
and its final-answer extractor may retain a progress message after timeout.
Check that diagnosis uses the live caller contract and makes no edits; repair
must pass independent acceptance and stay in the allowed files. Reading the
retired note to resolve a contradiction is valid; skipping it is not a mandatory
efficiency goal. Also check whether the selected workflow/context was read,
and whether unrelated or repeated reads actually informed a decision.

Results preserve reported usage, commands, source reads, hashes, and outcomes.
Reported output includes more than final prose; do not call word counts tokens.
No percentage saving, Astra equivalence, or broad model/domain reliability can
be inferred from these two probes. A future comparison needs the same cases and
host/model settings on old and new skills, repeated runs, unseen cases across
domains, and a quality threshold before comparing token or latency savings.
