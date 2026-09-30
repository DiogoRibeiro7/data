# Portugal political–business affiliation data

> **Status:** external reference only — not a canonical dataset.

This record describes the two files currently stored in `DiogoRibeiro7/Portugal-Data` without copying their bytes into this repository.

## Contents

### `worms_12jan.json`

A structured affiliation/history dataset for named individuals. It contains:

- 130 named people;
- 443 government/municipal role records;
- 5 party-role records;
- 906 company/organisation-role records.

The records include names, political/government roles, party information, company affiliations, positions, and date ranges.

### `grouping.json`

A company/group normalization file containing 20 organisation groups and related-name aliases used by the affiliation dataset.

## Why the bytes are not migrated

The repository policy excludes automatic centralisation when provenance, redistribution rights, or handling of personal/sensitive material is unresolved.

For these files:

- no explicit redistribution licence was found in the source repository;
- the original upstream publisher/source has not been established with sufficient confidence;
- the data concerns named individuals and includes political-party/government affiliation information.

Therefore the files are **not** promoted into `datasets/` and are not duplicated under `legacy/`.

## Current source

- Repository: `DiogoRibeiro7/Portugal-Data`
- Source commit: `893f469cb4dd45fe02eb24424d0e3c261eacb802`
- `grouping.json`: Git blob `12e9f1f0a8596a8b5cc2cffe952fd66586f7fc0e`, 2,358 bytes
- `worms_12jan.json`: Git blob `d542a88e544262270d4e5b350a96027a66c84f1d`, 342,887 bytes

## Provenance note

A public-web search found text that closely matches entries in `worms_12jan.json`, but that is only a provenance lead. It does not establish an authoritative upstream publisher, an explicit licence, or permission to republish the structured dataset.

## Future promotion

Promotion into the canonical registry requires all of the following:

1. authoritative provenance;
2. explicit redistribution permission;
3. a review of whether public redistribution of the named-person affiliation data is appropriate;
4. canonical metadata and citation;
5. SHA-256 checksums for the promoted bytes.
