# Eurostat: inputs of the EU service sector, 1995-2025

Canonical snapshot of seven Eurostat API responses that measure what the service
sector of the EU and its member states uses: hours worked, final energy, and the
time of the people who consume its output.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `services-energy-time`) needs these series
to reproduce its numbers exactly. Eurostat's dissemination API serves only the
current vintage of each dataset, so a query cannot be pinned the way a Git
commit can. The registry keeps the responses byte for byte, with checksums, so
the downstream output does not change when Eurostat revises a series.

## Upstream identity

- Publisher: Eurostat (European Commission)
- Service: dissemination API, JSON-stat 2.0
  (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data`)
- Retrieved: **2026-11-22T20:10:07Z**
- Each file keeps Eurostat's own `updated` timestamp for the dataset, and
  `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/nama_10_a10.json` | 506,067 | `6a100cf6bbe75ca4d0e88203bc12a35088c740bc48491b037cca0b4f2816a652` |
| `raw/nama_10_a10_e.json` | 475,622 | `6dc6ddbdcd9054101f4df1f7fe86044b6786f2feda6beeabc5ea5d0c49bce425` |
| `raw/nrg_bal_c.json` | 187,819 | `fc2249d35669f7f4f65bc4aa7608b53c4096ccf3e2bae9713e98115b7073b2ac` |
| `raw/tus_00age.json` | 30,160 | `fddd5c9b429426f63ad2aea85fdaca53d8e2eb6077b7385bd961f8bb3b723805` |
| `raw/nama_10_pc.json` | 113,495 | `03811a0d57751b88dd24005689e98e29776d949121011dc711369d51cdba25f8` |
| `raw/nama_10_pe.json` | 25,614 | `72f9cb832d04789ea347d057d49b6dd41fd1405e883fc6c50df09f1a1d1429dc` |
| `raw/prc_hicp_aind.json` | 6,285 | `9d8b275f4149b15365f3412f35c086f5762136ef624887a63717aef60914b7eb` |

What each file holds:

- `nama_10_a10.json`: gross value added by NACE Rev.2 A*10 industry,
  chain-linked volumes (2020) and current prices.
- `nama_10_a10_e.json`: hours worked and persons employed by the same
  industries (domestic concept).
- `nrg_bal_c.json`: final energy consumption in total and by industry,
  transport, households and commercial and public services, all products and
  electricity, ktoe.
- `tus_00age.json`: Harmonised European Time Use Surveys, 2000 and 2010
  waves, minutes per day by activity for all persons. Eurostat writes durations
  as `hh:mm` strings.
- `nama_10_pc.json`: per-capita GDP, household and NPISH consumption and actual
  individual consumption, in PPS and chain-linked volumes.
- `nama_10_pe.json`: total population, national concept.
- `prc_hicp_aind.json`: HICP annual indices for services and all items, EU27
  and euro area. The query also asked for goods, which the API does not return.

All queries start in 1995, except the HICP and time-use queries, which take
every year Eurostat publishes. Geographies are not filtered, so EU and euro-area
aggregates come with the member states.

## Reading the files

They are JSON-stat 2.0 documents. Observations sit in a flat `value` object
keyed by the row-major position over the dimensions in `id`, with sizes in
`size`. Missing observations are absent. Status flags (for example `p`
provisional, `e` estimated, `b` break in series) are in `status`, keyed the
same way.

## Licence and attribution

Eurostat data may be reused free of charge for commercial and non-commercial
purposes, with acknowledgement of the source, under the Commission's reuse
policy (Decision 2011/833/EU), subject to the exceptions in Eurostat's
copyright notice. Use the attribution:

> Source: Eurostat.

The canonical metadata records `redistribution: allowed`.

## Consumers

- `medium-blog`: `DiogoRibeiro7/Medium-Blog`, folder `services-energy-time`.
