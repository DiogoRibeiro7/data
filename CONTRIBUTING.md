# Contributing

Contributions should improve the registry without weakening provenance, licensing, or reproducibility.

## Workflow

1. Work from `main` on a focused branch.
2. Make one coherent data or policy change.
3. Run the repository validation and tests.
4. Open a pull request.
5. Do not merge until validation passes and the data contract is satisfied.

Suggested branch prefixes:

- `data/<dataset-slug>`
- `source/<source-slug>`
- `docs/<topic>`
- `chore/<topic>`

## Propose before committing data

Before adding new dataset bytes, open the appropriate proposal:

- [Canonical dataset proposal](https://github.com/DiogoRibeiro7/data/issues/new?template=dataset-proposal.yml) — use when you think the bytes should live under `datasets/`.
- [External source proposal](https://github.com/DiogoRibeiro7/data/issues/new?template=external-source-proposal.yml) — use when the authoritative publisher should remain the byte source.

The proposal stage is where we decide whether a candidate should become canonical, be recorded as an external source, stay project-local, or be rejected.

Do not commit or attach candidate dataset bytes until the proposal is reviewed and canonical storage is approved. Never commit private, personal, confidential, credential-bearing, or redistribution-restricted data. Sensitive or regulated data requires an explicit approved publication basis.

## Adding a canonical dataset

Use the structure:

```text
datasets/<dataset-slug>/
├── README.md
├── metadata.yaml
├── raw/
└── derived/        # optional
```

Start from [`templates/metadata.yaml`](templates/metadata.yaml).

Before committing bytes, verify that redistribution is permitted.

A canonical submission must include:

- a stable lowercase hyphenated dataset ID;
- title and description;
- domain tags;
- upstream publisher;
- canonical source URL;
- retrieval date and snapshot/version;
- explicit licence or terms URL;
- redistribution status;
- citation when available;
- a metadata entry for every data file;
- SHA-256 for every data file;
- lineage for every derived artifact.

Raw files should preserve source bytes as closely as practical. Do not silently clean or reinterpret source files inside `raw/`.

## External source records

Use `external/<source-slug>/` when the upstream provider should remain the byte source.

An external source record should explain:

- what the source provides;
- who publishes it;
- where it can be obtained;
- what licence/terms apply;
- which projects consume it, when useful;
- why the bytes are not mirrored here.

## Legacy material

Do not promote a legacy package merely because its filenames look useful.

Promotion requires the same provenance, licensing, and integrity evidence as a new canonical dataset.

## Derived data

Derived artifacts belong in `derived/` only when they have durable cross-project value.

Metadata lineage must identify:

- output path;
- source inputs;
- transformation method or code;
- relevant parameters/version.

Project-specific model outputs, reports, caches, and experiment artifacts should remain in their owning project.

## Files that do not belong here

Do not add:

- private or personal data;
- credentials or secrets;
- confidential/company datasets;
- regulated or sensitive records without an explicit approved publication basis;
- test fixtures that belong to one project;
- generated reports and model artifacts;
- caches;
- data with unknown redistribution rights as canonical bytes.

## File size

Follow [the repository policy](docs/DATA_POLICY.md):

- below 25 MiB: normally acceptable in Git;
- 25–100 MiB: requires explicit storage review;
- above 100 MiB: do not commit directly.

Do not introduce Git LFS automatically. Decide storage deliberately for each large dataset.

## Catalogs

Canonical metadata is the source of truth.

After adding or changing a canonical dataset:

```bash
python scripts/validate_repository.py --write-catalog
```

Commit both generated files:

- `datasets/CATALOG.md`
- `datasets/catalog.json`

## Validation

Run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

## Pull request checklist

- [ ] Provenance is documented.
- [ ] Redistribution is permitted.
- [ ] Upstream terms are not overwritten by repository licensing.
- [ ] Metadata is complete.
- [ ] Checksums are correct.
- [ ] Raw/derived placement is correct.
- [ ] Derived lineage is documented.
- [ ] No private, sensitive, generated, or cache data was added accidentally.
- [ ] Catalogs were regenerated when needed.
- [ ] Tests and validation pass.
