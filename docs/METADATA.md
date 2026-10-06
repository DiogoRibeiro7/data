# Dataset metadata specification

Every canonical dataset must contain `metadata.yaml`.

The metadata file is the machine-readable source of truth for discovery, provenance, licensing, and integrity checks.

## Required fields

```yaml
schema_version: 2

id: portugal-sico-mortality
family: portugal-sico-mortality
version: "2026-09-30"
lifecycle:
  state: active
  supersedes: null
  transitioned_at: null
  compatibility: null
  notes: "Initial canonical version."
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

files:
  - path: raw/example.csv
    role: raw
    format: csv
    sha256: "<64 lowercase hexadecimal characters>"

lineage: []
```

## Field semantics

### `schema_version`

Integer version of this repository metadata contract. Current canonical metadata uses `2`; v1 is retained only for historical snapshots.

### `id`

Stable immutable identifier for this canonical snapshot. It must match the dataset directory slug.

### `family`

Stable identifier shared by all canonical versions of the same dataset family.

### `version`

Human/machine-readable version identifier unique within the dataset family.

### `lifecycle`

Required lifecycle state for canonical metadata v2.

- `state`: `active`, `deprecated`, or `superseded`;
- `supersedes`: immediate predecessor dataset ID, or `null` for the first canonical version;
- `transitioned_at`: optional ISO date for a lifecycle transition;
- `compatibility`: optional compatibility/migration note;
- `notes`: optional lifecycle note.

Only `supersedes` is authored as the replacement edge. Reverse `superseded_by` lookup is derived from the registry graph.

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

The canonical contract is defined by [`schemas/canonical-metadata-v2.schema.json`](https://github.com/DiogoRibeiro7/data/blob/main/schemas/canonical-metadata-v1.schema.json). See [Metadata schemas](SCHEMAS.md) for external/legacy schemas and schema evolution rules.

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
