# Eurostat: EU material use, footprint, circularity and waste, 2000-2025

Canonical snapshot of ten Eurostat API responses on how much material the EU
and its member states take in, how much of it is used up, built into stocks or
recycled, and how that compares with GDP and construction output.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `eu-material-use`) needs these series to
reproduce its numbers exactly. Eurostat's dissemination API serves only the
current vintage of each dataset, so a query cannot be pinned the way a Git
commit can. The registry keeps the responses byte for byte, with checksums, so
the downstream output does not change when Eurostat revises a series.

## Upstream identity

- Publisher: Eurostat (European Commission)
- Service: dissemination API, JSON-stat 2.0
  (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data`)
- Retrieved: **2026-11-22T23:14:04Z** to **23:14:16Z**
- Each file keeps Eurostat's own `updated` timestamp for the dataset, and
  `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/env_ac_mfa.json` | 639,762 | `bf8404fac88be14279c658d508316476b3ff2050a4a267e953f770e761f431db` |
| `raw/env_ac_rme.json` | 236,273 | `77197e35a2deadcfab40645bc74b6a1b1303cd0d8a5dc78ca3c8046b7776052d` |
| `raw/env_ac_rmefd.json` | 18,102 | `8371fe7440b236cea684087d06761c2627e452ededf38c747f541d25da94813b` |
| `raw/env_ac_cur.json` | 8,158 | `1a59492dd813862dfe279fe850074e71a226828e8acb13066e76bae988e8a579` |
| `raw/env_ac_curm.json` | 4,084 | `985b1fb43365ee4c430493d7ce4d49d124eed615a61df78871a122a1a7f8369f` |
| `raw/env_ac_sd.json` | 21,517 | `d3b041c9a803323c4928320ed79d4a26a5a76ef43c3a13e01e11cce2f66f4f5c` |
| `raw/env_wastrt.json` | 22,341 | `fc316d295993afe4fd199140cefd5f3d04da15e3aac5e00b5c907ae36c1bbb35` |
| `raw/nama_10_gdp.json` | 26,626 | `8adaef8903d9b0838d2e615e75142e1007ec43eab615dd9aa3e57f95c5fd3956` |
| `raw/nama_10_a10.json` | 25,877 | `583636ab65823ab8873a58ad10aaa4096431ee8bda16c2bfcdba5e2932045c57` |
| `raw/nama_10_pe.json` | 14,821 | `6c722147372159582cc925a295c4b8c1ac508cd7f5ff11eb5b27824244626490` |

What each file holds:

- `env_ac_mfa.json`: economy-wide material flow accounts. Domestic material
  consumption (DMC), domestic extraction, imports and exports, in total and
  for biomass, metal ores, non-metallic minerals, fossil energy materials and
  other products, in thousand tonnes and tonnes per person, EU27 and each
  member state, from 2000.
- `env_ac_rme.json`: material footprint in raw material equivalents. Raw
  material consumption (RMC) and its parts, in total and for the four main
  material groups, EU27 and each member state.
- `env_ac_rmefd.json`: the EU27 material footprint by final use: final
  consumption of households and government, and gross capital formation, for
  all products and for construction.
- `env_ac_cur.json` and `env_ac_curm.json`: the circular material use rate,
  by country, and for the EU27 by material group.
- `env_ac_sd.json`: the EU27 flows behind Eurostat's Sankey diagram of
  material flows: processed material, material use, material accumulation,
  emissions, dissipative flows and trade in waste for recycling.
- `env_wastrt.json`: waste treatment by waste category and treatment type
  (recycling, backfilling, energy recovery, incineration, landfill, other
  disposal), EU27 and Portugal, every second year from 2004.
- `nama_10_gdp.json`, `nama_10_a10.json` and `nama_10_pe.json`: GDP,
  construction value added (both in chain-linked volumes) and population for
  the same countries, from 2000.

Some recent footprint values and the 2025 material-flow values carry Eurostat
flags; the flags are kept in each file's `status` object.

## Reading the files

They are JSON-stat 2.0 documents. Observations sit in a flat `value` object
keyed by the row-major position over the dimensions in `id`, with sizes in
`size`. Missing observations are absent. Status flags are in `status`, keyed
the same way.

## Licence and attribution

Eurostat data may be reused free of charge for commercial and non-commercial
purposes, with acknowledgement of the source, under the Commission's reuse
policy (Decision 2011/833/EU), subject to the exceptions in Eurostat's
copyright notice. Use the attribution:

> Source: Eurostat.

The canonical metadata records `redistribution: allowed`.

## Consumers

- `medium-blog`: `DiogoRibeiro7/Medium-Blog`, folder `eu-material-use`.
