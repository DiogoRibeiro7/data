# UCDP GED 25.1 canonical promotion — 2026-10-03

## Decision

Promote **UCDP Georeferenced Event Dataset (GED) version 25.1** as the second
canonical dataset.

## Why this candidate

GED 25.1 satisfies the phase-four requirements that the previous maize
Bipolaris candidate could not:

- it has a real maintained consumer;
- the version is immutable and historically addressable;
- UCDP explicitly permits redistribution under CC BY 4.0;
- the official source artifact is stable and checksummable;
- the downstream consumer already targets this exact version.

## Authoritative source

- publisher: Uppsala Conflict Data Program, Uppsala University;
- version: 25.1;
- official archive: `https://ucdp.uu.se/downloads/ged/ged251-csv.zip`;
- version codebook: `https://ucdp.uu.se/downloads/ged/ged251.pdf`;
- codebook extraction date: 2025-03-19;
- registry retrieval date: 2026-10-03.

## Exact source identity

Official archive:

- filename: `ged251-csv.zip`;
- size: 29,307,888 bytes;
- SHA-256: `e256f1fb20a579d8b2f910e5bae212f486d3002adaa2e4359ace740c737da05d`.

Contained source CSV:

- filename: `GEDEvent_v25_1.csv`;
- size: 250,393,383 bytes;
- SHA-256: `3f286de84cc0cb9152403f53e6aea2ac604d623f156e61079338596e09e8b550`;
- rows: 385,918;
- columns: 49;
- year range: 1989-2024;
- event-date range: 1989-01-01 through 2024-12-31.

## Storage decision

The decompressed CSV exceeds the repository's 100 MiB direct-Git limit.

The canonical raw object is therefore the exact official ZIP archive. This
preserves upstream bytes without repackaging or transformation and keeps the
stored object within the repository's reviewed large-file range.

The canonical metadata records both archive and contained-CSV hashes so a
consumer can verify both transport and extracted data identities.

## Licence

UCDP's dataset download center states that its datasets are licensed under
**CC BY 4.0** and may be redistributed with citation.

Canonical metadata therefore records:

`redistribution: allowed`

Attribution and version-specific citation guidance are documented in the
dataset README.

## External-record boundary

The existing `external/ucdp-conflict-data/` record remains in place because
it represents the wider UCDP dataset family. It is not a duplicate byte store.

## Downstream

Issue #65 will migrate `displacement-risk-lab-dynamodb` from its direct
`ged251-csv.zip` download to an exact canonical registry commit + archive
SHA-256 contract.
