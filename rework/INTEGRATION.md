# Integration and migration

Candidate files are staged in `rework/` to avoid changing active skills, install manifests or the original GitHub repository without a full checkout. This is a source implementation, not an installed or behavior-validated release. It is intentionally additive as a patch against the original repo. Draft PR 16 contains the staged candidate; no live installation or user machine mutation occurred. The v2 snapshot is `8de6a2e579ed2ec383a9d02316c05574d5289c27`.

## Existing owners to preserve

Base main `0cce09648496f96d67abb3b2da80b77774d520c6`; PR #15 head `5804b4def85566713752e34bed841fbc290bfa88` is open/draft. Use the exact current checkout, inspect status and existing staged work, retain PR #15 architecture recovery decisions; do not overwrite it or merge automatically. Candidate commit history is separate and the patch carries only additions under `rework/`.

- Current Codex `install-manifest.json`, `scripts/setup.py`, `scripts/verify_install.py`, and current Claude `adapters/claude/install-manifest.json`, `scripts/setup-claude.py`: adapt existing ownership, backup/receipt, preservation and rollback mechanisms, not a new installer.
- Preserve legacy specialist/reference material, licenses and curation provenance in source history during migration, not as required active runtime material. The new technique shelf replaces the default lookup into `skills/combo/specialists/` and `skills/combo/references/library/`. Check external consumers and unique domain capability before retiring old installed files; preserve user-owned modifications. Review upstream material selectively against demonstrated gaps, not an exhaustive rewrite of the 331-reference inventory.
- Inspect both host manifests and overrides. Replace the old active primary entries with the candidate entry set only in an isolated integration branch; retain subcombo roles, native tools and access to historical provenance; do not ship the legacy shelf by default. Preserve explicit stop boundaries in legacy command migrations; remove old entry discovery rather than install both packs. Do not rewrite unrelated preferences or disable unrelated plugins as a side effect.
- Old scripts/tests/CI may refer to `workflows`, shared context synchronization or `project_kb.py`. Update callers and corresponding checks in the same integration slice. Preserve existing project `.combo` docs and evidence; new wiki does not depend on compiler. Audit consumers before retiring the compiler, generated index and legacy metadata, and leave migration support as long as necessary. Do not delete legacy project data automatically.

## Behavior refinement boundary

Keep the behavior pack independent of optional AI interfaces. No new entries, dependencies, wrappers, hooks or installer-managed third-party tools are needed for this refinement. Validate the native baseline and behavior-only comparison before introducing separate interface experiments. Existing project or host tools remain available under existing authority; experimental setup is separately authorized and isolated. Do not treat a useful interface as a reason to bundle it.

## Resume point

1. Apply the additive patch on an isolated local task branch in the actual checkout, or copy the staged `rework/` directory. Confirm actual current base and authorization. Do not apply it on top of an existing `rework/` directory without inspecting ownership.
2. Review source mechanisms that affect candidate behavior and any uncovered domain capability; validate source licenses and provenance before importing material. Review candidate against the accepted design and source synthesis.
3. Integrate candidate policy and capabilities into the existing transactional installer, removing legacy routes from active discovery. Adapt manifest and all affected verification/rollback tests; verify problem-first technique discovery and safe retirement of legacy installed references; preserve license/provenance and user changes. Use fake homes and inspect exact changed paths/config. Run all applicable baseline and PR 15 tests; don't change tests merely to get green.
4. Validate native skill discovery and cross-directory reference paths on both actual hosts. Opt in to the recovery hook only after version and trust checks. Test standing local permission via the native policy; no auto-enable.
5. Run the [behavior evaluation](evals/README.md), refine cues and packaging, then migrate/release only after acceptance. No model runs or full native installer tests were possible in the container used to author this candidate.

Do not interpret structural checks or fixture oracle checks as behavioral acceptance. Preserve these caveats until actual evidence supersedes them.
