# Phase 7 candidate discovery and promotion scoring — 2026-10-05

## Purpose

Phase 7 expands the canonical registry only from demonstrated downstream demand.
This audit ranks concrete public-data candidates already used by maintained
repositories and separates promotable datasets from sources that should remain
external for now.

## Scoring model

Each candidate is scored from 0 to 2 on six dimensions:

1. **real demand** — active maintained downstream use;
2. **licence clarity** — explicit redistribution basis for the exact data;
3. **immutable identity** — exact snapshot, commit, version or reproducible query;
4. **source stability** — durable upstream source and schema;
5. **reuse value** — value beyond a single one-off analysis;
6. **migration ease** — ability to replace floating/downstream copies with a
   commit/path/SHA-256 registry contract.

Maximum score: **12**.

A high score does not override a licensing blocker. Candidates with ambiguous
redistribution rights remain external regardless of demand.

## Ranked candidates

| Rank | Candidate | Demand | Licence | Identity | Stability | Reuse | Migration | Total | Decision |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | ONS Explore Local Statistics — gross median weekly pay | 2 | 2 | 2 | 2 | 1 | 2 | **11** | promote |
| 2 | UNHCR Refugee Population Statistics | 2 | 2 | 1 | 1 | 2 | 1 | **9** | promote |
| 3 | Turing Change Point Dataset subset | 2 | 0 | 2 | 2 | 1 | 2 | **9** | defer |
| 4 | Our World in Data Grapher datasets | 2 | 1 | 1 | 1 | 2 | 1 | **8** | defer |
| 5 | FRED economic series | 2 | 0 | 1 | 1 | 2 | 1 | **7** | defer |

## 1. ONS Explore Local Statistics — gross median weekly pay

### Demand evidence

`DiogoRibeiro7/city-wage-cost-global` downloads:

`ONSdigital/explore-local-statistics-data/main/gross-median-weekly-pay/gross-median-weekly-pay.csv`

The notebook uses the file as a core input to the UK wage/cost analysis and
currently relies on a floating `main` URL.

### Why it is first

- real maintained consumer;
- GitHub-hosted upstream supports an exact commit and file path;
- compact CSV;
- official ONS source;
- straightforward migration from floating upstream URL to exact registry
  commit/path/SHA-256.

### Promotion target

Promote the exact upstream CSV from a pinned ONS commit and register
`city-wage-cost-global` as the first canonical consumer.

## 2. UNHCR Refugee Population Statistics

### Demand evidence

`DiogoRibeiro7/displacement-risk-lab-dynamodb` contains a live ingestion
helper for:

`https://api.unhcr.org/population/v1/population/`

with optional year bounds.

### Why it is promotable

- explicit CC BY 4.0 terms already established in Phase 6;
- existing real downstream use;
- strong reuse value for displacement analysis;
- attribution requirements are known.

### Remaining design work

The API is live and mutable. Promotion therefore needs a bounded query and an
exact captured payload/serialization contract. The canonical object should be a
well-defined snapshot, not an alias for "latest UNHCR data".

## Deferred candidates

### Turing Change Point Dataset

`cpd-stress-test` downloads several TCPD benchmark JSON files from a floating
GitHub `master` path.

Demand and immutable Git identity are strong, but the TCPD source record
explicitly notes that licensing is **dataset-specific** and some files cannot be
redistributed. The benchmark subset should remain external until each selected
file has an explicit redistribution basis.

### Our World in Data / Grapher

Multiple maintained repositories download OWID Grapher CSVs, including
`crisis_wealth_dynamics`, `ccs-scale-gap`, and
`productivity_taxation_inequality_project`.

Demand is strong, but OWID mixes its own material with third-party datasets and
the registry intentionally records redistribution as dataset-specific. A future
promotion should target one exact Grapher dataset only after verifying its
dataset-level terms and stable snapshot identity.

### FRED economic series

`gdp_prediction` and other projects consume FRED series through the API.

FRED is a source platform rather than one homogeneous licensing unit. Rights
can depend on the underlying series/provider, and a live API query does not
itself define a stable canonical snapshot. Promotion should be evaluated
series-by-series, not at collection level.

## Other observations

The account-wide scan also found direct public-data downloads that are not part
of this first batch, including Inside Airbnb, Northwind example CSVs, and ONS
housing-affordability data. These may become later Phase 7 candidates if a
maintained consumer and clear canonical-use case justify them.

The ONS housing-affordability file is particularly close to the selected weekly
pay candidate, but promoting both simultaneously would couple Phase 7 to one
analysis domain. The first batch deliberately keeps the target at two datasets
from different domains.

## Phase 7 promotion order

1. promote ONS gross median weekly pay;
2. migrate and register `city-wage-cost-global`;
3. promote a bounded UNHCR population snapshot;
4. migrate and register `displacement-risk-lab-dynamodb`;
5. audit downstream redundant copies/floating URLs;
6. update expansion quality safeguards;
7. publish the Phase 7 immutable snapshot.

## Decision

Proceed with issues #104 and #103.

Do **not** promote TCPD, OWID, or FRED in the initial Phase 7 batch. Their
deferred status is intentional and should only change after dataset-specific
licensing and immutable-identity evidence improve.
