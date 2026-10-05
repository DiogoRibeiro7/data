# Metadata schemas

Repository metadata is validated against versioned JSON Schemas in `schemas/`.

## Current schemas

| Layer | Schema | Metadata version |
| --- | --- | ---: |
| Canonical datasets | `schemas/canonical-metadata-v1.schema.json` | 1 |
| External source records | `schemas/external-metadata-v1.schema.json` | 1 |
| Consumer relationships | `schemas/consumer-metadata-v1.schema.json` | 1 |
| Legacy quarantine | `schemas/legacy-metadata-v0.schema.json` | 0 |

The JSON Schemas define structural requirements: required fields, types, enums, string patterns, URI/date formats, and whether unknown top-level fields are permitted.

The Python validator retains semantic checks that cannot be represented cleanly in JSON Schema, including:

- directory name equals metadata `id`;
- referenced files exist;
- canonical raw/derived roles match directory placement;
- SHA-256 and Git-blob identities match;
- canonical stored bytes require `redistribution: allowed`;
- derived files have lineage;
- undeclared files are rejected;
- duplicate stored bytes are detected;
- generated catalogs are current;
- consumer IDs/filenames match their directory relationship identity;
- canonical consumer dataset/path/checksum values agree with canonical metadata.

## Canonical metadata

Canonical metadata is intentionally strict. Unknown top-level fields are rejected.

If a new generally useful metadata field is required, update the schema and documentation rather than adding ad-hoc fields to one dataset.

## External metadata

External source records enforce a common discovery core:

- `schema_version`;
- `status`;
- `id`;
- `title`;
- `publisher`;
- `source_url`;
- storage/usage policy.

Known source-specific extensions such as `medium_blog`, `doi`, `source_commit`, and `source_path` are explicitly represented.

External metadata may also include an optional structured `resolution` block
for unresolved provenance, snapshot, lineage, or redistribution debt.

See [provenance and licensing resolution evidence](PROVENANCE_RESOLUTION.md).

## Consumer metadata

Consumer schema version 1 describes one downstream dependency on one canonical dataset.

The committed record lives at `consumers/<consumer-id>/<dataset-id>.yaml` and pins the
exact registry commit, canonical file path, and SHA-256. Repository validation resolves the
dataset and file against committed canonical metadata without network access.

Each record also carries downstream evidence through either a consumer commit or an evidence
URL. Consumer records describe dependency state; they are not executable fetch configuration.

## Legacy metadata

Legacy schema version 0 describes quarantine packages only. It is intentionally small and records enough information to preserve file identity and unresolved provenance/licensing state.

Legacy metadata may include the same optional `resolution` evidence block used
by external records. This lets a quarantine package distinguish an actionable
audit task from a terminal decision without changing its legacy status.

Legacy schema version 0 is not a weaker canonical schema and should never be used for new reusable datasets.

## Schema evolution

Schema versions are integer contracts.

A version change is required when an existing valid metadata document would need different interpretation or when a new required field changes the contract.

Examples that require a new version:

- renaming/removing a field;
- changing the meaning of a field;
- changing an optional field to required;
- changing allowed values incompatibly.

Backward-compatible clarifications do not require a new version when they leave all existing valid documents semantically unchanged.

When introducing a new schema version:

1. add a new schema file; do not silently rewrite the old contract;
2. update the validator to select the correct schema by layer/version;
3. add migration documentation;
4. migrate existing metadata deliberately;
5. update templates;
6. add tests for both supported and unsupported versions;
7. update release notes when the change affects consumers.

## Validation

Run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

JSON Schema validation is performed with Draft 2020-12 and URI/date format checking enabled.
