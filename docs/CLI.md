# Registry CLI

The local registry CLI provides a lightweight interface over the repository's three data layers:

- canonical datasets under `datasets/`;
- external source records under `external/`;
- legacy quarantine packages under `legacy/`.

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
```

## Fetch a canonical file

Fetching is available only for canonical datasets.

```bash
python scripts/registry.py fetch <dataset-id> \
  --file raw/example.csv \
  --commit <40-character-git-sha> \
  --output data/external/example.csv
```

The CLI does **not** accept a checksum from the caller. It reads the expected SHA-256 from the canonical dataset's `metadata.yaml` and delegates downloading to the existing immutable fetch helper.

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
