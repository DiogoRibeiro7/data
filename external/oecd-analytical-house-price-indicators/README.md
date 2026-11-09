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

### Interpretation and extraction safeguards

The [OECD indicator definition](https://www.oecd.org/en/data/indicators/housing-prices.html)
and [OECD Data Explorer](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.ECO.MPD&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_AN_HOUSE_PRICES%40DF_HOUSE_PRICES&df%5Bvs%5D=1.0&fc=Topic&pg=0&snb=106&tm=housing)
establish the following distinctions:

| Measure | Meaning | Interpretation boundary |
| --- | --- | --- |
| `HPI` | Nominal house-price index | Index of prices, not a dwelling-price level |
| `RHP` | Real house-price index | Deflated nominal prices, not the unadjusted nominal series |
| `RPI` | Housing rent-price index | Index, not monthly rent in euros |
| `HPI_YDH` | House-price / disposable-income index | Normalized ratio index (2015 = 100), not the percentage of income used for housing |
| `HPI_RPI` | House-price / rent index | Normalized ratio index (2015 = 100), not a rental yield |

According to the [OECD housing-price FAQ](https://www.oecd.org/en/data/insights/data-explainers/2024/07/Residential-Property-Price-Indices-and-related-housing-indicators-Frequently-Asked-Questions.html),
the analytical price indices are seasonally adjusted. The Data Explorer
describes annual observations as averages of the year, not end-of-year values.
Levels of normalized indices should not be compared across countries as if
they were common-currency dwelling prices or comparable affordability ratios.

The consumer's query leaves the `MEASURE` and final unit/dimension positions
unrestricted (`{REF_AREA}.A..`). Its normalizer pivots each year and measure
using the first matching value, without checking uniqueness across remaining
dimensions; it also accepts a result with only country and year columns.
This is a **potential ambiguity**, not evidence that an actual response
contains duplicates. The [2026-11-09 audit](../../docs/consumer-source-audits/wealth-rentier-dynamics-oecd-housing-2026-11-09.md)
defines acceptance checks before an empirical extraction can be trusted.

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
plus an exact-dimensionality/uniqueness check in the consumer, followed by a
pinned export. No observations are stored in this registry.
