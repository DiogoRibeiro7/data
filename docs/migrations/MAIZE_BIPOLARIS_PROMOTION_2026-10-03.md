# Maize Bipolaris promotion review — 2026-10-03

## Outcome

The attempted canonical promotion of the maize Bipolaris disease-progress CSV
was **reversed** after review identified that dataset-specific redistribution
permission had not been established explicitly.

The source remains a pinned external record. The registry does not republish
the dataset bytes.

## Immutable source identity

- repository: `emdelponte/paper-hgam-curves`;
- commit: `d793d54c17ad404df2f6618d2681c993fcf144cf`;
- path: `maize_bipolaris.csv`;
- Git blob SHA-1: `433a2d1c37ba4f6069d04d8ffc9f7916f0a8adc3`;
- byte size: 53,293;
- SHA-256: `eb013e32ca60f7a80e2be10c91b6cac5df68f863ce24597ebf48ebd07ec9e705`;
- data rows: 1,105;
- columns: 5.

The existing copy in `DiogoRibeiro7/crop-protection-predictive-science` has
the same Git blob identity and byte length as this pinned upstream object.

## Licensing review

The pinned upstream README describes the repository as providing the **data and
computational workflow** and identifies `maize_bipolaris.csv` as the raw
dataset. The repository also contains a root MIT `LICENSE`.

However, the MIT notice itself grants rights over "software and associated
documentation files". The upstream snapshot does not explicitly state that the
raw dataset is licensed under MIT, and no separate dataset licence or explicit
redistribution grant was found.

That distinction is material for this registry: repository-level software
licensing is not treated automatically as dataset licensing.

Therefore:

- repository-level licence: MIT;
- dataset-specific redistribution: unresolved;
- canonical republication: not permitted by registry policy until clarified.

## Review findings

The promotion review also identified two implementation problems that become
moot once the canonical copy is removed:

1. the source CSV uses CRLF bytes while the repository's generic CSV
   `.gitattributes` rule normalizes line endings, creating a risk that a future
   Git add would change the byte identity;
2. the added dataset tests were module-level pytest-style functions, while the
   repository CI uses `unittest discover`, so those checks were not collected.

If a future promotion becomes permissible, both issues must be addressed before
the dataset is committed canonically.

## Registry state after correction

The correction:

- removes `datasets/maize-bipolaris-disease-progress/`;
- restores `external/maize-bipolaris-disease-progress/`;
- records redistribution as unresolved;
- regenerates canonical and external catalogs;
- preserves the immutable upstream commit, blob, size and SHA-256 metadata.

## What would unblock promotion

Canonical promotion may be reconsidered if one of the following is obtained:

1. an explicit dataset licence covering `maize_bipolaris.csv`;
2. an explicit statement from the dataset author that the repository MIT
   licence applies to the dataset;
3. another authoritative source with clear redistribution terms for the exact
   dataset.

Until then, downstream consumers should continue using their existing pinned
source arrangement rather than a registry-hosted canonical copy.

## Publication reference

The dataset accompanies Del Ponte's plant disease progress-curve work,
DOI `10.1094/PHYTO-01-26-0009-LE`.
