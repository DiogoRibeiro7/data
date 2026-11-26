# CWON 2024 wealth resilience candidate

Reviewed 2026-11-26. This is an acquisition contract, not an observed data report or a canonical registration.

## Source

- [The Changing Wealth of Nations 2024](https://www.worldbank.org/en/publication/the-changing-wealth-of-nations).
- [Wealth Accounting dataset](https://datacatalog.worldbank.org/search/dataset/0042066/wealth-accounting), annual 1995–2020.
- [World Bank API source directory](https://api.worldbank.org/v2/sources?format=json&per_page=100): Wealth Accounts source 59, lastupdated 2024-10-08, verified 2026-11-26.
- [DataBank Wealth Accounts](https://databank.worldbank.org/source/wealth-accounts).

The 33-country sample matches the WDI acquisition. Request the seven indicator IDs below for 1995–2020 (up to 858 cells per series). Preserve the original API metadata and observation pages. The individual observation endpoint could not be verified in the research session; the workflow therefore fails closed if its source, vintage, or indicator semantics differ from the contract.

| Indicator | Expected interpretation |
| --- | --- |
| NW.TOW.PC | National comprehensive wealth per capita index |
| NW.PCA.PC | Produced capital per capita |
| NW.HCA.PC | Human capital per capita |
| NW.NCA.TOTL.PC | Renewable natural capital per capita |
| NW.NCA.SSOI.PC | Nonrenewable natural capital per capita |
| NW.NFA.PC | Foreign assets per capita |
| NW.NFL.PC | Foreign liabilities per capita |

All must identify real chained 2019 US dollars, not current dollars or the earlier 2018-dollar methodology. Inspect full definitions as well as names before canonical promotion; in particular, foreign assets and liabilities are distinct and must not be relabelled as net foreign assets based only on an indicator code or legacy source note. The 2024 methodology uses a chained Törnqvist volume index; component series do not add to total wealth, and country-level chained series are not to be summed to create an EU-wide chain index.

## Run

After merging, manually run **Acquire CWON 2024 wealth resilience candidate** in Actions.

Locally, from the root of the data repository:

```bash
python -m unittest discover -s tests -p test_acquire_cwon_gdp_resilience.py -v
python -m scripts.acquire_cwon_gdp_resilience --output cwon-candidate
```

The workflow uploads only on success. Download the artifact named cwon-2024-gdp-resilience-candidate. It includes original metadata, paginated observations, source metadata before and after acquisition, request URLs, retrieval timestamps, checksums, and coverage by country. Nulls and absent observations remain distinct. Identical before/after metadata should not be duplicated in canonical storage; retain provenance for both retrievals.

## Review and downstream interpretation

The World Bank Sovereign ESG portal identifies comprehensive wealth, produced capital, and natural capital indicators as CC BY 4.0:
- [Total wealth](https://esgdata.worldbank.org/data/indicators?ind=NW.TOW.PC&lang=en).
- [Produced capital](https://esgdata.worldbank.org/data/indicators?ind=NW.PCA.PC&lang=en).
- [Renewable capital](https://esgdata.worldbank.org/data/indicators?ind=NW.NCA.TOTL.PC&lang=en).
- [Nonrenewable capital](https://esgdata.worldbank.org/data/indicators?ind=NW.NCA.SSOI.PC&lang=en).

Check the complete downloaded metadata, each indicator's applicable license, and [World Bank dataset terms](https://data.worldbank.org/summary-terms-of-use) before promotion. The reproduction package contains restricted underlying inputs; this acquisition does not request those inputs.

Compare country-level changes in real GDP per capita (WDI real GDP divided by population) with changes in real wealth per capita on identical endpoint years. Start with 1995–2020 and use common observed years only; show excluded countries and 2019 endpoint sensitivity. Do not compare levels in different base-year dollars or infer causality from divergence. A wealth stock is a model-based estimate of future production capacity, not a measure of household net worth or a complete measure of resilience.

The latest wealth year is 2020, so this source cannot support conclusions about wealth changes after 2020. Use WDI independently for later GDP observations. WDI canonical registration must be confirmed before pinning the downstream dataset.

No dataset bytes are committed, no catalog entries are changed, and no active consumer relationship is claimed by this PR.
