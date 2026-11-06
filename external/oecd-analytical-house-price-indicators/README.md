# OECD analytical house prices — country-year source

The OECD publishes [analytical house-price indicators](https://www.oecd.org/en/data/indicators/housing-prices.html)
combining nominal and real house-price indices, rent-price indices and ratios
comparing house prices with rents and disposable income. Its
[official explanatory note](https://www.oecd.org/en/data/insights/data-explainers/2024/07/Residential-Property-Price-Indices-and-related-housing-indicators-Frequently-Asked-Questions.html)
explains the national scope, measures and cross-country comparability limits.

## Verified downstream use

The [`wealth_rentier_dynamics` downloader](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py)
requests annual OECD SDMX-CSV for the following country codes:

| Project code | OECD `REF_AREA` |
| --- | --- |
| PT | PRT |
| ES | ESP |
| FR | FRA |
| IT | ITA |
| IE | IRL |
| NL | NLD |

Its reproducible *query template*, not a frozen response, is:

```text
https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/{REF_AREA}.A..?startPeriod=1990&format=csvfile
```

The consumer maps measure codes `HPI`, `RHP`, `RPI`, `HPI_YDH` and `HPI_RPI`
to nominal house-price index, real house-price index, rent-price index,
price-to-income ratio and price-to-rent ratio respectively. It caches source
responses locally and normalizes them into country-year tables. The downloader
converts the project's two-letter codes to the three-letter OECD codes.

No specific downloaded SDMX response version or checksum has been pinned in
this registry. Revisions to source data, response coverage or methodology
could change later results. Any reproducible empirical release needs the
full request, access date, response SHA-256 and transformation version.

## Reuse decision

The OECD's [Data Terms & Conditions](https://www.oecd.org/en/about/terms-conditions.html)
generally permit copying, adapting and redistributing OECD data for commercial
and non-commercial purposes with attribution. The same terms explicitly
require users to check whether an individual dataset includes third-party
content or additional source-specific conditions. The OECD's housing note
describes several national indicators derived from national statistical
providers or Eurostat.

This consumer's exact set of source tabs and ownership declarations has not
yet been audited. **Redistribution therefore remains unresolved for central
mirroring**, even though the OECD general reuse policy is permissive. The
next actionable step is a per-country, per-measure metadata and licence check,
followed by a pinned export. No observations are stored in this registry.
