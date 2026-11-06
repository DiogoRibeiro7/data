# Changelog

This changelog records changes to the installable `diogo-data-registry`
client. Immutable registry snapshot releases have their own release notes and
tags.

The format follows Keep a Changelog conventions and package versions follow
Semantic Versioning as defined in `docs/COMPATIBILITY.md`.

## [Unreleased]

### Added

- Versioned `verify-handoff --json` evidence with per-file SHA-256 checksums,
  observed byte counts, and a packaged verification-result v1 JSON schema.
- Deterministic `snapshot-provenance.json` release metadata binding snapshot identity, release-asset digests, producer workflow/generator identity, and client/distribution interface versions.
- Deterministic snapshot-to-snapshot diff tooling;
- snapshot manifest v7 consumer-relationship and provenance-debt identities for exact release diffs;
- snapshot manifest v9 normalized external-source state for exact resolution and availability diffs;

- Public compatibility constants for package API, static distribution, and
  supported historical snapshot-manifest versions.
- Explicit compatibility, deprecation, schema, distribution, and historical
  snapshot policy.

### Fixed

- Canonical fetch now treats existing output symlinks, including dangling
  links, as occupied paths requiring explicit `--force`. Forced downloads
  replace the link atomically without modifying its target.
- Archive generation and offline verification now check indexed distribution
  artifact names and declared schema versions against the packaged JSON, so
  mislabeled or schema-inconsistent artifacts cannot pass bundle checks.
- Repository hygiene validation now splits NUL-delimited Git index paths
  correctly, detecting tracked forbidden cache and temporary files while
  continuing to ignore untracked runtime artifacts.
- Offline release/archive verification now rejects symlinked top-level assets,
  so a downloaded bundle cannot silently borrow its manifest, summary,
  provenance, or standalone archive metadata from outside the bundle.
- Offline release and archive verification now reject unsupported manifest and
  distribution versions, including Boolean values that compare equal to an
  integer in Python. Metadata-schema compatibility helpers use exact integers.
- Offline release and archive verifiers now hash the exact manifest bytes they
  parse, so reported audit digests cannot silently refer to a later file revision.
- Archive bundle generation and offline verification now measure byte counts
  from the same stable SHA-256 read, detecting observed file changes or
  replacements instead of trusting a separate size stat.
- Verified-local handoff manifest generation now shares the verifier's stable
  file fingerprint routine, preventing mismatched SHA-256/size declarations
  when a source file changes or is replaced during verification.
- Handoff verification counts bytes from the same stream used for SHA-256 and
  rejects files that change or are replaced during reading; verification
  evidence no longer relies on a separate pre-hash file-size measurement.

## 0.1.0 - current repository package version

### Added

- Installable `diogo-data-registry` package for Python 3.12–3.14.
- `data-registry` console entry point.
- Strict typed models for canonical, external, legacy, consumer, provenance,
  and lifecycle records.
- Stable typed `RegistryClient` read API.
- Checksum-verified immutable canonical fetch through the packaged client.
- Versioned machine-readable static registry distribution v1.

### Compatibility

- snapshot manifest v9 is current;
- historical manifest versions 1–9 remain supported for interpretation;

- Public package API version: **1**.
- Static distribution version: **1**.
- Historical snapshot-manifest versions recognized: **1–9**.

The repository does not yet publish a separate `v0.1.0` GitHub package-release tag; snapshot tags remain independent registry release identities.
