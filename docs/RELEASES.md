# Release and snapshot policy

The repository uses immutable Git history as the technical version boundary and optional GitHub releases as human-readable dataset-registry milestones.

## Principles

### Canonical dataset snapshots are immutable

A published snapshot must not be silently edited in place.

When upstream data changes, either:

- add a new immutable snapshot/version; or
- update a deliberately rolling dataset through a reviewed commit that clearly records the new retrieval/snapshot date and checksums.

### Consumers pin commits and checksums

Reproducible consumers should pin:

- the exact 40-character Git commit SHA;
- canonical path;
- SHA-256 checksum.

A release tag is useful for discovery but does not replace checksum verification.

## Repository releases

Create a repository release when a change materially alters the reusable data surface, for example:

- the first canonical dataset is promoted;
- a canonical dataset receives a new snapshot;
- a dataset is deprecated or removed;
- the metadata schema changes;
- the consumer contract changes incompatibly.

Documentation-only edits and external-source note corrections do not require a release unless they materially affect reproducibility or legal interpretation.

## Tag convention

Use calendar-based immutable snapshot tags:

```text
snapshot-YYYY.MM.DD
snapshot-YYYY.MM.DD.N
```

Use the optional numeric suffix when more than one registry snapshot is published on the same day.

Examples:

```text
snapshot-2026.09.30
snapshot-2026.09.30.2
```

## Release notes

A registry snapshot release should state:

- canonical datasets added;
- canonical datasets updated;
- canonical datasets deprecated/removed;
- source/provenance corrections;
- licence/terms changes;
- metadata schema changes;
- migration notes affecting consumers;
- the release commit SHA.

## Client and manifest compatibility

Package/API, metadata-schema, static-distribution, deprecation, and historical
snapshot-manifest compatibility are governed by
[Compatibility and versioning policy](COMPATIBILITY.md).

Registry snapshot tags, package versions, metadata schema versions, static
distribution versions, and snapshot manifest versions are deliberately
independent version domains.

The current snapshot manifest is version 7. Published historical manifests
versions 1–7 remain recognized and are never rewritten in place.

## Metadata schema versioning

`schema_version` inside dataset metadata is independent of repository snapshot tags.

Increase the metadata schema version only for a contract change that requires validators or consumers to interpret metadata differently.

## Corrections

If a published dataset has an integrity, provenance, licensing, or privacy problem:

1. open an issue immediately;
2. prevent new consumption where appropriate;
3. correct or remove the affected bytes in a new commit;
4. document the change in migration/release notes;
5. do not rewrite already published tags to hide the earlier state.

For serious publication issues, a release can be marked as superseded, but historical Git objects remain part of repository history unless a dedicated history-rewrite process is justified.

## Snapshot tooling

The repository provides `scripts/create_snapshot.py` to generate deterministic release material.

Example:

```bash
python scripts/create_snapshot.py \
  --tag snapshot-2026.10.01 \
  --commit <40-character-commit-sha> \
  --output-dir release-material
```

The output directory contains:

- `snapshot-manifest.json` — machine-readable immutable manifest;
- `snapshot-summary.md` — human-readable release summary;
- `release-provenance.json` — deterministic provenance and release-attestation metadata generated after the manifest and summary.

The manifest records:

- repository name;
- snapshot tag;
- exact commit SHA;
- SHA-256 of the canonical and external catalogs;
- canonical/external catalog schema versions;
- metadata schema versions and schema-file SHA-256 digests;
- every canonical dataset file path and SHA-256 checksum;
- each canonical dataset's committed source snapshot and licence identity;
- the committed provenance-debt report SHA-256 and debt summary;
- the committed registry-quality/adoption-policy digests and canonical expansion state;
- the committed lifecycle report SHA-256, lifecycle counts, replacement chains, and consumer migration state;
- the installable registry client package/API/Python compatibility identity;
- the static machine-readable distribution version, index digest, and artifact contract.

Snapshot manifest version 7 adds normalized consumer-relationship and provenance-debt item identities for exact snapshot-to-snapshot diffs. Manifest v6 added packaged registry-client and static-distribution state; manifest v5 added canonical lifecycle and supersession state. Historical releases that used earlier manifest versions remain unchanged.

No runtime timestamp is included. Given the same repository bytes, tag, and commit, the generated JSON and Markdown are byte-for-byte deterministic.

## Release provenance and attestation metadata

After snapshot material is generated, `scripts/generate_release_provenance.py` writes `release-provenance.json`.

The provenance record is versioned by `schemas/release-provenance-v1.schema.json` and binds:

- repository, immutable snapshot tag, exact release commit, and snapshot-manifest version;
- SHA-256 digests of `snapshot-manifest.json` and `snapshot-summary.md`;
- the repository workflow path and the exact commit-pinned reusable publisher workflow;
- registry-client package/API identity and static-distribution version;
- the validation commands that are required to have succeeded before provenance generation.

The provenance payload deliberately excludes runtime timestamps, workflow run IDs, runner identities, and other execution-specific values. Those values can be useful operational evidence, but putting them into the deterministic payload would make identical release inputs produce different bytes.

This provenance record is an attestation of the deterministic release inputs and required validation path. Cryptographic/offline verification of the complete release bundle is a separate trust layer and is handled by the independently verifiable release-identity work.

## Manual GitHub release workflow

Use **Actions → Snapshot release → Run workflow**.

Inputs:

- `snapshot_tag` — must match `snapshot-YYYY.MM.DD` or `snapshot-YYYY.MM.DD.N`;
- `commit_sha` — exact 40-character lowercase Git SHA;
- `publish_release` — defaults to `false`.

Every manual run:

1. validates the tag and commit syntax;
2. checks out exactly the requested commit;
3. verifies checkout identity;
4. installs validation dependencies;
5. runs the full unit-test suite;
6. validates repository metadata, checksums, catalogs, and hygiene;
7. validates the external catalog freshness;
8. validates the consumer catalog freshness;
9. validates the registry quality report freshness;
10. validates the provenance-debt report freshness;
11. validates the lifecycle report freshness;
12. validates the static registry distribution freshness;
13. generates deterministic snapshot material;
14. generates deterministic release provenance;
15. uploads the complete material as a workflow artifact.

After the repository-specific validation and release-material generation, the workflow delegates snapshot publication to the reusable `snapshot-release.yml` workflow in `DiogoRibeiro7/git-actions-collection`, pinned to an exact collection commit.

When `publish_release=false`, the reusable workflow runs in dry-run mode. It validates the snapshot identity and prepared artifact but does not create a tag or release. This is the recommended dry run.

When `publish_release=true`, the reusable workflow:

1. refuses to overwrite an existing tag;
2. downloads the exact prepared artifact;
3. creates an annotated tag pointing to the requested commit;
4. pushes the tag;
5. creates a GitHub release using `snapshot-summary.md` as release notes;
6. attaches the prepared snapshot files, including provenance metadata, to the release.

The data repository therefore owns registry validation and deterministic snapshot generation, while the shared Actions collection owns the generic immutable publication machinery.

Ordinary pushes and pull requests **never create tags or releases**.

## Operator checklist

Before publishing:

- ensure `main` is green;
- choose the exact commit to release;
- run the manual workflow once with `publish_release=false`;
- inspect the uploaded manifest, summary, and provenance record;
- rerun with the same tag/commit and `publish_release=true`;
- never reuse or move an existing snapshot tag.
