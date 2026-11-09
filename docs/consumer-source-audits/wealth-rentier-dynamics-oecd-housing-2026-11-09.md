# Supplemental consumer audit: OECD analytical house prices

Reviewed: **2026-11-09**. Downstream implementation examined at
[`f3e6e3a5`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py).
This is a source-contract and consumer-code audit, not a verified retrieval of
the six national OECD responses. No OECD observations or raw files are
committed or redistributed here.

## Exact downstream request scope

The downloader constructs six SDMX-CSV requests using the same annual flow:

```text
https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/{REF_AREA}.A..?startPeriod=1990&format=csvfile
```

| Consumer geography | OECD `REF_AREA` |
| --- | --- |
| PT | `PRT` |
| ES | `ESP` |
| FR | `FRA` |
| IT | `ITA` |
| IE | `IRL` |
| NL | `NLD` |

The dataflow/version matches the [OECD Analytical House Price Indicators
Data Explorer](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.ECO.MPD&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_AN_HOUSE_PRICES%40DF_HOUSE_PRICES&df%5Bvs%5D=1.0&fc=Topic&pg=0&snb=106&tm=housing).
But `.A..` selects the annual frequency while leaving further dimensions
open. It is a *query template*, not an immutable data release or a verified
five-measure export.

## Interpretation controls

| Code | Consumer field | OECD statistical meaning | Invalid inference to avoid |
| --- | --- | --- | --- |
| `HPI` | `house_price_index` | Nominal house-price index | Nominal price per dwelling |
| `RHP` | `real_house_price_index` | Deflated house-price index | Same as unadjusted HPI |
| `RPI` | `rent_price_index` | Housing-rent price index | Euro rent per month |
| `HPI_YDH` | `price_to_income_ratio` | Price-to-disposable-income **index** (2015 = 100) | Housing cost as a share of income |
| `HPI_RPI` | `price_to_rent_ratio` | Price-to-rent **index** (2015 = 100) | Gross rental yield or rent/price level |

The [OECD indicator definition](https://www.oecd.org/en/data/indicators/housing-prices.html)
describes the ratio indices and their 2015 reference year. The
[OECD housing-price FAQ](https://www.oecd.org/en/data/insights/data-explainers/2024/07/Residential-Property-Price-Indices-and-related-housing-indicators-Frequently-Asked-Questions.html)
states that analytical RPPI series are seasonally adjusted. The Data Explorer
states that its annual observations are annual averages, not Q4 observations.
Its metadata also documents different national source practices, so
comparability is not automatic. This audit does **not** establish the owner or
reuse rights of each of the six countries' underlying observations.

## Consumer extraction risks

The pinned consumer's `normalize_oecd_house_price_data()`:

1. Finds country, year, value and measure columns, but does not constrain an
   expected response unit, adjustment flag or all remaining series dimensions.
2. Calls `pivot_table(..., aggfunc="first")` by year and measure. **If** the
   response includes multiple values for one year/measure under different
   dimensions, the choice depends on input order rather than a declared
   statistical contract.
3. Accepts a result containing `country` and `year` even when none of the five
   promised measures are available, which can mask schema drift.
4. Records neither a full URL/response SHA-256 nor a dated OECD release
   identity, so repeating the extraction cannot reproduce a specific vintage.

These are code-level risks, not a finding that the currently served OECD CSV
contains duplicate observations or that a download was tested here.

## Required checks for a consumer acquisition PR

1. Query each of the six exact OECD areas with annual frequency and a declared
   five-measure and unit/adjustment selection; check every returned
   `REF_AREA`, `FREQ`, `MEASURE`, unit and time period before normalization.
2. Fail on duplicate `(country, year, measure)` observations after the intended
   dimensions are selected. Never silently take the first of conflicting
   rows; require every scientifically necessary measure or expose missing
   coverage explicitly.
3. Retain the original index units and 2015 reference-year definition;
   distinguish a normalized price-to-income index from observed household
   housing-cost burdens or capital-income shares.
4. Retain the exact request URL, download timestamp, source-update metadata,
   raw byte length and SHA-256, and normalization revision for each country.
   A dataflow version (`1.0`) is not a frozen observation vintage.
5. Check the Data Explorer *source* information for each country and measure
   before redistributing or promoting any output. The
   [OECD data terms](https://www.oecd.org/en/about/terms-conditions.html)
   require checking third-party rights and additional conditions.
6. Test the consumer with offline SDMX-CSV fixtures for duplicate rows,
   unexpected units, empty/partial measure sets, annual period parsing and
   country-code conversion before attempting live acquisition.

## Registry disposition

The source remains **metadata-only, redistribution unresolved, actionable**.
No per-country ownership check, authoritative CSV response checksum, or
empirical panel has been established by this PR. The next code change belongs
in `wealth_rentier_dynamics`; this record preserves the requirements and
official evidence without claiming that the scientific analysis is complete.
