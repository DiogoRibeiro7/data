# Registry client architecture

Phase 9 separates reusable registry behavior from repository-only command
wrappers before the client is packaged for external installation.

## Module boundary

### `data_registry.fetch`

Owns immutable canonical-file retrieval primitives:

- `DatasetReference`;
- exact repository/commit/path/SHA-256 validation;
- immutable raw URL construction;
- local SHA-256 calculation;
- verified-local-copy reuse;
- atomic download and checksum verification.

Network access occurs only when `fetch_dataset_file` is called explicitly.

### `data_registry.core`

Owns deterministic registry reads and lookups:

- registry entry discovery across canonical, external, and legacy layers;
- list/search/exact-ID lookup;
- consumer dependency graph reads;
- provenance/debt reads and filtering;
- lifecycle/replacement reads;
- canonical file metadata lookup;
- registry-aware composition of immutable fetch references.

These operations read committed repository files only. They do not perform
implicit network requests.

## Compatibility scripts

`scripts/registry.py` remains the repository CLI. It owns argument parsing,
human-readable rendering, and focused repository validation, but delegates
registry reads/lookups/fetch composition to `data_registry.core`.

`scripts/fetch_dataset.py` remains the direct fetch CLI and delegates the
fetch implementation to `data_registry.fetch`.

The scripts intentionally re-export the shared functions used by the existing
test suite and downstream repository workflows. This preserves current
behavior while eliminating a second implementation path.

## Repository-only code

Repository structural validation remains in
`scripts/validate_repository.py`. It is not part of the reusable client core
in this phase because it validates repository-maintainer invariants rather
than downstream registry consumption.

Report generators and snapshot publication also remain repository tooling.

## Next Phase 9 steps

This issue establishes a package-oriented module boundary only. It deliberately
does not yet define a released package API.

The following Phase 9 issues build on this exact layout:

- #148 — typed public registry models;
- #149 — installable package and console entry point;
- #150 — stable programmatic public API;
- #151 — packaged checksum-verified fetch;
- #153 — compatibility and versioning policy.

Packaging should consume `data_registry/` directly rather than moving or
copying this logic again.
