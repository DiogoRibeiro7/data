# Maize Bipolaris canonical promotion audit — 2026-10-03

## Decision

Promote the maize Bipolaris disease-progress CSV from
`emdelponte/paper-hgam-curves` to the canonical registry.

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

## Licensing evidence

The pinned upstream README describes the repository as providing the **data and
computational workflow** for the paper. Its repository-structure section names
`maize_bipolaris.csv` as the raw dataset and names `LICENSE` as the MIT
License.

The same pinned snapshot contains no separate dataset licence or data-specific
terms. The repository-level MIT notice grants permission to copy, modify,
publish, distribute, sublicense, and sell copies subject to preservation of the
copyright and permission notice.

For this immutable repository snapshot, the registry treats the repository's
MIT licence as the declared terms covering the included raw dataset. The
upstream MIT notice is copied into the canonical package as
`LICENSE.upstream.txt`.

This is a snapshot-specific licensing decision. It does not claim that future
versions of the upstream repository will necessarily retain the same terms.

## Publication

The dataset accompanies:

Del Ponte, E. M. (2026). *From Scalar Summaries to Functional Comparisons:
A Framework for Analyzing Plant Disease Progress Curves*. Phytopathology,
116(8), 1188-1193. DOI `10.1094/PHYTO-01-26-0009-LE`.

## Registry changes

Promotion:

- adds `datasets/maize-bipolaris-disease-progress/`;
- preserves the exact source CSV without transformation;
- records SHA-256 and upstream Git identity;
- retains the upstream MIT notice;
- replaces the previous external-source record;
- regenerates canonical and external catalogs.

## Downstream migration

The consumer repository is not changed in this promotion.

Issue #46 will migrate `crop-protection-predictive-science` to an immutable
registry commit + canonical path + SHA-256 contract before its redundant local
copy is removed.
