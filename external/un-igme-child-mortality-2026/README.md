# UN IGME child mortality estimates: 2026 data release

The [UN Inter-agency Group for Child Mortality Estimation (UN IGME)](https://childmortality.org/all-cause-mortality/data)
publishes comparable country-level child mortality series. The source's
2026 data update is dated **18 March 2026**, and the official portal offers
downloads of estimates and the underlying available source observations.

The associated [UNICEF child mortality dataset](https://data.unicef.org/resources/dataset/child-mortality/)
is available for structured download, including via UNICEF's SDMX data
services. The portal documents:

- **Neonatal mortality:** death in the first 28 days of life.
- **Infant mortality:** death before the first birthday.
- **Under-five mortality:** death before the fifth birthday.
- **Observed source series:** vital registration or survey/census inputs,
  which may be retained or excluded by the modeling procedure.
- **Model estimates:** annual central estimates with uncertainty ranges;
  the portal's plotted bands are **90% uncertainty intervals**.

The research project `portugal-living-standards-reassessment` plans to
compare Portuguese infant and child mortality with predefined European
peer groups. It has **not yet imported a pinned UN IGME source export**.
Before use, store the exact downloaded release, file checksum, date,
indicator/age definition, sex, geographic codes, years and interval limits.

## Important inference limits

The World Bank's infant mortality series `SP.DYN.IMRT.IN` is sourced from
UN IGME, so it is **not an independent validation dataset**. A direct UN
IGME estimate and a WDI observation can disagree due to release timing or
presentation while remaining products of the same modeling family.

Do not splice UN IGME modeled estimates with INE/PORDATA registered rates.
Nor should either infant or under-five mortality be used as a direct
survival-to-age-20 probability for male military inspection cohorts.

## Rights

UNICEF explicitly marks the **downloadable child mortality dataset** as
[CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/), requiring
attribution. The UNICEF website's default content licence is a different,
noncommercial licence; it does not replace the specific dataset licence.
This is an external, metadata-only registry entry. No statistical source
files are mirrored.
