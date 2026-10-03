# UCDP Georeferenced Event Dataset (GED) 25.1

This is the second canonical dataset in the registry.

UCDP GED is the event-level geocoded dataset published by the Uppsala Conflict
Data Program. Version **25.1** covers organized-violence events from 1989
through 2024.

## Canonical source

- Publisher: Uppsala Conflict Data Program (UCDP), Uppsala University
- Version: **25.1**
- Official archive: https://ucdp.uu.se/downloads/ged/ged251-csv.zip
- Version codebook: https://ucdp.uu.se/downloads/ged/ged251.pdf
- UCDP extraction date recorded by the codebook: **2025-03-19**
- Retrieved for this registry: **2026-10-03**

The registry stores the official ZIP archive byte-for-byte rather than the
decompressed CSV. This preserves the exact upstream artifact while remaining
below GitHub's direct-Git size limit.

## Integrity

Canonical path:

`raw/ged251-csv.zip`

Archive size:

`29,307,888 bytes`

Archive SHA-256:

`e256f1fb20a579d8b2f910e5bae212f486d3002adaa2e4359ace740c737da05d`

The archive contains exactly one CSV:

`GEDEvent_v25_1.csv`

Contained CSV properties:

- size: **250,393,383 bytes**;
- SHA-256: `3f286de84cc0cb9152403f53e6aea2ac604d623f156e61079338596e09e8b550`;
- rows: **385,918** data rows;
- columns: **49**;
- minimum year: **1989**;
- maximum year: **2024**;
- first event date: **1989-01-01**;
- last event date: **2024-12-31**.

## Licence and redistribution

UCDP's download center states that its datasets are licensed under
**Creative Commons Attribution 4.0 International (CC BY 4.0)** and may be
redistributed provided the required attribution/citation is retained.

This satisfies the registry's canonical-storage requirement:
`redistribution: allowed`.

## Citation

UCDP GED 25.1 requires the version number to be reported in analyses.

Primary dataset citation:

> Sundberg, Ralph and Erik Melander (2013). *Introducing the UCDP
> Georeferenced Event Dataset*. Journal of Peace Research 50(4), 523-532.

Version-specific codebook:

> Högbladh, Stina (2025). *UCDP GED Codebook version 25.1*. Department of
> Peace and Conflict Research, Uppsala University.

See the official 25.1 codebook for the full citation guidance.

## Schema

The contained CSV has 49 fields, including event/conflict/dyad identifiers,
actors, location and geographic precision, dates, source information, and
fatality estimates.

The canonical archive is not transformed by this repository.

## External UCDP record

`external/ucdp-conflict-data/` remains intentionally present because UCDP
publishes several other datasets besides GED. Canonicalizing GED 25.1 does not
replace that broader source record.

## Consumer migration

`DiogoRibeiro7/displacement-risk-lab-dynamodb` currently downloads the
official GED 25.1 archive directly. Issue #65 will migrate that production path
to this canonical registry snapshot using an exact registry commit and SHA-256.
