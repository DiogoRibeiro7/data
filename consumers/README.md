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
- `deprecated` for a historical relationship retained for traceability. Deprecated records must remain structurally valid, but they are not required to match a currently live canonical dataset/path/checksum.

## Registered relationships

The initial Phase 5 backfill registers two active canonical consumers:

- `DiogoRibeiro7/Medium-Blog` → `online-retail-ii`;
- `DiogoRibeiro7/displacement-risk-lab-dynamodb` → `ucdp-ged-25-1`.

Generated views are committed under:

- `consumers/CATALOG.md` — human-readable relationship table;
- `consumers/catalog.json` — machine-readable relationship catalog;
- `consumers/dependency-graph.json` — both consumer → dataset and dataset → consumer views.

Regenerate them with:

```bash
python scripts/generate_consumer_catalog.py --write
```

CI checks that all three generated artifacts remain current.
