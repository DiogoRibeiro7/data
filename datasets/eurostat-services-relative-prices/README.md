# Eurostat: why services prices move relative to goods, EU 1995-2025

Canonical snapshot of five Eurostat API responses that let a reader take the
price of each industry apart into wages per hour, output per hour and the share
of value added paid to labour, and set it against what households pay for
services and goods and against price levels across member states.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `services-relative-prices`) needs these
series to reproduce its numbers exactly. Eurostat's dissemination API serves
only the current vintage of each dataset, so a query cannot be pinned the way a
Git commit can. The registry keeps the responses byte for byte, with checksums,
so the downstream output does not change when Eurostat revises a series.

## Upstream identity

- Publisher: Eurostat (European Commission)
- Service: dissemination API, JSON-stat 2.0
  (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data`)
- Retrieved: **2026-11-22T21:59:03Z** to **21:59:09Z**
- Each file keeps Eurostat's own `updated` timestamp for the dataset, and
  `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/nama_10_a64.json` | 2,186,817 | `11ee27e6a719fc8a255c7b48ddae42c3301e0632578191e5e7545c0b2602a8c4` |
| `raw/nama_10_a64_e.json` | 622,210 | `c0c90f441e21612bec574d7cf0df0ea6852b313e3e6a0e2530dfe16138139bc9` |
| `raw/prc_hicp_aind.json` | 563,897 | `7b27b52c329f77c998adce5edd687d76cb836b0fc278e196a2e1dc6603f5fc85` |
| `raw/prc_hicp_inw.json` | 54,662 | `1ccdb645e1416f0352be40ee0680ed1d02bacf67157feb252f3825e180f07e46` |
| `raw/prc_ppp_ind.json` | 210,069 | `7d4c9b4fff197bfb7eb295ff66383eedb6b5922f73abafd0a1020da212614e77` |

What each file holds:

- `nama_10_a64.json`: gross value added at current prices and in chain-linked
  volumes (2020), and, at current prices, compensation of employees, operating
  surplus and mixed income (net), other taxes less subsidies on production and
  consumption of fixed capital. Million euro, by NACE Rev.2 section A to T,
  the total, and the divisions J61 (telecommunications), Q86 (health) and
  Q87_Q88 (residential care and social work), for the EU27 and each member
  state.
- `nama_10_a64_e.json`: hours worked by all workers and by employees
  (domestic concept), thousand hours, for the same industries and geographies.
- `prc_hicp_aind.json`: HICP annual average indices, 2015 = 100. All items,
  goods, services, the energy, food and non-energy industrial goods
  aggregates, the five service groups, education-health-social protection,
  administered prices, and 39 COICOP items, from hairdressing and dental care
  to computers and television sets. EU27, euro area (EA20) and each member
  state.
- `prc_hicp_inw.json`: HICP weights of the same codes, per mille of all items,
  for the EU27, the euro area and Portugal.
- `prc_ppp_ind.json`: price level indices (EU27 = 100) and per-capita volume
  indices for GDP, actual individual consumption, goods, services and seven
  consumption categories, for the EU27 and each member state.

The national-accounts queries start in 1995, the price-level query in 1995
(goods and services categories exist from 2003), and the HICP queries take
every year Eurostat publishes. At EU level the aggregates start in 2000 or
2001 and several items only in 2017.

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

- `medium-blog`: `DiogoRibeiro7/Medium-Blog`, folder `services-relative-prices`.
