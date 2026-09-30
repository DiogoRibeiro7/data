# Data repository policy

This repository is the canonical home for reusable public datasets shared across analysis, research, teaching, and software projects.

It is a dataset registry, not a general-purpose artifact store.

## Dataset contract

Every canonical dataset must use a stable, lowercase, hyphen-separated slug:

```text
datasets/<dataset-slug>/
├── README.md
├── metadata.yaml
├── raw/
│   └── <source files>
└── derived/
    └── <derived files>
```

The `derived/` directory is optional. A dataset may contain multiple raw files when they belong to the same upstream dataset or snapshot.

## What belongs here

A dataset is a good candidate when it is:

- reusable by more than one project;
- public or redistributable;
- useful as a stable reference or reproducibility snapshot;
- documented well enough to identify its origin and meaning;
- suitable for versioned storage in Git or the repository's chosen external storage mechanism.

Examples include official public statistics, public research datasets, stable teaching datasets, and reusable reference tables.

## What stays in project repositories

Do not centralize:

- unit-test fixtures;
- tiny synthetic examples created specifically for one project;
- generated reports, model outputs, caches, logs, and temporary files;
- application state or configuration data;
- experiment artifacts that are meaningful only within one repository;
- datasets whose redistribution terms are unknown or restrictive;
- private, personal, confidential, sensitive, or regulated data.

A project may keep a small fixture derived from a canonical dataset when that fixture is required for fast, deterministic tests.

## Provenance and redistribution

Before adding third-party data, verify that redistribution is permitted.

Each dataset must document:

1. upstream publisher or author;
2. canonical source URL;
3. retrieval or snapshot date;
4. license or applicable terms;
5. citation, when available;
6. checksums for stored files.

If redistribution is not clearly permitted, store metadata and retrieval instructions instead of copying the source data.

## Raw and derived data

### Raw

Files under `raw/` are immutable source snapshots. They should preserve the upstream content as closely as practical.

Do not silently edit raw files to fix formatting, missing values, encodings, column names, or types.

### Derived

Files under `derived/` are produced from raw data by a documented transformation.

Each derived artifact must identify:

- its raw inputs;
- the transformation or script used;
- any important parameters;
- the transformation date or version;
- its checksum.

Derived files should be committed only when they provide durable cross-project value.

## Naming

Dataset directory names must:

- use lowercase ASCII where practical;
- use hyphens as separators;
- describe the dataset rather than a consuming project;
- remain stable after publication.

Examples:

```text
portugal-sico-mortality
jhu-covid19-time-series
telco-customer-churn
portugal-resident-population
```

Within `raw/`, preserve upstream filenames when doing so helps traceability. If an upstream filename is ambiguous, document it in the dataset README rather than silently changing its meaning.

## File-size policy

Git is appropriate for small and moderately sized, version-worthy datasets.

As a repository rule:

- files below 25 MB may normally be committed directly;
- files from 25 MB to 100 MB require an explicit reason and should be reviewed for a better distribution mechanism;
- files above GitHub's normal 100 MB limit must not be committed directly.

For large or frequently changing datasets, prefer one of:

- an authoritative upstream download;
- a versioned release asset;
- Git LFS when its operational trade-offs are acceptable;
- dedicated object/data storage.

The metadata record must state where the canonical bytes live.

## Versioning

Dataset snapshots are immutable. Updating an upstream dataset means adding a new snapshot or replacing a clearly documented rolling snapshot through a reviewed change.

Consumers should pin a repository tag, release, or commit plus an expected SHA-256 checksum. They should not depend on an unpinned default-branch raw URL for reproducible work.

## Catalog

The repository catalog is built from dataset metadata.

The human-readable entry point is `datasets/README.md`. Each dataset entry should expose its ID, title, domain, source, snapshot date, license/terms, and link to the dataset README.

A future machine-readable catalog may be generated from `metadata.yaml` files; dataset metadata remains the source of truth.
