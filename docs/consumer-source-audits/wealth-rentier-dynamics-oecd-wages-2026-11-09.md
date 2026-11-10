# Supplemental consumer audit: OECD average annual wages

Reviewed: **2026-11-09**. Current downstream code inspected at
[`bf0e75b9`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/data_sources.py).
This is a review of the official statistical contract and consumer code,
not an executed extraction or independently verified OECD CSV download.

## What the consumer requests

The consumer's query template for each of six countries is:

```text
https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE,1.0/{REF_AREA}.WG.USD_PPP..Q..?startPeriod=1990&format=csvfile
```

| Research code | OECD `REF_AREA` |
| --- | --- |
| PT | `PRT` |
| ES | `ESP` |
| FR | `FRA` |
| IT | `ITA` |
| IE | `IRL` |
| NL | `NLD` |

The [OECD Data Explorer](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.ELS.SAE&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_EARNINGS%40AV_AN_WAGE&df%5Bvs%5D=1.0&dq=..USD_PPP....&pd=2023%2C&pg=0&snb=26&tm=average+annual+wage&to%5BTIME_PERIOD%5D=false&vw=tb)
confirms the `USD_PPP`/constant-price selection. `WG` selects the average
wage indicator and `Q` denotes a constant-price base in the consumer query.
The blank positions in the key must be reconciled against all dimensions
in the actual returned response, not assumed to be a unique series.

## Statistical meaning

The [OECD indicator](https://www.oecd.org/en/data/indicators/average-annual-wages.html)
measures the mean yearly wage per full-time-equivalent *dependent employee*.
It uses a national-accounts wage bill and an adjustment for working hours.
For the currently displayed release, levels are constant-price 2025 US
dollars converted with purchasing-power parities for private consumption.

The following are different estimands:

| Selected observation | Not equivalent to |
| --- | --- |
| Full-time-equivalent mean annual wage | Median wage or wage of a typical individual |
| Constant-price USD-PPP wage level | Nominal annual salary in euros |
| Wage growth from adjacent annual real-wage observations | Disposable household income growth or income inequality |
| Wage measure for dependent employment | All households' wealth or capital income |

The PPP price base and prior-year values can be revised. An OECD SDMX
dataflow version (`1.0`) does not pin the observation vintage.

## Parser risks verified from the consumer code

1. `normalize_oecd_average_wages()` checks for country, time and value
   columns but does not validate their dimensional values. It then discards
   the country column and any remaining unit/measure/price-base fields.
2. `.drop_duplicates(subset=[year])` keeps the first candidate per year.
   **If** one query returns two distinct observations for a year, it silently
   chooses a row instead of checking which statistical series is intended.
3. `.pct_change()` reports growth between adjacent *rows*, not necessarily
   adjacent years. For example, a 2019-to-2021 change over missing 2020 is a
   two-year change and must not be treated as 2021 year-on-year growth.
4. The normalized table does not retain source response identity, the PPP
   reference year, upstream status flags or a recorded checksum. It cannot
   substantiate a reproducible empirical panel by itself.

These are structural risks; this audit does not claim that the live OECD
response has duplicate rows or missing periods. No network retrieval or
per-country coverage check was completed here.

## Acceptance criteria for a downstream acquisition PR

1. Validate every returned country's `REF_AREA`, `WG` indicator,
   `USD_PPP` unit, constant-price `Q`, time frequency and all remaining SDMX
   dimensions. Filter to a scientifically explicit series before reshaping.
2. Enforce one unambiguous observation per `(country, year)` for the chosen
   measure and unit; reject conflicting duplicates rather than taking the
   first value. Flag missing countries and years explicitly.
3. Produce `wage_growth` only where year `t-1` exists and both observations
   are valid. For a year gap, return missing growth and a gap marker; never
   mistake an interval-average change for one-year growth.
4. Test offline CSV fixtures containing: two units in one year, conflicting
   duplicate values, missing preceding year, missing `OBS_VALUE`, unexpected
   country code, incorrect price base and normal consecutive annual values.
5. Preserve full query URL, raw byte length and SHA-256, UTC acquisition
   timestamp, observed PPP/price reference year, source-update information
   and normalization revision for all six country responses.
6. Inspect country-series *source* ownership in the Data Explorer. The
   [OECD Data Terms & Conditions](https://www.oecd.org/en/about/terms-conditions.html)
   expressly require checking third-party rights and any added restrictions
   before publication or redistribution.

## Registry decision

Keep the OECD wages source **metadata-only with unresolved redistribution
rights**, pending source-ownership evidence and a dated, hashed consumer
export. The actual parser change and acquisition belong in
`wealth_rentier_dynamics`; this audit defines the evidence gates without
representing synthetic or unverified observations as real data.
