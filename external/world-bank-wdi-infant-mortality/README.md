# World Bank World Development Indicators: infant mortality

The [World Bank's infant mortality indicator](https://data.worldbank.org/indicator/SP.DYN.IMRT.IN?locations=PT),
`SP.DYN.IMRT.IN`, measures **deaths before age one per 1,000 live births**.
Its underlying statistical source is the **UN Inter-agency Group for Child
Mortality Estimation (UN IGME)**. The current indicator page presents a
historical series from 1960, with its displayed end year depending on the
release; do not assume new years or source revisions are immutable.

For reproducible extraction, the study should record the complete World
Bank API response URL, requested ISO3 country IDs, retrieval timestamp,
provider update, API pagination, exact observation years, units, missing
values and SHA-256 of its stored response. For Portugal, the API endpoint
is:

`https://api.worldbank.org/v2/country/PT/indicator/SP.DYN.IMRT.IN?format=json&per_page=20000`

No WDI response has yet been imported or pinned by the consumer. Do not
present future comparisons as already computed.

## Separation from other measures

- **INE/PORDATA:** registered Portuguese infant deaths and births; specific
  population definitions and official structural breaks apply.
- **WDI:** modeled and internationally harmonized UN IGME estimates. Its
  observations for Portugal can differ from the national registered rates.
- **UN IGME direct:** the same underlying estimation programme with a
  different presentation, release/version and available uncertainty ranges.
  WDI and direct UN IGME values are **not independent replications**.
- **Survival to age 20:** not measured by infant mortality; it requires a
  different life-table/cohort-survival analysis.

For a European comparison, choose comparison countries **before** examining
post-1974 changes. Report both levels and annualized changes, including
pre-periods and uncertainty. National endpoint differences are not by
themselves estimates of regime or SNS causal effects.

## Reuse

The [indicator page](https://data.worldbank.org/indicator/SP.DYN.IMRT.IN)
marks this series **CC BY 4.0**. [World Bank data terms](https://data.worldbank.org/summary-terms-of-use)
require attribution to both the World Bank and original providers, prohibit
implied endorsement, and retain any dataset-specific third-party conditions.
The licence assertion is specific to this indicator, not a blanket grant
for every dataset served by the World Bank. The registry contains only a
source record and no downloadable data copy.
