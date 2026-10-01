# Legacy quarantine resolution audit

Date: 2026-09-30

This audit resolves every package that remained under `legacy/` after the initial repository reorganization.

## Outcome summary

| Package | Decision | Result |
| --- | --- | --- |
| `country-age-sex-2019` | retain in legacy | exact upstream revision and redistribution terms unresolved |
| `covid19-modeling` | remove obsolete project inputs | no consumers; mixed Kaggle/OWID/manual provenance; not a reusable registry dataset |
| `italy-covid19` | retain in legacy | workbook source and redistribution terms not recovered |
| `jhu-covid19-time-series` | replace with external source | all five files traced by Git blob identity to one JHU commit; CC BY 4.0 |
| `portugal-covid19` | retain in legacy | package mixes a traceable MTSSS workbook with an unattributed derived ARS estimate table |
| `portugal-population-2018` | retain in legacy | likely official statistics, but exact export/query and redistribution basis unresolved |
| `portugal-sico-mortality` | retain in legacy | DGS/SICO source family identified; exact export endpoint and redistribution terms unresolved |
| `r-example-datasets` | replace with external source | built-in R datasets; local CSV serialization redundant; no consumers |
| `telco-customer-churn` | replace with external source | IBM sample identified; local file equals IBM data after line-ending normalization; dataset-specific redistribution still unresolved |

After this resolution pass, legacy quarantine contains **five** packages instead of nine.

## Dependency audit

Account-wide code search for the distinctive legacy filenames found no current consumers outside `DiogoRibeiro7/data`.

The removed packages therefore do not break known repository consumers.

Generic filenames such as `train.csv` were evaluated as part of their containing legacy package rather than treated as globally unique identifiers.

## Package decisions

### country-age-sex-2019 — retain

The package contains 2019 male/female population counts by age band for multiple countries.

The structure is consistent with UN World Population Prospects-derived population-pyramid data, and PopulationPyramid.net exposes 2019 country pages sourced from UN WPP. However, the current historical pages use a newer WPP revision and do not reproduce the retained Portugal totals exactly.

The package also contains:

- two different Portugal CSV age-band variants;
- a Portugal workbook;
- no recorded original download URL or WPP revision.

**Blockers**

- exact upstream provider/download route not proven;
- historical UN WPP revision not recovered;
- redistribution terms for the exact historical snapshot not recorded;
- relationship between the Portugal workbook and the two CSV variants remains undocumented.

No promotion is justified.

### covid19-modeling — remove obsolete project inputs

The package is a mixed 2020 modeling bundle rather than one coherent reusable dataset:

- `train.csv` matches the schema and date range of the Kaggle **COVID19 Global Forecasting (Week 1)** competition, whose dataset is subject to competition rules;
- `full_data_logistic.csv` is a transformed/filtered COVID case table matching the early Our World in Data/WHO-style `full_data.csv` schema;
- `locations_population.csv` is a manually assembled population helper with mixed per-row provenance URLs.

The package has no current consumer and no durable cross-project identity.

**Decision:** remove the package rather than promote or mirror competition/mixed-source data.

### italy-covid19 — retain

Only `Dataset_Italy_COVID_19.xlsx` remains.

No authoritative source, retrieval URL, publication, or redistribution statement was recovered from repository history or public filename search.

Because the workbook may represent a unique historical snapshot, it is retained rather than deleted.

**Blockers**

- source publisher unknown;
- snapshot date/version not established;
- redistribution/licence unknown;
- workbook lineage unknown.

### jhu-covid19-time-series — replace with external source

The five files were traced to the JHU CSSE COVID-19 repository.

All five retained Git blob identities match the upstream files at commit:

`dd07d05ff02d8aea12cab868e8a36c0e31cadf66` (2020-06-08).

JHU documents the dataset under **CC BY 4.0** with attribution requirements.

Because the bytes are exactly recoverable from a pinned upstream commit and no consumers were found, the local legacy package is removed and replaced by:

`external/jhu-csse-covid19/`

### portugal-covid19 — retain

`Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx` can be associated with the 2020 COVID-19 monitoring-workbook series published by the Portuguese Ministry of Labour, Solidarity and Social Security / GEP.

However, `Portugal_ARS.csv` is a derived-looking regional estimate table with columns such as `ML`, `Low_90`, `High_90`, `Low_50`, and `High_50`, and its generating model/source was not recovered.

The package therefore has mixed lineage and cannot be treated as one canonical source.

**Blockers**

- exact historical MTSSS workbook URL/terms not pinned;
- `Portugal_ARS.csv` derivation and upstream inputs unknown;
- package-level redistribution terms unresolved.

### portugal-population-2018 — retain

The file name indicates a 2018 Portuguese resident-population workbook, but repository history does not identify the exact statistical query/export.

Public Portuguese population statistics are available from multiple official/secondary systems, so assigning INE, PORDATA, or another publisher without evidence would be speculative.

**Blockers**

- exact publisher/export route unknown;
- query dimensions and transformation history unknown;
- licence/redistribution terms for this workbook unknown.

### portugal-sico-mortality — retain

The file names and content identify aggregated mortality extracts associated with Portugal's **SICO — Sistema de Informação dos Certificados de Óbito**.

The Direção-Geral da Saúde is the responsible entity for the SICO data system and describes its statistical mortality role.

The retained files are daily aggregate cause-category tables for 2015–2020 with a snapshot naming date of `2020-05-31`.

**Blockers**

- exact public export endpoint/retrieval procedure not recovered;
- redistribution terms for the historical exported CSVs not established;
- no immutable upstream snapshot identifier is available.

The source family is now documented, but canonical promotion remains blocked.

### r-example-datasets — replace with external source

`InsectSprays` and `PlantGrowth` are built-in datasets distributed with R's base `datasets` package.

Official R documentation identifies their original published sources. R is distributed under `GPL-2 | GPL-3`.

The local files were merely CSV serializations and had no consumers. They are removed and replaced by:

`external/r-base-example-datasets/`

### telco-customer-churn — replace with external source

The retained file is the familiar IBM Telco Customer Churn sample.

Comparison with IBM's archived `data/Telco-Customer-Churn.csv` shows identical normalized content; the historical local copy differs only by CRLF versus LF line endings.

The IBM sample repository is archived and can be pinned, but dataset-specific redistribution terms are not explicit enough to claim that the repository's Apache-2.0 software licence automatically covers the data.

The duplicate local serialization is therefore removed and replaced by:

`external/ibm-telco-customer-churn/`

with redistribution recorded as unresolved.

## Canonical promotions

None.

This is intentional. Issue #22 is a resolution exercise, not a requirement to populate the canonical catalog.

## Remaining quarantine

After this change, only packages with concrete unresolved evidence remain:

- `country-age-sex-2019`;
- `italy-covid19`;
- `portugal-covid19`;
- `portugal-population-2018`;
- `portugal-sico-mortality`.
