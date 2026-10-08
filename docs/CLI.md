# Registry CLI

## Installable client

The registry client is packaged as `diogo-data-registry` and exposes the
`data-registry` console command.

For local development:

```bash
python -m pip install -e .
data-registry list
```

The package supports Python **3.12, 3.13, and 3.14**.

For downstream use from a Git checkout, pin the exact repository revision in
your dependency tooling. Package release/version compatibility is defined in a
later Phase 9 issue.

`python scripts/registry.py ...` remains available as a compatibility wrapper
and calls the same packaged CLI implementation.


The local registry CLI provides a lightweight interface over the repository's three data layers plus the canonical consumer relationship graph:

- canonical datasets under `datasets/`;
- external source records under `external/`;
- legacy quarantine packages under `legacy/`;
- canonical consumer relationships generated from `consumers/`.

It runs directly from the repository and does not require a service or database.

## List entries

```bash
python scripts/registry.py list
python scripts/registry.py list --layer external
python scripts/registry.py list --json
```

Human-readable output is tabular. `--json` emits a stable machine-readable array.

## Search

Search covers IDs, titles, publishers, canonical descriptions, and canonical domain tags.

```bash
python scripts/registry.py search climate
python scripts/registry.py search portugal --layer legacy
python scripts/registry.py search world --json
```

Search is case-insensitive and deterministic.

## Show one entry

```bash
python scripts/registry.py show world-bank-greenhouse-gas
python scripts/registry.py show world-bank-greenhouse-gas --json
```

If the same ID exists in more than one layer, specify the layer:

```bash
python scripts/registry.py show example-id --layer external
```

The command refuses ambiguous IDs rather than silently choosing one.

## Verify one entry

```bash
python scripts/registry.py verify world-bank-greenhouse-gas
python scripts/registry.py verify country-age-sex-2019 --layer legacy --json
```

Verification reuses the repository validator logic:

- canonical entries: metadata schema, file declarations, checksums, placement, lineage, and redistribution rules;
- external entries: external metadata schema and directory/ID rules;
- legacy entries: quarantine metadata, file declarations, sizes, and Git blob identity.

The command is focused on the selected entry rather than performing a full-repository catalog check.

For complete CI-equivalent validation, continue to use:

```bash
python scripts/validate_repository.py
python scripts/generate_external_catalog.py
python scripts/generate_consumer_catalog.py
```


## Consumer relationships

List all registered canonical consumers:

```bash
python scripts/registry.py consumers
python scripts/registry.py consumers --json
```

Show one consumer and its canonical datasets:

```bash
python scripts/registry.py consumer medium-blog
python scripts/registry.py consumer medium-blog --json
```

Find which consumers use one canonical dataset:

```bash
python scripts/registry.py used-by online-retail-ii
python scripts/registry.py used-by online-retail-ii --json
```

Find which canonical datasets are used by one consumer:

```bash
python scripts/registry.py uses displacement-risk-lab-dynamodb
python scripts/registry.py uses displacement-risk-lab-dynamodb --json
```

These commands read the committed deterministic
`consumers/dependency-graph.json`. They do not query GitHub or rebuild the
graph on demand.

The graph includes active and deprecated relationships. Unknown consumer or
dataset IDs fail clearly rather than returning an ambiguous empty result.


## Dataset lifecycle and replacements

Lifecycle commands read the committed deterministic `reports/lifecycle.json`.
They do not rebuild the lifecycle graph and do not access the network.

Show lifecycle state for one canonical dataset:

```bash
python scripts/registry.py lifecycle unhcr-refugee-population-2024
python scripts/registry.py lifecycle unhcr-refugee-population-2024 --json
```

Resolve the direct and preferred terminal replacement:

```bash
python scripts/registry.py replacement <dataset-id>
python scripts/registry.py replacement <dataset-id> --json
```

The replacement response includes:

- lifecycle status;
- direct replacement;
- preferred terminal canonical dataset;
- full replacement chain;
- deprecation date;
- migration note.

Reverse lookup which datasets a canonical dataset supersedes:

```bash
python scripts/registry.py supersedes <dataset-id>
python scripts/registry.py supersedes <dataset-id> --json
```

This reports both direct predecessors and all transitive historical datasets
whose replacement chain reaches the selected dataset.

Unknown lifecycle dataset IDs fail explicitly rather than returning an empty
result.

## Provenance and licensing debt

The CLI can inspect the committed deterministic debt queue without network
access.

List all debt items:

```bash
python scripts/registry.py debt
python scripts/registry.py debt --json
```

Filter by layer, blocker category, or review status:

```bash
python scripts/registry.py debt --layer external
python scripts/registry.py debt --category redistribution-rights
python scripts/registry.py debt --status terminal
python scripts/registry.py debt --layer legacy --status terminal --json
```

Show one debt item:

```bash
python scripts/registry.py debt-show pordata-portugal-resident-population
python scripts/registry.py debt-show pordata-portugal-resident-population --json
```

These commands read `reports/provenance-debt.json`. They do not query remote
sources or regenerate the debt queue on demand.

## Fetch a canonical file

Fetching is available only for canonical datasets. The installed command and
the compatibility script use the same `RegistryClient.fetch()` implementation.

```bash
data-registry --root /path/to/data fetch <dataset-id> \
  --file raw/example.csv \
  --commit <40-character-git-sha> \
  --output data/external/example.csv

python scripts/registry.py fetch <dataset-id> \
  --file raw/example.csv \
  --commit <40-character-git-sha> \
  --output data/external/example.csv
```

The CLI does **not** accept a checksum from the caller. It reads the expected SHA-256 from canonical metadata and uses the same packaged fetch path as the Python API.

The operation requires:

- an exact 40-character commit SHA;
- a file declared in canonical metadata;
- a matching SHA-256 after download.

It will not fetch from a branch such as `main`.

Use `--force` only when intentionally replacing a mismatched existing destination.

JSON output is also available:

```bash
python scripts/registry.py fetch <dataset-id> \
  --file raw/example.csv \
  --commit <40-character-git-sha> \
  --output data/external/example.csv \
  --json
```

## Repository root

By default the CLI resolves the repository root relative to its own location.

For tests or alternate checkouts, use the global `--root` option before the command:

```bash
python scripts/registry.py --root /path/to/data list
```
