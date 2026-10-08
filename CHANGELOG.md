# Changelog

This changelog records changes to the installable `diogo-data-registry`
client. Immutable registry snapshot releases have their own release notes and
tags.

The format follows Keep a Changelog conventions and package versions follow
Semantic Versioning as defined in `docs/COMPATIBILITY.md`.

## [Unreleased]

### Added

- Public compatibility constants for package API, static distribution, and
  supported historical snapshot-manifest versions.
- Explicit compatibility, deprecation, schema, distribution, and historical
  snapshot policy.

## [0.1.0] - 2026-10-08

### Added

- Installable `diogo-data-registry` package for Python 3.12–3.14.
- `data-registry` console entry point.
- Strict typed models for canonical, external, legacy, consumer, provenance,
  and lifecycle records.
- Stable typed `RegistryClient` read API.
- Checksum-verified immutable canonical fetch through the packaged client.
- Versioned machine-readable static registry distribution v1.

### Compatibility

- Public package API version: **1**.
- Static distribution version: **1**.
- Historical snapshot-manifest versions recognized: **1–5**.

[Unreleased]: https://github.com/DiogoRibeiro7/data/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DiogoRibeiro7/data/releases/tag/v0.1.0
