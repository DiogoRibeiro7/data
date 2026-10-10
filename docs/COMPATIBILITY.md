# Compatibility and versioning policy

This policy defines the compatibility contract for the installable registry
client, public Python API, registry schemas, static distribution, and immutable
snapshot manifests.

The Git repository remains the source of truth. Version numbers describe
interfaces and interpretation contracts; they do not make mutable data
snapshots acceptable.

## Package releases

The Python distribution is `diogo-data-registry`.

Package releases follow Semantic Versioning.

The initial packaged client is `0.1.0`. Before package version 1.0:

- patch releases fix bugs without intentionally breaking the documented public
  API;
- minor releases may introduce new public capabilities;
- an unavoidable breaking public API change requires both a package minor
  version bump and a `PUBLIC_API_VERSION` increment.

At and after package version 1.0, breaking public API changes require a package
major-version bump.

Repository commits and registry snapshot tags are independent of package
versions.

## Public Python API

The current public API contract is:

`PUBLIC_API_VERSION = 1`

The supported public surface is the documented package-root API and
`RegistryClient` behavior described in [Python API](PYTHON_API.md).

Within API version 1:

- documented methods, arguments, return meanings, and exported model fields are
  compatibility commitments;
- new optional methods, arguments with defaults, model types, or fields may be
  added without changing the API version;
- removing or renaming a public symbol, changing required arguments, changing a
  return type incompatibly, or changing documented error semantics requires a
  new API version;
- private helpers and undocumented implementation modules are not compatibility
  commitments.

### Deprecation window

A public API scheduled for removal must:

1. be documented as deprecated;
2. remain functional for at least one subsequent package minor release;
3. include the replacement path in release notes.

Removal may happen sooner only for a security, legal, privacy, or data-integrity
issue where continued behavior would be unsafe or misleading.

## Registry metadata schemas

Metadata schema versions are explicit in committed records.

Current schema versions:

- canonical metadata: v1;
- consumer metadata: v1;
- external metadata: v1;
- legacy metadata: v0.

A schema version may remain unchanged for a backward-compatible extension when
older readers can safely ignore the new optional field and existing records
remain valid.

Increase the schema version when a reader must interpret an existing field
differently, a previously optional field becomes required, an allowed value is
removed, or record structure changes incompatibly.

Readers must reject unsupported schema versions rather than silently coercing
them.

Schema versioning is independent of package, static-distribution, and snapshot
manifest versions.

## Static machine-readable distribution

The current static distribution contract is:

`STATIC_DISTRIBUTION_VERSION = 1`

Public v1 files live under:

`/registry/v1/`

A backward-compatible addition may add a new artifact or optional field while
preserving the meaning of existing v1 artifacts.

A breaking path, structure, or interpretation change requires a new
distribution version such as `v2`. Published v1 URLs must not be silently
repurposed to mean something incompatible.

The distribution is generated from committed repository state. It is not a
second source of truth.

## Snapshot manifest compatibility

Immutable snapshot releases have historically used manifest versions:

| Snapshot | Manifest version |
| --- | ---: |
| `snapshot-2026.10.02` | 1 |
| `snapshot-2026.10.03` | 1 |
| `snapshot-2026.10.04` | 2 |
| `snapshot-2026.10.05` | 3 |
| `snapshot-2026.10.06` | 4 |
| `snapshot-2026.10.07` | 5 |
| `snapshot-2026.10.09` | 6 |
| Phase 10 preservation snapshot | 8 |

The packaged compatibility contract currently recognizes manifest versions
**1 through 8**.

Historical snapshot manifests are immutable. New tooling must not rewrite an
old release into the current manifest shape.

When reading historical manifests, tooling should branch explicitly on
`manifest_version`. Unknown future versions must be rejected unless support
has been added deliberately.

A new snapshot manifest version is required when the manifest contract changes
in a way that cannot be represented as a backward-compatible additive field.

## Release notes and changelog

Package-facing changes are recorded in `CHANGELOG.md`.

Every package release should identify:

- package version;
- public API version;
- supported Python versions;
- added/deprecated/removed public APIs;
- schema compatibility changes;
- static distribution compatibility changes;
- snapshot-manifest compatibility changes.

Breaking changes must include migration instructions.

Registry snapshot release notes continue to describe the data/registry state at
an exact tag and commit. Package release notes describe client behavior. These
are separate release identities.

## Compatibility exceptions

Compatibility may be broken without the ordinary deprecation window only when
required to address:

- a security vulnerability;
- privacy or confidentiality exposure;
- invalid or dangerous integrity behavior;
- a licensing/legal constraint.

Such changes must be documented immediately and should minimize downstream
breakage where possible.
