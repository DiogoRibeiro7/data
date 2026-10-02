# Second canonical dataset decision

## Decision

Select **maize Bipolaris disease-progress data** from the maintained
`DiogoRibeiro7/crop-protection-predictive-science` repository as the second
canonical dataset candidate.

This decision does not yet add dataset bytes. Promotion remains a separate,
reviewed change.

## Why this candidate

The dataset is already used by a real empirical workflow rather than only as a
fixture or example. The consumer repository treats it as an offline
reproducibility input and documents the exact upstream Git object identity.

The upstream source is:

- repository: `emdelponte/paper-hgam-curves`;
- dataset: `maize_bipolaris.csv`;
- domain: southern corn leaf blight / Bipolaris disease progression in maize;
- expected size: 53,293 bytes;
- expected columns: `Ambiente`, `Hibrido`, `DAE`, `Fenologia`,
  `Bipolaris`;
- upstream repository licence: MIT.

The existing registry already contains an external-source record for this
dataset, so provenance has previously been reviewed. Promotion would therefore
exercise the established external-to-canonical path rather than introduce an
unreviewed source.

## Current consumer

Primary maintained consumer:

- repository: `DiogoRibeiro7/crop-protection-predictive-science`;
- local path: `data/raw/maize_bipolaris.csv`;
- use: second empirical disease-progress case;
- execution model: committed raw input, reproducible without network access;
- recovery path: exact upstream commit/blob identity.

The downstream migration after canonical promotion should replace the
repository-local source copy with the standard immutable registry consumer
contract: exact registry commit, canonical path, and SHA-256 verification.

## Alternatives reviewed

### Richardson & Gent hop downy mildew field trial

This is also a strong real-data consumer in
`crop-protection-predictive-science`, with a DOI and documented provenance.
However, the currently recorded evidence does not establish dataset-specific
redistribution terms as explicitly as the maize Bipolaris source. It remains a
good future candidate after licensing is verified independently.

### Energy-cleanliness reference data

`nuclear_vs_wind_solar_cleanliness` has several reusable-looking tables, but
they combine derived project reference data with multiple third-party sources
and provider-specific terms. They are better audited source-by-source before
any canonical promotion.

### Productivity / taxation / inequality inputs

The project consumes multiple remote series from OWID, World Bank, OECD, FRED,
and related providers. These are useful external-source consumers, but there is
no single coherent redistributable dataset that is a better second canonical
candidate than maize Bipolaris.

## Promotion requirements

The follow-up promotion must:

1. verify the exact upstream commit and file identity again;
2. confirm the upstream MIT licence applies to the dataset bytes being
   redistributed;
3. copy the authoritative source bytes without analytical transformation;
4. compute and record SHA-256;
5. add complete canonical `metadata.yaml` and dataset documentation;
6. regenerate the canonical and external catalogs;
7. remove or replace the external record cleanly where appropriate;
8. migrate `crop-protection-predictive-science` to an immutable registry
   commit + SHA-256 before deleting its local duplicate.

## Outcome

Maize Bipolaris has the strongest combination of:

- real maintained consumer;
- explicit source identity;
- small, stable public dataset;
- documented upstream repository licence;
- existing registry provenance record;
- clear duplicate-removal benefit.

It is therefore the selected second canonical dataset candidate for phase four.
