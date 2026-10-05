# ONS Explore Local Statistics: Gross median weekly pay

Canonical snapshot of the **Gross median weekly pay** indicator published by the
Office for National Statistics (ONS) Explore Local Statistics service.

## Why this dataset is canonical

This dataset was promoted in Phase 7 because a maintained downstream project,
`DiogoRibeiro7/city-wage-cost-global`, consumed the ONS CSV directly from a
floating GitHub `main` URL.

The registry now provides an immutable byte-for-byte snapshot with explicit
licensing, provenance and checksum identity.

## Upstream identity

- Publisher: Office for National Statistics
- Upstream repository: `ONSdigital/explore-local-statistics-data`
- Upstream commit: `005f2da64d498b80ef9579db17d82933f6119745`
- Upstream path: `gross-median-weekly-pay/gross-median-weekly-pay.csv`
- Upstream Git blob: `f7904856bac0accd44bfc731f2d188a4ab8a5237`
- Retrieved: **2026-10-05**

ONS documents Explore Local Statistics as a public dissemination service whose
indicator CSVs are generated and quality-assured through its reproducible data
pipeline.

## Canonical file

`raw/gross-median-weekly-pay.csv`

Properties:

- size: **894,555 bytes**
- data rows: **7,109**
- columns: **12**
- SHA-256:
  `285a76982afdfd38e9366535b43bf3e68c878ada7b819d722d2ec188c38eff17`
- encoding: UTF-8 with BOM
- line endings: CRLF, preserved from upstream

The dataset-specific `.gitattributes` rule disables text normalization for this
raw path so checkout does not change the canonical bytes.

## Licence and attribution

ONS material may be reused under the **Open Government Licence v3.0**, subject
to its conditions and attribution requirements.

Use the attribution:

> Source: Office for National Statistics licensed under the Open Government
> Licence v3.0.

The canonical metadata records `redistribution: allowed`.

## Schema

The upstream CSV uses 12 columns:

- `areacd`
- `areanm`
- `geography`
- `indicator`
- `period`
- `observation`
- `measure`
- `unit`
- `lci_95`
- `uci_95`
- `status`
- `notes`

The registry does not transform or reorder the upstream rows.

## Consumer

The first registered consumer is `DiogoRibeiro7/city-wage-cost-global`.
Its reproducible UK wage analysis should pin the registry commit, canonical
path, and SHA-256 rather than the upstream floating `main` URL.

## Update semantics

A future ONS refresh must be added as a new reviewed registry snapshot. This
file is immutable and must not be silently replaced with a newer ONS export.
