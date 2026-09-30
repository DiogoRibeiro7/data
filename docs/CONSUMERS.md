# Consuming canonical datasets

A project should consume a canonical dataset only after that dataset has been promoted under `datasets/<slug>/`.

At present the canonical catalog is empty. This document defines the contract for future consumers.

## Reproducibility contract

Every consumer must pin all four values:

1. repository, normally `DiogoRibeiro7/data`;
2. exact 40-character Git commit SHA;
3. canonical file path;
4. SHA-256 checksum from the dataset metadata.

Do not fetch data from an unpinned `main`, `master`, branch, or floating raw URL.

## Reference manifest

Copy `templates/consumer-dataset.yaml` into the consuming project and fill in the canonical values.

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

## Current consumer audit

As of 2026-09-30:

- `datasets/catalog.json` contains zero canonical datasets;
- account-wide GitHub code search found no exact consumer URL for `DiogoRibeiro7/data`;
- therefore there are no consumer repositories to migrate in issue #7.

The first real consumer migration should happen when the first dataset is promoted into `datasets/`.
