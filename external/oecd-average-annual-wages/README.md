# OECD real average annual wages — country-year covariate

The [OECD average annual wages indicator](https://www.oecd.org/en/data/indicators/average-annual-wages.html)
estimates wages per **full-time-equivalent dependent employee** using the
national-accounts wage bill and employment. The selected series is in constant
prices, converted to US dollars using purchasing-power parities. It is an
**average** and does not measure median wages, household disposable income or
the earnings distribution.

## Verified downstream contract

The [`wealth_rentier_dynamics` downloader](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py)
uses the OECD SDMX dataflow `OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE,1.0`.
For each country, its query is:

```text
https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE,1.0/{REF_AREA}.WG.USD_PPP..Q..?startPeriod=1990&format=csvfile
```

| Consumer code | OECD `REF_AREA` |
| --- | --- |
| PT | PRT |
| ES | ESP |
| FR | FRA |
| IT | ITA |
| IE | IRL |
| NL | NLD |

The key requests the `WG` wage indicator, `USD_PPP` unit and real/constant
price base `Q`. The consumer saves raw responses as
`oecd_wages_{country}.csv`, then selects observation year and value to derive
`average_annual_wage` and `wage_growth` (year-on-year percentage change).
Its normalized output is a country-year covariate. It is **not** an independent
measure of the distribution of wealth or of capital income.

## Source revisions and permissions

The OECD currently [describes the indicator](https://www.oecd.org/en/data/indicators/average-annual-wages.html)
in constant 2025 US dollars at consumption PPPs, but the upstream PPP base
year may change after later releases. Even though the query fixes dataflow
version `1.0`, the values are **not frozen**. A reproducible consumer snapshot
must record the full URL, retrieval timestamp, exact price/PPP base year,
country coverage, raw bytes SHA-256 and transformation revision.

The OECD's [Data Terms & Conditions](https://www.oecd.org/en/about/terms-conditions.html)
allow extraction, use and redistribution of OECD-owned data with source
attribution, while requiring users to inspect the dataset's source metadata
for third-party ownership or specific restrictions. That series-level check
has not been completed for the six country slices, so central redistribution
is recorded as **unresolved**. No SDMX data bytes have been acquired or
committed in this registry.

This is a distinct statistical product from the
[OECD analytical house-price indices](https://github.com/DiogoRibeiro7/data/tree/main/external/oecd-analytical-house-price-indicators).
