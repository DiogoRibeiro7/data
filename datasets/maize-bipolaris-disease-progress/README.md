# Maize Bipolaris disease-progress data

This is the second canonical dataset in the registry.

It contains multi-environment southern corn leaf blight disease-progress
observations for maize hybrids used in the analysis accompanying Emerson M.
Del Ponte's 2026 Phytopathology paper.

## Source

- Publisher/author: Emerson M. Del Ponte
- Upstream repository: https://github.com/emdelponte/paper-hgam-curves
- Pinned commit: `d793d54c17ad404df2f6618d2681c993fcf144cf`
- Source path: `maize_bipolaris.csv`
- Upstream Git blob: `433a2d1c37ba4f6069d04d8ffc9f7916f0a8adc3`
- Retrieved for canonical promotion: 2026-10-03
- Source size: 53,293 bytes

The canonical file is preserved byte-for-byte from the pinned upstream Git
object.

## Variables

The source contains 1,105 observations and five columns:

- `Ambiente` — trial environment;
- `Hibrido` — maize hybrid;
- `DAE` — days after emergence;
- `Fenologia` — phenological stage;
- `Bipolaris` — southern corn leaf blight severity.

The registry does not rename, normalize, or otherwise transform these fields.

## Integrity

Canonical path:

`raw/maize_bipolaris.csv`

SHA-256:

`eb013e32ca60f7a80e2be10c91b6cac5df68f863ce24597ebf48ebd07ec9e705`

Git blob identity of the upstream source:

`433a2d1c37ba4f6069d04d8ffc9f7916f0a8adc3`

## Licence and redistribution

The pinned upstream repository README states that the repository provides the
**data and computational workflow**, identifies `maize_bipolaris.csv` as the
raw dataset, and identifies the repository `LICENSE` as MIT. No separate
dataset terms are declared in that snapshot.

For this immutable source snapshot, the registry therefore records
redistribution as allowed under the repository's MIT licence. The exact
upstream MIT notice is retained in `LICENSE.upstream.txt`.

The evidence and decision are documented in
`docs/migrations/MAIZE_BIPOLARIS_PROMOTION_2026-10-03.md`.

## Citation

> Del Ponte, E. M. (2026). From Scalar Summaries to Functional Comparisons:
> A Framework for Analyzing Plant Disease Progress Curves.
> *Phytopathology*, 116(8), 1188-1193.
> https://doi.org/10.1094/PHYTO-01-26-0009-LE

The upstream citation remains required when the dataset is used. A registry
snapshot citation is supplementary reproducibility information.

## Consumer migration

The maintained `crop-protection-predictive-science` repository currently has
a byte-identical committed copy. That consumer is intentionally migrated only
after this canonical promotion is merged, under issue #46.
