# Dataset registry

This directory contains the canonical datasets maintained by this repository.

Each dataset uses a stable slug and follows the repository contract documented in [Data repository policy](../docs/DATA_POLICY.md).

## Layout

```text
datasets/
└── <dataset-slug>/
    ├── README.md
    ├── metadata.yaml
    ├── raw/
    └── derived/        # optional
```

Legacy, not-yet-verified material lives under `legacy/` and is deliberately excluded from this canonical registry.

## Catalogs

- [`CATALOG.md`](CATALOG.md) is the generated human-readable catalog.
- [`catalog.json`](catalog.json) is the generated machine-readable catalog.

Both are generated from canonical `metadata.yaml` records and must not be edited by hand.

Regenerate them with:

```bash
python scripts/validate_repository.py --write-catalog
```

Then run validation without the write flag:

```bash
python scripts/validate_repository.py
```

## Adding a dataset

Before adding data:

1. read the [repository policy](../docs/DATA_POLICY.md);
2. verify provenance and redistribution terms;
3. create a stable dataset slug;
4. add a dataset README and `metadata.yaml`;
5. place source snapshots in `raw/`;
6. place only durable, documented transformations in `derived/`;
7. record SHA-256 checksums for every canonical data file;
8. regenerate both catalogs;
9. run the validator and its tests;
10. submit the dataset through review.

The metadata specification is documented in [Dataset metadata specification](../docs/METADATA.md), and migration rules are documented in [Dataset migration policy](../docs/MIGRATION.md).

## Validation

CI checks:

- canonical metadata structure;
- source, license, redistribution, and citation fields;
- referenced-file existence;
- SHA-256 integrity for canonical data;
- Git-blob integrity for legacy quarantine data;
- duplicate file contents;
- raw/derived placement and lineage;
- undeclared data files;
- generated/cache files;
- repository file-size policy;
- relative links inside dataset documentation;
- catalog freshness.

The validator is intentionally lightweight: Python plus PyYAML, with no data-science runtime dependency.
