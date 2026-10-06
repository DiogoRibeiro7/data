# UNHCR Refugee Population Statistics — Global Trends 2024

Canonical immutable snapshot of the UNHCR Refugee Population Statistics
Database as shipped in version **2024.12.0** of the `refugees` R package.

## Why this dataset is canonical

Phase 7 identified a real maintained consumer:
`DiogoRibeiro7/displacement-risk-lab-dynamodb`.

That project previously called the live UNHCR population API directly. The live
API is useful for current data, but it is not an immutable reproducibility
contract. This registry snapshot freezes the Global Trends 2024 population
state instead.

## Upstream identity

- Database: UNHCR Refugee Population Statistics Database
- Package: `PopulationStatistics/refugees`
- Package version: **2024.12.0**
- Package commit: `5b1f3a14960441177e5f5dc1752d2416edcc388b`
- Upstream path: `data/population.rda`
- Upstream Git blob: `017d710c6a0a8c3229625ff56786db1d2d91f9ad`
- Release note: updated with **Global Trends 2024**
- Retrieved for this registry: **2026-10-05**

The package metadata identifies the database as published by UNHCR and records
UNHCR as copyright holder.

## Upstream build semantics

The package's committed `data-raw/rdf.R` documents how the population object is
built from the UNHCR Refugee Statistics API:

- endpoint: `/population/v1/population`;
- `coo_all=true`;
- `coa_all=true`;
- pagination in 10,000-row pages;
- type conversion after retrieval.

The canonical registry stores the resulting versioned package object rather
than re-querying the mutable API during validation.

## Canonical file

`raw/population.rda`

- size: **456,835 bytes**
- SHA-256:
  `261acf0b3efb5e87fddfe794ec1b5d42fe7bc7217d80990bd7ae0bce31524e52`
- Git blob:
  `017d710c6a0a8c3229625ff56786db1d2d91f9ad`

The bytes are copied exactly from the pinned upstream commit.

## Licence and attribution

The package is licensed under **Creative Commons Attribution 4.0
International (CC BY 4.0)**. UNHCR's Refugee Population Statistics Database
terms likewise require attribution.

Use:

> UNHCR Refugee Population Statistics Database

and retain the package/version identity when citing this snapshot.

## Consumer use

The downstream Python consumer will fetch this exact registry object, verify
its SHA-256, load the R data object, and select the desired year range locally.
For the Phase 7 reproducibility path, 2024 is the primary bounded year.

## Update semantics

This snapshot is immutable. Later UNHCR releases belong in a new reviewed
canonical snapshot rather than replacing these bytes.
