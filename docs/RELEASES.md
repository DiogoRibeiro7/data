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
