# Changelog

This changelog records changes to the installable `diogo-data-registry`
client. Immutable registry snapshot releases have their own release notes and
tags.

The format follows Keep a Changelog conventions and package versions follow
Semantic Versioning as defined in `docs/COMPATIBILITY.md`.

## [Unreleased]

### Added

- Deterministic `snapshot-provenance.json` release metadata binding snapshot identity, release-asset digests, producer workflow/generator identity, and client/distribution interface versions.
- Deterministic snapshot-to-snapshot diff tooling;
- snapshot manifest v7 consumer-relationship and provenance-debt identities for exact release diffs;

- Public compatibility constants for package API, static distribution, and
  supported historical snapshot-manifest versions.
- Explicit compatibility, deprecation, schema, distribution, and historical
  snapshot policy.

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

- snapshot manifest v7 is current;
- historical manifest versions 1–7 remain supported for interpretation;

- Public package API version: **1**.
- Static distribution version: **1**.
- Historical snapshot-manifest versions recognized: **1–7**.

The repository does not yet publish a separate `v0.1.0` GitHub package-release tag; snapshot tags remain independent registry release identities.
