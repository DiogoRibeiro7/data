# Data Registry

[![Data validation](https://github.com/DiogoRibeiro7/data/actions/workflows/data-validation.yml/badge.svg)](https://github.com/DiogoRibeiro7/data/actions/workflows/data-validation.yml)

A curated registry for datasets and data sources used across analysis, research, teaching, and software projects.

**Documentation:** https://diogoribeiro7.github.io/data/  
**Roadmap:** [ROADMAP.md](ROADMAP.md)

The repository separates **canonical datasets**, **external source records**, **consumer relationships**, and **legacy quarantine material** so that provenance, licensing, reproducibility, and reuse remain explicit.

## Repository model

```text
datasets/   canonical datasets that satisfy the repository contract
external/   reusable upstream sources whose bytes are not mirrored here
consumers/  downstream dependencies on canonical registry files
legacy/     historical files awaiting or failing canonical promotion
docs/       policy, metadata, migration, and consumer documentation
templates/  metadata and consumer-reference templates
scripts/    validation and deterministic fetch tooling
tests/      repository-tooling tests
```

### Canonical datasets

Canonical datasets live under:

```text
datasets/<dataset-slug>/
├── README.md
├── metadata.yaml
├── raw/
└── derived/        # optional
```

A canonical dataset must have verified provenance, explicit redistribution terms, checksums, and complete metadata.

Browse:

- [human-readable catalog](datasets/CATALOG.md)
- [machine-readable catalog](datasets/catalog.json)
- [dataset policy](docs/DATA_POLICY.md)
- [metadata specification](docs/METADATA.md)

Canonical promotion remains conservative: data is added only when it meets the repository contract.

### External source records

[`external/`](external/) records authoritative upstream sources that are reusable across projects but should not be mirrored automatically.

Typical reasons include provider-specific licensing, large or mutable upstream datasets, or project snapshots that are better kept with the analysis that consumes them.

Browse:

- [external source catalog](external/CATALOG.md)
- [machine-readable external catalog](external/catalog.json)

### Consumer relationships

[`consumers/`](consumers/) records downstream repositories that depend on canonical dataset
files. Each relationship pins an exact registry commit, canonical path, and SHA-256 and is
validated against canonical metadata offline.

See [Consuming canonical datasets](docs/CONSUMERS.md) for the contract and
[canonical consumer catalog](consumers/CATALOG.md) for current adoption.

### Legacy quarantine

[`legacy/`](legacy/) contains historical data preserved for traceability.

Legacy files are **not canonical**. Their presence does not imply verified provenance, current relevance, or redistribution approval.

## Explore the registry locally

The repository includes a lightweight CLI for listing, searching, inspecting, and verifying all registry layers:

```bash
python scripts/registry.py list
python scripts/registry.py search climate
python scripts/registry.py show world-bank-greenhouse-gas
python scripts/registry.py verify world-bank-greenhouse-gas
```

Add `--json` to read commands for machine-readable output.

See [Registry CLI](docs/CLI.md) for the full command reference, including immutable canonical-data fetching.

## Using a canonical dataset

Consumers should pin:

1. the exact repository commit;
2. the canonical dataset path;
3. the expected SHA-256 checksum.

Do not build reproducible workflows around a floating `main` raw URL.

The reference fetch helper is:

```bash
python scripts/fetch_dataset.py \
  --commit <40-character-git-sha> \
  --path datasets/<dataset>/raw/<file> \
  --sha256 <expected-sha256> \
  --output data/external/<file>
```

See [Consuming canonical datasets](docs/CONSUMERS.md) for the complete contract.

## Adding or updating data

Start with [CONTRIBUTING.md](CONTRIBUTING.md).

Every proposed canonical dataset must document at least:

- upstream publisher and canonical source;
- retrieval/snapshot date;
- licence or redistribution terms;
- citation where available;
- raw versus derived status;
- SHA-256 checksums;
- lineage for derived artifacts.

Do not commit private, personal, confidential, regulated, or redistribution-restricted data.

## Validation

Install the lightweight development dependency and run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/generate_external_catalog.py
python scripts/generate_consumer_catalog.py
```

When canonical metadata changes, regenerate the catalogs first:

```bash
python scripts/validate_repository.py --write-catalog
```

CI checks metadata consistency, integrity, duplicate content, file-size policy, lineage, catalog freshness, and dataset-documentation links.

## Versioning and releases

Dataset snapshots are immutable. Consumers pin commits and checksums; repository releases provide human-readable snapshot milestones.

See [Release and snapshot policy](docs/RELEASES.md).

## Citation

Use the repository-level [`CITATION.cff`](CITATION.cff) for the registry tooling, and see [Citation guidance](docs/CITATION.md) for snapshot citations and upstream dataset attribution.

## Licensing

This repository contains material under different licensing regimes.

- Repository-maintained tooling is covered by [LICENSE-CODE](LICENSE-CODE).
- Third-party and canonical dataset licensing is recorded per dataset/source.
- No repository-level licence overrides upstream dataset terms.

See [NOTICE.md](NOTICE.md) before redistributing data.

## History

The repository originated as a small collection of project data files. In 2026 it was reorganized into a provenance-first dataset registry with explicit canonical, external, and legacy layers.
