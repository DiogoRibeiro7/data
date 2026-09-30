# Data Registry

A provenance-first registry for datasets and external data sources used across research, analysis, teaching, and software projects.

The registry deliberately separates three layers:

- **Canonical datasets** — reusable datasets that satisfy the repository contract for provenance, licensing, checksums, and metadata.
- **External sources** — authoritative upstream sources that are documented centrally but not mirrored automatically.
- **Legacy quarantine** — historical files retained for traceability while provenance or redistribution questions remain unresolved.

## Start here

- Browse the [canonical dataset catalog](generated/canonical-catalog.md).
- Browse the [external source catalog](generated/external-catalog.md).
- Review the [legacy quarantine inventory](generated/legacy-inventory.md).
- Use the [registry CLI](CLI.md) for local search, inspection, verification, and immutable canonical fetches.
- Read the [data policy](DATA_POLICY.md) before adding or promoting data.
- Read the [consumer guide](CONSUMERS.md) before wiring a project to canonical data.

## Design principles

The repository favors explicit provenance over convenience.

A file is not canonical merely because it is public, useful, or already committed somewhere else. Promotion requires documented source identity, redistribution terms, metadata, integrity checks, and a reproducible snapshot contract.

External-source records are first-class registry entries. They avoid unnecessary duplication while preserving discoverability, licensing context, and known consumer relationships.

Legacy data remains visible rather than being silently deleted or promoted without evidence.

## Validation

The repository validates:

- metadata schemas;
- file identity and checksums;
- raw/derived placement;
- lineage;
- duplicate stored bytes;
- generated catalog freshness;
- external source records;
- repository hygiene.

Run the same checks locally:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/generate_external_catalog.py
mkdocs build --strict
```

## Repository

Source code, metadata, schemas, and history live at [DiogoRibeiro7/data](https://github.com/DiogoRibeiro7/data).
