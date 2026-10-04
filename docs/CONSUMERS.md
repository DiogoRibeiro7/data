# Consuming canonical datasets

A project should consume a canonical dataset only after that dataset has been promoted under `datasets/<slug>/`.

This document defines both the downstream reproducibility contract and the central registry record used to describe canonical consumers.

## Reproducibility contract

Every consumer must pin all four values:

1. repository, normally `DiogoRibeiro7/data`;
2. exact 40-character Git commit SHA;
3. canonical file path;
4. SHA-256 checksum from the dataset metadata.

Do not fetch data from an unpinned `main`, `master`, branch, or floating raw URL.

## Central consumer registry

Canonical consumer relationships are recorded centrally under:

```text
consumers/<consumer-id>/<dataset-id>.yaml
```

Each record pins the exact registry commit, canonical path, and SHA-256, and identifies the
downstream repository plus evidence of the migration. The central record is validated offline
against canonical metadata.

The registry currently records two active canonical relationships:

- `DiogoRibeiro7/Medium-Blog` → `online-retail-ii`;
- `DiogoRibeiro7/displacement-risk-lab-dynamodb` → `ucdp-ged-25-1`.

Browse the generated [canonical consumer catalog](../consumers/CATALOG.md) or use
the registry CLI's `consumers`, `consumer`, `used-by`, and `uses` commands.

## Reference manifest

`templates/consumer-dataset.yaml` now mirrors the formal consumer-record schema. It can be used
as a starting point when adding a central consumer relationship.

## Reference fetch helper

The reference implementation is `scripts/fetch_dataset.py`.

Example:

```bash
python scripts/fetch_dataset.py \
  --commit 0123456789abcdef0123456789abcdef01234567 \
  --path datasets/example-dataset/raw/example.csv \
  --sha256 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --output data/external/example.csv
```

The helper refuses branch names and short SHAs, verifies SHA-256 before accepting a download, writes atomically, reuses an already verified local copy without network access, and refuses to overwrite a mismatched file unless `--force` is explicit.

## Offline and CI policy

- Keep small deterministic test fixtures local.
- Fetch full canonical data only for integration or reproduction workflows that need it.
- Allow a previously verified local copy to satisfy offline runs.
- Never silently fall back to a different dataset version.
- Treat checksum mismatch as fatal.

CI should test the fetch helper with a local HTTP fixture rather than repeatedly downloading the real dataset.

## Removing old copies

Only remove a project's old full dataset copy after:

1. the canonical dataset is promoted;
2. the consumer pins a commit and SHA-256;
3. all code and notebook paths are updated;
4. the consumer passes its tests and reproducibility checks;
5. intentionally local small fixtures are retained.

A project may deliberately retain a full immutable snapshot when offline scientific reproducibility or packaging requires it. Document why it exists and verify its identity instead of deleting it mechanically.

## Current adoption

Both canonical datasets currently have at least one registered active consumer.
Consumer adoption is measured from formal `consumers/` records, not from
free-form external-source annotations.

The deterministic reverse dependency graph is committed at
`consumers/dependency-graph.json`, and active contracts are monitored by the
scheduled/manual consumer health workflow.
