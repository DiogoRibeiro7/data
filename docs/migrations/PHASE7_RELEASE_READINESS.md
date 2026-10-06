# Phase 7 release readiness

Phase 7 is ready for its immutable closing snapshot.

## Release candidate state

- canonical datasets: **4**;
- canonical data files: **4**;
- active canonical consumer relationships: **4**;
- active consumer repositories: **3**;
- canonical dataset adoption coverage: **100%**;
- pinned consumer contract coverage: **100%**;
- uncovered canonical datasets: **0**;
- actionable provenance/licensing debt: **0**;
- unstructured provenance/licensing debt: **0**.

## Canonical additions since the Phase 7 baseline

Baseline: `snapshot-2026.10.05`.

New canonical datasets:

- `ons-gross-median-weekly-pay`;
- `unhcr-refugee-population-2024`.

Both have active real consumers with exact registry commit, canonical path and
SHA-256 contracts.

## Publication

Tracking issue: #107.

The closing snapshot should be published through **Actions → Snapshot release**
using the exact release commit.

Use the normal two-step process:

1. run with `publish_release=false`;
2. inspect `snapshot-manifest.json` and `snapshot-summary.md`;
3. rerun the same tag and commit with `publish_release=true`;
4. verify the immutable tag and GitHub Release assets.

The snapshot workflow now delegates generic publication to the reusable
`snapshot-release.yml` workflow in `DiogoRibeiro7/git-actions-collection`.
Registry validation and deterministic release-material generation remain local
to this repository.

Phase 7 should be marked complete only after #107 confirms the published tag,
release commit, manifest and summary.
