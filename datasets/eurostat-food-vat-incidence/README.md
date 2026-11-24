# Eurostat: household budgets by income fifth, for the incidence of VAT on food

Canonical snapshot of seven Eurostat API responses that let a reader compute,
for every member state, who gains from a change in VAT on food: how many
euros each income fifth saves and how large the saving is relative to its
budget and its income.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `food-vat-shares`) needs these series to
reproduce its numbers exactly. Eurostat's dissemination API serves only the
current vintage of each dataset, so a query cannot be pinned the way a Git
commit can. The registry keeps the responses byte for byte, with checksums, so
the downstream output does not change when Eurostat revises a table.

## Upstream identity

- Publisher: Eurostat (European Commission)
- Service: dissemination API, JSON-stat 2.0
  (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data`)
- Retrieved: **2026-11-24T21:28:57Z** to **2026-11-24T21:32:02Z**
- Each file keeps Eurostat's own `updated` timestamp for the dataset, and
  `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/hbs_str_t223.json` | 77,411 | `1d11c464d4f090bc478d7f8cd20b83c56eb08eea5870bafd53f238f3e3f76356` |
| `raw/hbs_exp_t133.json` | 15,619 | `8031373a8d39f9f0b246c60c5a30a5a5335e674b34e765919a97eaf253089ff3` |
| `raw/hbs_exp_t111.json` | 7,968 | `80a31967b2afc68af57042db406cb12ac69105314d34cea81502c5e45b5e6471` |
| `raw/icw_aff_01.json` | 79,262 | `fd4738da89fea4b0f9def505b2a8470f79b398e1f691a4643c75da9f99d1a509` |
| `raw/icw_sr_10.json` | 10,437 | `7028a2058c36c75d5a67e4171c1dc994b1dfed6fcf04f42176318b0386e29ac3` |
| `raw/ilc_di01.json` | 22,968 | `a3d8dfd5426d70bfa774fac86e154fe98d33885097243c6182011a2c86a4b3f8` |
| `raw/prc_hicp_aind.json` | 22,249 | `a89b83729aec0ab4ea4b837191019c0a47df52f58fc7f6dc829bc7701e1aeb7d` |

What each file holds:

- `hbs_str_t223.json`: Structure of consumption expenditure by income fifth (QU1 to QU5) and COICOP purpose, per mille of total consumption expenditure: the twelve divisions CP01 to CP12 and the groups CP011 (food), CP012 (non-alcoholic beverages), CP041 (actual rentals), CP042 (imputed rentals), CP111 (catering services) and CP112 (accommodation), EU27 (2020) and the 27 member states, budget-survey waves 2010, 2015 and 2020. Italy has no data by income fifth; for 2020, Cyprus, France and Malta are their 2015 surveys repriced by Eurostat, and Portugal publishes divisions only.
- `hbs_exp_t133.json`: Mean consumption expenditure by income fifth and total, in PPS per adult equivalent and per household, same geographies and waves.
- `hbs_exp_t111.json`: Mean consumption expenditure per household and per adult equivalent in euros, national currency and PPS (totals, no income breakdown), same geographies and waves; used for the euros-per-PPS factor of each survey.
- `icw_aff_01.json`: Experimental income-consumption-wealth statistics: disposable income of households spent on all consumption (CP00), consumption without imputed rent (CP00_X_042), food and non-alcoholic beverages (CP01) and food (CP011), as a percentage of disposable income, by income fifth and decile, 2015 and 2020.
- `icw_sr_10.json`: Experimental statistics: aggregate propensity to consume (consumption as a percentage of disposable income) by income fifth, 2015 and 2020.
- `ilc_di01.json`: EU-SILC distribution of equivalised disposable income: top cut-off points of deciles 1 to 9 and quintiles 1 to 4, euros, survey years 2022 onward (incomes of the previous year).
- `prc_hicp_aind.json`: HICP annual average indices (2015 = 100): all items (CP00), food and non-alcoholic beverages (CP01) and restaurants, cafés and the like (CP111), 2010 onward.

## Known limits

- The household budget survey (HBS) is run every five years on a voluntary
  basis; survey years differ by country and are repriced to the reference
  year. The 2015 wave was collected between 2012 and 2017.
- Italy publishes no HBS table by income fifth. Czechia and Malta impute no
  rent to owner-occupiers. In the 2020 wave, Cyprus, France and Malta are
  their 2015 surveys repriced, Czechia and Sweden are missing, and Portugal
  (survey of 2022/23) publishes COICOP divisions only.
- `icw_*` tables are experimental statistics built by statistically matching
  EU-SILC and HBS records on shared variables; they assume that income and
  consumption are linked only through those variables. All observations carry
  Eurostat's flag `i`.
- `ilc_di01` cut-offs refer to equivalised disposable income of the year
  before the survey year.

## Reading the files

They are JSON-stat 2.0 documents. Observations sit in a flat `value` object
keyed by the row-major position over the dimensions in `id`, with sizes in
`size`. Missing observations are absent. Status flags (for example `p`
provisional, `e` estimated, `b` break in series, `i` see metadata) are in
`status`, keyed the same way.

## Licence and attribution

Eurostat data may be reused free of charge for commercial and non-commercial
purposes, with acknowledgement of the source, under the Commission's reuse
policy (Decision 2011/833/EU), subject to the exceptions in Eurostat's
copyright notice. Use the attribution:

> Source: Eurostat.

The canonical metadata records `redistribution: allowed`.

## Consumers

- `medium-blog`: `DiogoRibeiro7/Medium-Blog`, folder `food-vat-shares`.
