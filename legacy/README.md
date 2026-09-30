# Legacy data quarantine

This directory contains data that previously lived directly at the repository root.

The files are organized by logical group, but they are **not canonical datasets yet**. They remain quarantined until provenance, redistribution terms, and integrity metadata are verified.

```text
legacy/<group>/
├── README.md
├── metadata.yaml
└── raw/
```

The legacy metadata files intentionally use `schema_version: 0`.

See [INVENTORY.md](INVENTORY.md) for the migration record.
