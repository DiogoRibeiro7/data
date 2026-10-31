# Eurostat Portugal population by citizenship: `migr_pop1ctz`

Eurostat's [population by citizenship](https://doi.org/10.2908/migr_pop1ctz)
dataset supplies **1 January** population estimates, with citizenship,
age, sex and geography dimensions.

The research project `empirical-analysis-r` pins the [Portugal API
response](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_pop1ctz?geo=PT&age=TOTAL&sex=T&unit=NR&sinceTimePeriod=2017)
at `studies/portugal-migration/data/raw/eurostat_migr_pop1ctz_pt_2017_2025_2026-09-25.json`.

- Filter: `geo=PT`, `age=TOTAL`, `sex=T`, `unit=NR`, annual periods 2017–2025.
- Retrieved for the project: **25 October 2026**.
- Eurostat response `updated`: `2026-09-25T23:00:00+0200`.
- Downstream SHA-256 including its committed trailing newline:
  `27a81f6e211af0b941f507c96ab2f7af8bd5c27b428be114760b9cb1cda2c88b`.

Eurostat's JSON-stat dimensions contain total, national and foreign/stateless
aggregates alongside individual citizenship categories. **Do not sum the
aggregates with their component countries**. An omitted value or explicitly
unavailable source status means **missing**, not zero; the stored 2025
Portugal response has a population total but lacks nationality-specific
data in this vintage.

AIMA/SEF figures are **31 December administrative residence stocks**.
Eurostat uses **1 January statistical population by citizenship**, so even
one-day-aligned figures are not necessarily the same population definition.

Eurostat [authorizes reuse of its statistical API data](https://ec.europa.eu/eurostat/help/copyright-notice)
with source acknowledgment and disclosure of modifications, subject to
its third-party exceptions. This source record is **metadata only**; the
research response is already pinned downstream and is not mirrored here.
