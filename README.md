# Data Registry

[![Data validation](https://github.com/DiogoRibeiro7/data/actions/workflows/data-validation.yml/badge.svg)](https://github.com/DiogoRibeiro7/data/actions/workflows/data-validation.yml)

A provenance-first, versioned data registry for reusable datasets and external
data sources used across research, analysis, teaching, and software projects.

**Documentation:** https://diogoribeiro7.github.io/data/  
**Current immutable snapshot:** `snapshot-2026.10.12`  
**Roadmap:** [ROADMAP.md](ROADMAP.md)

The registry is deliberately conservative. Data becomes canonical only when
source identity, redistribution rights, file integrity, metadata, and downstream
reuse are explicit. Everything else remains discoverable without pretending it
is safe to mirror or redistribute.

## What this repository provides

- **Canonical datasets** with verified SHA-256 checksums and explicit redistribution rights.
- **External source records** for authoritative upstream data that should not be mirrored automatically.
- **Consumer contracts** that pin downstream repositories to an exact registry commit, path, and checksum.
- **Legacy quarantine** for historical material whose provenance or redistribution status is unresolved.
- **Typed Python API and CLI** through the `diogo-data-registry` package.
- **Deterministic machine-readable catalogs and reports** for canonical, external, consumer, lifecycle, provenance-debt, and quality state.
- **Static distribution v1** for downstream automation.
- **Immutable snapshot releases** with manifest, summary, provenance, offline verification, and GitHub artifact attestations.
- **Archival and DOI-ready metadata** for eligible milestone snapshots.
- **External-source lifecycle state** including actionable/terminal resolution, moved sources, permanent disappearance, and legal withdrawal.

## Current baseline

The current published baseline is:

- snapshot: `snapshot-2026.10.12`
- commit: `f0545790a246782313ac38bb07918d35670bdfd3`
- snapshot manifest: **v8**
- public API: **v1**
- static distribution: **v1**
- Python: **3.12–3.14**

At that snapshot the registry contains:

- **4 canonical datasets**;
- **16 external source records**;
- **2 legacy quarantine packages**;
- **4 active canonical consumer relationships** across **3 repositories**;
- **100% canonical consumer coverage**;
- **0 actionable provenance/licensing debt items**.

Remaining provenance debt is retained as explicit terminal evidence rather than
silently reclassified as safe.

## Repository model

```text
datasets/       canonical datasets that satisfy the registry contract
external/       authoritative upstream sources and external-state metadata
consumers/      downstream dependencies on canonical registry files
legacy/         historical files preserved in quarantine
distribution/   versioned static machine-readable registry output
reports/        deterministic quality, provenance, lifecycle, and changelog state
schemas/        versioned JSON Schema contracts
archive/        archive/DOI identifier state
preservation/   preservation and disappearance policies
src/            installable Python client
docs/           policy, API, release, migration, and architecture documentation
scripts/        deterministic generation, validation, release, and audit tooling
tests/          repository and package contract tests
```

## Canonical datasets

Canonical datasets live under:

```text
datasets/<dataset-slug>/
├── README.md
├── metadata.yaml
├── raw/
└── derived/        # optional
```

A canonical dataset must have:

- verified source identity;
- explicit redistribution permission;
- immutable file identity and SHA-256 checksums;
- complete metadata and citation information;
- documented lineage for derived artifacts;
- a real reuse case when promoted from an external source.

Browse:

- [human-readable canonical catalog](datasets/CATALOG.md)
- [machine-readable canonical catalog](datasets/catalog.json)
- [data policy](docs/DATA_POLICY.md)
- [metadata specification](docs/METADATA.md)

Canonical promotion is intentionally difficult. Public availability alone is
not enough.

## External sources

[`external/`](external/) records authoritative upstream sources that are useful
across projects but should not automatically be copied into this repository.

External records can carry structured state such as:

- redistribution status;
- provenance-resolution status;
- terminal/actionable review state;
- blocker category;
- availability state;
- moved-source replacement URL;
- disappearance or legal-withdrawal status;
- known downstream consumers.

Browse:

- [human-readable external catalog](external/CATALOG.md)
- [machine-readable external catalog](external/catalog.json)

The external catalog is governed by
[`schemas/external-catalog-v1.schema.json`](schemas/external-catalog-v1.schema.json)
and is published byte-for-byte through
[`distribution/v1/external.json`](distribution/v1/external.json).

## Consumer relationships

[`consumers/`](consumers/) records downstream repositories that depend on
canonical dataset files.

Each active relationship pins:

1. the exact registry commit;
2. the canonical dataset path;
3. the expected SHA-256;
4. downstream evidence.

This avoids floating `main` URLs and makes dependency state reproducible.

See:

- [consumer guide](docs/CONSUMERS.md)
- [consumer catalog](consumers/CATALOG.md)
- [consumer contract health](docs/CONSUMER_HEALTH.md)

## Typed client and CLI

Install locally:

```bash
python -m pip install -e .
```

Then:

```bash
data-registry list
data-registry search climate
data-registry show world-bank-greenhouse-gas
data-registry external medium-crawlfeeds-corpus
data-registry debt --status terminal
data-registry lifecycle online-retail-ii
```

Add `--json` to supported read commands for machine-readable output.

The Python API exposes a deterministic offline `RegistryClient`:

```python
from pathlib import Path

from data_registry import RegistryClient

registry = RegistryClient(Path("."))
dataset = registry.canonical("online-retail-ii")
source = registry.external("medium-crawlfeeds-corpus")
debt = registry.provenance_debt(status="terminal")
```

Registry reads are offline. Network access occurs only for an explicit immutable
canonical fetch.

See:

- [CLI reference](docs/CLI.md)
- [Python API](docs/PYTHON_API.md)
- [client architecture](docs/CLIENT_ARCHITECTURE.md)
- [compatibility policy](docs/COMPATIBILITY.md)

## Using canonical data reproducibly

Consumers should pin:

1. exact 40-character registry commit;
2. canonical path;
3. expected SHA-256.

Do not build reproducible workflows around a floating default-branch raw URL.

The packaged client can fetch and verify canonical files:

```bash
data-registry fetch <dataset-id> \
  --file raw/example.csv \
  --commit <40-character-git-sha> \
  --output data/external/example.csv
```

Checksum mismatch is fatal.

## Machine-readable distribution

Versioned static registry output lives under:

```text
distribution/v1/
```

The public entry point is:

```text
https://diogoribeiro7.github.io/data/registry/v1/index.json
```

Most artifacts are copied byte-for-byte from deterministic committed sources.
The external artifact is required to remain byte-identical to
`external/catalog.json`.

See [Machine-readable registry distribution](docs/STATIC_DISTRIBUTION.md).

## Provenance, lifecycle, and trust

The registry keeps unresolved questions visible instead of hiding them.

Deterministic reports cover:

- provenance/licensing debt;
- canonical lifecycle and supersession;
- consumer migrations;
- registry quality and coverage;
- snapshot-to-snapshot changes;
- preservation eligibility.

Immutable snapshot releases include:

- `snapshot-manifest.json`;
- `snapshot-summary.md`;
- `snapshot-provenance.json`;
- offline verification support;
- GitHub artifact attestations;
- archive-ready metadata.

See:

- [provenance resolution](docs/PROVENANCE_RESOLUTION.md)
- [release policy](docs/RELEASES.md)
- [release verification and attestations](docs/ATTESTATION.md)
- [preservation policy](docs/PRESERVATION.md)
- [archiving and DOI workflow](docs/ARCHIVING.md)

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

Do not commit private, personal, confidential, regulated, or
redistribution-restricted data.

## Validation

Install dependencies and run:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/generate_external_catalog.py
python scripts/generate_consumer_catalog.py
python scripts/generate_provenance_debt.py
python scripts/generate_static_distribution.py
mkdocs build --strict
```

Generated artifacts are freshness-checked in CI.

## What this repository is not

This registry is not:

- a generic data dump;
- a personal data lake;
- a mirror of every public dataset;
- a mutable "latest data" bucket;
- a replacement for authoritative upstream providers;
- a place to store large files merely because Git permits it.

The durable rule is:

> identify reusable data, prove its provenance and redistribution basis, pin
> immutable bytes when justified, register real consumers, and preserve the
> resulting state through immutable snapshots.

## Citation

Use repository-level [`CITATION.cff`](CITATION.cff) for registry tooling and
see [citation guidance](docs/CITATION.md) for snapshot citations and upstream
dataset attribution.

## Licensing

This repository contains material under different licensing regimes.

- Repository-maintained tooling is covered by [LICENSE-CODE](LICENSE-CODE).
- Third-party and canonical dataset licensing is recorded per dataset/source.
- No repository-level licence overrides upstream dataset terms.

See [NOTICE.md](NOTICE.md) before redistributing data.

## History

The repository began as a small collection of project data files. In 2026 it
was rebuilt into a typed, provenance-first registry with explicit canonical,
external, consumer, legacy, lifecycle, preservation, and immutable-release
contracts.
