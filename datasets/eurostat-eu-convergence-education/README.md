# Eurostat: GDP per head, labour productivity and adult education in the EU, 1975-2025

Canonical snapshot of four Eurostat API responses that place every EU member
state on income and productivity relative to the EU average and show the age
profile of its adults' educational attainment.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `estado-novo-legacy`) needs these series
to reproduce its numbers exactly. Eurostat's dissemination API serves only the
current vintage of each dataset, and national accounts are revised every year,
so a query cannot be pinned the way a Git commit can. The registry keeps the
responses byte for byte, with checksums, so the downstream output does not
change when Eurostat revises a table.

## Upstream identity

- Publisher: Eurostat (European Commission)
- Service: dissemination API, JSON-stat 2.0
  (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data`)
- Retrieved: **2026-11-25T00:38:28Z** to **2026-11-25T00:38:33Z**
- Each file keeps Eurostat's own `updated` timestamp for the dataset, and
  `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/nama_10_pc.json` | 53,748 | `15b5e3f72789bbd76fa4c17f890aae40d80cd11c0a2f6acce7265d52a7b1e4ff` |
| `raw/edat_lfse_03.json` | 118,970 | `c8babca938a802f7ae70b9ef5ca4c639bdce2042b48fb8c2cd400e0edcaee2e3` |
| `raw/lfsa_egised.json` | 168,673 | `63077f2c73e4b0511faa8d5e95091665cf525b5e155b66e959d48fe8d3417fbd` |
| `raw/nama_10_lp_ulc.json` | 26,489 | `456047b0f1b71e4e659dc7104696a5feb72a3dde045995ed0a10286bc62fe071` |

What each file holds:

- `nama_10_pc.json`: GDP (B1GQ) and actual individual consumption (P41) per capita in purchasing power standards, as an index with EU27 (2020) = 100 and in current PPS per head, EU27 (2020) and the 27 member states, 1975 onward where published (most series start in 1995 or 2000).
- `edat_lfse_03.json`: Population aged 25-64 and in ten-year bands (25-34, 35-44, 45-54, 55-64) by educational attainment, percentage with at most lower secondary education (ISCED 2011 levels 0-2) and with tertiary education (levels 5-8), both sexes, EU27 (2020) and the 27 member states, Labour Force Survey, 1992 onward.
- `lfsa_egised.json`: Employed persons aged 20-64 by occupation (ISCO-08 total, managers OC1, professionals OC2, technicians and associate professionals OC3) and educational attainment (total, ISCED 0-2, ISCED 5-8), thousands, both sexes, EU27 (2020) and the 27 member states, Labour Force Survey; ISCO-08 breakdowns start in 2011.
- `nama_10_lp_ulc.json`: Nominal labour productivity per person employed (NLPR_PER) and per hour worked (NLPR_HW), PPS, EU27 (2020) = 100, EU27 (2020) and the 27 member states, 1975 onward where published.

## Known limits

- Values for 2025 are first estimates and many carry Eurostat's flag `p`
  (provisional); national accounts for recent years are revised each year.
- GDP per head in PPS is a price-level-adjusted volume index for comparing
  countries in one year, not for growth rates over time. Luxembourg and
  Ireland are distorted by cross-border workers and multinational accounting.
- Labour Force Survey series have breaks (flag `b`) when national surveys
  change; the ISCED 2011 classification applies from 2014, with earlier years
  converted by Eurostat. ISCO-08 occupations start in 2011.
- Small cells in `lfsa_egised` are suppressed or flagged `u` (low
  reliability); several member states publish no managers with at most lower
  secondary education.

## Reading the files

They are JSON-stat 2.0 documents. Observations sit in a flat `value` object
keyed by the row-major position over the dimensions in `id`, with sizes in
`size`. Missing observations are absent. Status flags (for example `p`
provisional, `e` estimated, `b` break in series, `u` low reliability) are in
`status`, keyed the same way.

## Licence and attribution

Eurostat data may be reused free of charge for commercial and non-commercial
purposes, with acknowledgement of the source, under the Commission's reuse
policy (Decision 2011/833/EU), subject to the exceptions in Eurostat's
copyright notice. Use the attribution:

> Source: Eurostat.

The canonical metadata records `redistribution: allowed`.

## Consumers

- `medium-blog`: `DiogoRibeiro7/Medium-Blog`, folder `estado-novo-legacy`.
