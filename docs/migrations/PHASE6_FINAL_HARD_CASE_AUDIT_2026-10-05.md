# Phase 6 final hard-case audit — 2026-10-05

This audit closes the remaining unstructured provenance/licensing debt for:

- `maize-bipolaris-disease-progress`;
- `legacy/country-age-sex-2019`;
- `legacy/portugal-covid19`.

## Maize Bipolaris disease-progress data

**Final decision: terminal external licensing blocker.**

The exact upstream repository, commit, path, Git blob and SHA-256 are already
known. The repository root carries an MIT licence and its README identifies
`maize_bipolaris.csv` as data.

The remaining ambiguity is legal scope: the MIT text covers software and
associated documentation, while no authoritative statement was recovered that
explicitly applies those redistribution rights to the dataset bytes.

The record therefore remains external with `redistribution: unresolved` and a
terminal `dataset-vs-repository-licence-scope` blocker.

## country-age-sex-2019

**Final decision: terminal legacy quarantine.**

The retained files are strongly attributable to United Nations World Population
Prospects 2019. The WPP 2019 publication is made available under CC BY 3.0 IGO.

That source-family attribution is not enough to promote these exact artifacts:
the original download/export route is unrecovered, the Portugal workbook
relationship is unresolved, and the broader-band Portugal CSV contains small
differences from direct aggregation.

Reopen only if an authoritative UN export identity can be tied to the retained
files and the Portugal variant lineage can be reconstructed.

## portugal-covid19

**Final decision: terminal legacy quarantine.**

The retained workbook is attributable to the GEP/MTSSS `Indicadores COVID-19
MTSSS` monitoring series. Contemporary GEP material describes that series as a
regularly updated collection of labour-market and social-support indicators,
and later GEP material cites the same series.

The exact 27 May 2020 workbook URL, an immutable upstream identity, and
dataset-specific redistribution terms were not recovered. The historical export
route is therefore terminally unresolved.

## Debt result

After this audit:

- total debt items: **6**;
- structured evidence: **6**;
- unstructured debt: **0**;
- terminal items: **6**;
- actionable items: **0**.

No questionable bytes are promoted, externalized, or removed by this audit.
