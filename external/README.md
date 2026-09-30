# External data references

This directory records reusable upstream datasets that are relevant to analysis projects but whose bytes are not stored in the canonical `datasets/` registry.

External references are appropriate when:

- the authoritative publisher should remain the byte source;
- local project files are derived extracts or snapshots;
- redistribution conditions make direct republishing undesirable;
- exact historical snapshot provenance is incomplete.

These records centralize provenance, licensing, citations, and source locations. They are not included in `datasets/catalog.json`.


## Catalog

Browse the generated external-source indexes:

- [human-readable catalog](CATALOG.md)
- [machine-readable catalog](catalog.json)

The catalogs are generated from `external/*/metadata.yaml`. Regenerate them with:

```bash
python scripts/generate_external_catalog.py --write
```

CI runs the generator in check mode and fails when either catalog is missing or stale.

A missing licence in the catalog is rendered as **Unresolved** rather than inferred from unrelated repository licensing.
