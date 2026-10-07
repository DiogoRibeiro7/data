# Dataset metadata specification

Every canonical dataset must contain `metadata.yaml`.

The metadata file is the machine-readable source of truth for discovery, provenance, licensing, and integrity checks.

## Required fields

```yaml
schema_version: 1

id: portugal-sico-mortality
title: Portugal SICO mortality data
description: >
  Short description of the dataset and its intended analytical use.

domain:
  - public-health
  - portugal

source:
  publisher: Example publisher
  url: https://example.org/dataset
  retrieved_at: 2026-09-30
  snapshot: "2020-05-31"

license:
  name: Example license
  url: https://example.org/license
  redistribution: allowed

citation:
  text: Example citation text
  url: https://example.org/citation

lifecycle:
  status: active

files:
  - path: raw/example.csv
    role: raw
    format: csv
    sha256: "<64 lowercase hexadecimal characters>"

lineage: []
```

## Field semantics

### `schema_version`

Integer version of this repository metadata contract. Start with `1`.

### `id`

Stable dataset identifier. It must match the dataset directory slug.

### `title`

Human-readable dataset title.

### `description`

Short description of the contents and intended use.

### `domain`

One or more lowercase tags describing the subject area.

### `source`

Required provenance information:

- `publisher`: upstream publisher, institution, or author;
- `url`: canonical source or landing page;
- `retrieved_at`: ISO date when the source snapshot was obtained;
- `snapshot`: upstream release, coverage date, version, or other stable snapshot identifier.

### `license`

- `name`: SPDX identifier when appropriate, otherwise the upstream license/terms name;
- `url`: canonical license or terms URL;
- `redistribution`: one of `allowed`, `restricted`, or `unknown`.

Datasets marked `restricted` or `unknown` must not include redistributed source bytes unless explicit permission has been documented.

### `citation`

Citation text and canonical citation URL when available. Use `null` only when no citation is provided by the source.

### `lifecycle`

Optional lifecycle metadata for a canonical dataset. If omitted, the dataset is
treated as `active`.

- `status`: one of `active`, `deprecated`, or `superseded`;
- `deprecated_at`: optional ISO date when deprecation became effective;
- `supersedes`: optional list of older canonical dataset IDs replaced by this dataset;
- `superseded_by`: canonical dataset ID that replaces this dataset; required when
  `status: superseded`;
- `migration_note`: optional non-empty guidance for consumers.

Lifecycle metadata never changes the bytes or identity of an existing canonical
snapshot. It only records which canonical representation is currently preferred.
Cross-dataset graph invariants such as cycles, missing targets, and ambiguous
replacement paths are validated separately by repository lifecycle validation.

### `files`

Every committed data file must be listed.

Each file record contains:

- `path`: path relative to the dataset directory;
- `role`: `raw` or `derived`;
- `format`: concise lowercase format identifier;
- `sha256`: SHA-256 checksum.

Optional useful fields include row count, column count, compression, encoding, and notes.

### `lineage`

Required as an empty list for datasets without derived artifacts.

For derived artifacts, each entry should identify the output, raw inputs, transformation code or method, relevant parameters, and transformation version.

## Formal schema

The canonical contract is defined by [`schemas/canonical-metadata-v1.schema.json`](https://github.com/DiogoRibeiro7/data/blob/main/schemas/canonical-metadata-v1.schema.json). See [Metadata schemas](SCHEMAS.md) for external/legacy schemas and schema evolution rules.

## Validation principles

Automated validation verifies:

- directory slug equals `id`;
- required fields are present;
- file paths exist;
- SHA-256 values match;
- no unregistered data files are committed;
- raw and derived roles match their directories;
- redistribution status is explicit;
- metadata uses the supported schema version.

Structural validation is performed with JSON Schema Draft 2020-12. Repository-specific semantic and integrity rules remain in `scripts/validate_repository.py`.
