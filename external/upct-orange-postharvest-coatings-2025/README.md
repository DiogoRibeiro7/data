# UPCT citrus postharvest dataset: orange empirical source record

Source: [Zenodo 16423047](https://zenodo.org/records/16423047), accompanying
[Martínez-Zamora et al. (2025)](https://doi.org/10.3390/foods14152616),
*Carnauba Wax Coatings Enriched with Essential Oils or Fruit By-Products Reduce
Decay and Preserve Postharvest Quality in Organic Citrus* (*Foods* 14, 2616).

The original `README.txt` names Lorena Martínez-Zamora at the Universidad
Politécnica de Cartagena, records collection in 2022--2024, identifies the
laboratory context, and explicitly declares **CC BY 4.0**. The central registry
records authoritative source URLs and independently checked MD5/SHA-256
digests; it does **not** store duplicate CSV content.

## Verified source and consumer

The new, standalone [`citrus_postharvest_empirical` project](https://github.com/DiogoRibeiro7/ds-projects-portfolio/pull/696)
vendors these three small files byte-for-byte, with a reproducible R parser
and checksums. Details and all digests are in [metadata.yaml](metadata.yaml).

The scope is deliberately limited to **oranges** and to three distinct
measurement panels:

- `Quality Data.csv` orange firmness: 200 separate observations, days
  0/5/10/15, 10 per treatment/day.
- Same CSV, orange weight loss: 60 separate observations, days 5/8/10/15,
  three per treatment/day; data are side-by-side, *not* fruit-matched.
- `in vivo data.csv` orange decay/sporulation: five treatment groups with
  three 20-orange boxes each, counts at days 5/7/10; experimentally
  inoculated, **not** observed natural storage failure.

The five groups are unwaxed (`CTRL`), carnauba wax (`CTRL-W`) and three waxes
enriched with fruit by-products (`AVOCADO`, `ORANGE`, `GRAPEFRUIT`). The latter
`ORANGE` label is a treatment, not another species field.

## Reuse and scientific limits

The original license permits redistribution with attribution; no license
inference is needed. The consumer retains an unchanged local snapshot for
offline, checksum-enforced reproducibility and uses **base R**. There are no
invented storage-day zeros, no row-by-row pairing of distinct outcomes, no
economic or price series, and no claim that an inoculation study identifies
commercial shelf life, population causal effects, or optimal selling days.

The lemon and in-vitro data in the wider original deposit remain outside the
scope of this registry consumer. A future wider study needs its own protocol.
