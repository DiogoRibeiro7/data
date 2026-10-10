# Machine-readable registry distribution

The registry publishes a versioned static JSON distribution for downstream
automation.

The Git repository remains the source of truth. Files under
`distribution/v1/` are generated deterministically from committed registry
state and must not be edited by hand.

## Public base URL

Version 1 is staged to GitHub Pages at:

`https://diogoribeiro7.github.io/data/registry/v1/`

Start with:

`https://diogoribeiro7.github.io/data/registry/v1/index.json`

The index records the distribution version, artifact paths, schema versions,
and the committed source-of-truth path for each artifact.

## Version 1 artifacts

| Artifact | Public path | Source |
| --- | --- | --- |
| Canonical catalog | `registry/v1/canonical.json` | `datasets/catalog.json` |
| Release changelog | `registry/v1/changelog.json` | `reports/registry-changelog.json` |
| External sources | `registry/v1/external.json` | `external/catalog.json` |
| Consumer relationships | `registry/v1/consumers.json` | `consumers/catalog.json` |
| Dependency graph | `registry/v1/dependencies.json` | `consumers/dependency-graph.json` |
| Legacy registry | `registry/v1/legacy.json` | `legacy/*/metadata.yaml` |
| Provenance debt | `registry/v1/provenance-debt.json` | `reports/provenance-debt.json` |
| Lifecycle state | `registry/v1/lifecycle.json` | `reports/lifecycle.json` |
| Registry quality | `registry/v1/registry-quality.json` | `reports/registry-quality.json` |

Except for the compact generated legacy catalog, existing machine-readable
registry artifacts are copied byte-for-byte into the distribution.

## Determinism and freshness

Generate the committed distribution with:

```bash
python scripts/generate_static_distribution.py --write
```

Verify freshness without changing files:

```bash
python scripts/generate_static_distribution.py
```

CI runs the freshness check. The documentation build stages the committed
bundle under `docs/registry/v1/` before MkDocs builds the Pages artifact.

Git and immutable registry snapshots remain the integrity boundary. The static
index is a discovery/versioning manifest rather than a second checksum contract.

## Versioning

`v1` is the static distribution contract version, not a mutable dataset
version. A breaking layout or interpretation change requires a new distribution
version rather than silently changing the meaning of v1.

Package/API, schema, and distribution compatibility rules are defined in
[Compatibility and versioning policy](COMPATIBILITY.md).
