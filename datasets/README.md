# Dataset catalog

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

## Catalog fields

As datasets are migrated, this page will list:

| Dataset | Domain | Snapshot | Source | License / terms |
| --- | --- | --- | --- | --- |

The catalog is intentionally empty until legacy files have been classified and migrated. Existing root-level files are legacy content and must not be treated as conforming to the new contract until their migration is complete.

## Adding a dataset

Before adding data:

1. read the [repository policy](../docs/DATA_POLICY.md);
2. verify provenance and redistribution terms;
3. create a stable dataset slug;
4. add a dataset README and `metadata.yaml`;
5. place source snapshots in `raw/`;
6. place only durable, documented transformations in `derived/`;
7. record SHA-256 checksums;
8. submit the dataset through review.

The metadata specification is documented in [Dataset metadata specification](../docs/METADATA.md), and migration rules are documented in [Dataset migration policy](../docs/MIGRATION.md).
