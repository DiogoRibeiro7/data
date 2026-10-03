# Phase-four legacy re-audit — 2026-10-03

This document records the second-pass review of the five packages that remained
in legacy quarantine after the 2026-10-01 resolution audit.

## country-age-sex-2019

**Decision: retain in legacy.**

### Evidence strengthened

The retained files are strongly consistent with **United Nations World
Population Prospects 2019 Revision** age/sex population data.

The key cross-check is `Portugal-2019_1.csv`:

- its male + female counts sum to **10,226,178**;
- WHO material citing **UN population prospects, 2019** reports the same
  Portugal 2019 total;
- current PopulationPyramid.net pages use WPP 2024 and report a different
  Portugal 2019 total, confirming revision drift.

UN WPP 2019 documentation also confirms that detailed age/sex outputs were
distributed through Excel/ASCII downloads and an interactive data-query system.

### Consumer search

Account-wide GitHub code search for distinctive filenames such as
`China-2019.csv`, `Portugal-2019_1.csv`, and `Portugal-2019.xlsx` found no
maintained consumer outside `DiogoRibeiro7/data`.

### Portugal lineage

The 5-year Portugal CSV and the broader-band Portugal CSV are closely related,
but the broader-band file is not a byte- or arithmetic-perfect aggregation:
small discrepancies remain in at least two grouped values.

The workbook relationship is still unproven.

### Licensing/provenance boundary

WPP 2019 publications are available under CC BY 3.0 IGO. However, the exact
retained artifacts cannot yet be tied to a specific authoritative UN download
URL or immutable export identity.

The registry therefore does **not** promote the files merely because the source
family is now highly likely.

### Remaining blockers

- exact historical download/export route not recovered;
- Portugal workbook lineage unresolved;
- broader-band Portugal CSV contains small discrepancies from direct grouping;
- exact file-level redistribution basis remains insufficiently evidenced.

No canonical promotion or external-source replacement is justified yet.


## portugal-covid19

**Decision: retain the MTSSS workbook; remove the orphaned ARS model output.**

### MTSSS workbook

`Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx` belongs to the 2020
**Indicadores COVID-19 MTSSS** monitoring-workbook series published by the
Gabinete de Estratégia e Planeamento (GEP) of the Portuguese Ministry of
Labour, Solidarity and Social Security.

The filename identifies the retained artifact as the **27 May 2020** snapshot.

The workbook is kept in legacy because the exact historical download URL,
dataset-specific redistribution terms, and immutable upstream identity have not
been recovered.

### Portugal_ARS.csv

The removed CSV contains regional statistical estimates and interval bounds
(`ML`, `Low_90`, `High_90`, `Low_50`, `High_50`) rather than raw
administrative observations.

Account-wide code search found no maintained consumer, and no generating code
or upstream source was recovered.

Keeping this file beside the source workbook would incorrectly mix raw source
material and derived model output, so the CSV is removed.

### Outcome

The package remains in legacy as a single-source workbook with a concrete
provenance/licensing blocker. No canonical or external promotion is justified
yet.


## portugal-population-2018

**Decision: replace the local workbook with an external PORDATA/INE source record.**

### Workbook evidence

The removed `populacao_residente_2018.xlsx` workbook contains one sheet,
`Planilha1`, with annual rows from 1970 through 2018.

Its columns are:

- total population;
- five-year age groups from `0-04` through `80-84`;
- `85 ou mais`.

The 2018 row totals **10,276,617** residents.

Office metadata records `OutSystemsApplications` as the creator, with the file
created on **2020-05-14** and last modified by Diogo Ribeiro.

The schema and values match the PORDATA resident-population table backed by INE
annual estimates. PORDATA also documents OutSystems as part of its platform,
which provides additional provenance evidence for the workbook export.

### Consumer search

Account-wide code search for `populacao_residente_2018.xlsx` found no
maintained consumer outside `DiogoRibeiro7/data`.

### Resolution

The workbook is an application-generated export rather than a durable,
immutable upstream artifact. Historical population estimates may also be
revised over time.

The local byte copy is therefore removed and replaced by:

`external/pordata-portugal-resident-population/`

Redistribution remains explicitly **unresolved** because the registry has not
recovered terms that clearly authorize mirroring the historical Excel export.

No canonical promotion is justified.


## portugal-sico-mortality

**Decision: replace the local historical export family with an external DGS mortality-platform record.**

### Evidence

The six retained CSV files share one schema and one snapshot naming convention,
covering complete years 2015-2019 plus a partial 2020 series.

The DGS services directory exposes both **DGS InfoClique - Plataforma da
Mortalidade** and **SICO - Sistema de Informação dos Certificados de Óbito**.

DGS documentation identifies SICO as a source used for mortality surveillance
and statistical analysis.

### Consumer search

Account-wide code search for the distinctive historical CSV filenames found no
maintained consumer outside this repository.

### Resolution

The local CSV exports are removed and replaced by:

`external/dgs-infoclique-mortality/`

The exact historical export route and immutable snapshot identity were not
recovered, and the current DGS site does not provide a clear redistribution
grant for mirroring those historical exports.

Redistribution is therefore recorded as **unresolved**.

No canonical promotion is justified.
