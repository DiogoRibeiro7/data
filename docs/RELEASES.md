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
- `snapshot-summary.md` — human-readable release summary.

The manifest records:

- repository name;
- snapshot tag;
- exact commit SHA;
- SHA-256 of the canonical and external catalogs;
- canonical/external catalog schema versions;
- metadata schema versions and schema-file SHA-256 digests;
- every canonical dataset file path and SHA-256 checksum;
- the committed provenance-debt report SHA-256 and Phase 6 debt summary.

No runtime timestamp is included. Given the same repository bytes, tag, and commit, the generated JSON and Markdown are byte-for-byte deterministic.

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
8. validates the registry quality report freshness;
9. validates the provenance-debt report freshness;
10. generates deterministic snapshot material;
11. uploads the material as a workflow artifact.

When `publish_release=false`, the workflow stops there. This is the recommended dry run.

When `publish_release=true`, a second job:

1. refuses to overwrite an existing tag;
2. downloads the exact prepared artifact;
3. creates an annotated tag pointing to the requested commit;
4. pushes the tag;
5. creates a GitHub release using `snapshot-summary.md` as release notes;
6. attaches both snapshot files to the release.

Ordinary pushes and pull requests **never create tags or releases**.

## Operator checklist

Before publishing:

- ensure `main` is green;
- choose the exact commit to release;
- run the manual workflow once with `publish_release=false`;
- inspect the uploaded manifest and summary;
- rerun with the same tag/commit and `publish_release=true`;
- never reuse or move an existing snapshot tag.
