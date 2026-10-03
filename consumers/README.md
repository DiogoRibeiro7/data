# Consumer registry

This directory records downstream dependencies on canonical datasets.

Each YAML file represents one consumer/dataset relationship:

```text
consumers/
  <consumer-id>/
    <dataset-id>.yaml
```

A consumer record is metadata only. It does not copy downstream code or data.

## Identity rules

- `consumer_id` must match the parent directory name.
- `dataset_id` must match the YAML filename stem.
- `consumer_repository` identifies the downstream GitHub repository.
- `registry_layer` is `canonical`.
- `registry_repository` is `DiogoRibeiro7/data`.
- `registry_commit` is an exact 40-character commit SHA.
- `path` must identify a file declared by the canonical dataset metadata.
- `sha256` must match that canonical file's checksum.
- every record must include either a downstream `consumer_commit` or an
  `evidence_url`.

The repository validator performs these checks offline against committed
canonical metadata.

## Status

Use:

- `active` for a current dependency;
- `deprecated` for a historical relationship retained for traceability.

Consumer records are added separately from the schema introduction. See Phase 5
issue #69 for the initial backfill.
