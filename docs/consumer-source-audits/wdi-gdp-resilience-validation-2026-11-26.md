# WDI GDP resilience snapshot: validation and licensing review

Reviewed the uploaded wdi-gdp-resilience-candidate.zip on 2026-11-26.

- Archive SHA-256: `67e93b7dd51b71588cd4f01b10b4c2b98309eef25ece82d3df52b26927f16747`.
- Manifest SHA-256: `45807a39fe812ba771fb88812509cdd55c23b2f0cc020de799bde86cb2e1838f`.
- 24/24 original files matched their recorded byte sizes and SHA-256 values (1,843,115 bytes).
- Each indicator has 1,023 unique country-year records with valid indicator IDs, country codes and dates; no absent cells. Eight indicators, 33 countries, 31 years.
- Source updated 2026-11-11; retrieved 2026-11-26T17:58:51.604028Z to 17:58:59.867295Z.

| Indicator | Non-null | Explicit null | Latest balanced year |
|---|---:|---:|---|
| NY.GDP.MKTP.CD | 1023 | 0 | 2025 |
| NY.GDP.MKTP.KD | 1023 | 0 | 2025 |
| NY.GDP.MKTP.PP.CD | 1023 | 0 | 2025 |
| SP.POP.TOTL | 1023 | 0 | 2025 |
| NV.AGR.TOTL.ZS | 1016 | 7 | 2021 |
| NV.IND.TOTL.ZS | 1016 | 7 | 2021 |
| NV.SRV.TOTL.ZS | 1016 | 7 | 2021 |
| NV.IND.MANF.ZS | 976 | 47 | None |
| Total | 8116 | 68 | — |

All three broad sectors: missing USA 1995–1996 and 2022–2025; JPN 2025. Manufacturing also lacks Bulgaria for all years and China 1995–2003. No imputation. Use separate denominator/coverage for manufacturing; use 2021 or earlier for all-country broad-sector comparison and 2025 for GDP. Additional BEA data can be considered for US sectors but must be harmonized rather than silently spliced.

## License review

World Bank indicator landing pages explicitly label each series CC BY 4.0. Checked 2026-11-26:

- [NY.GDP.MKTP.CD](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD)
- [NY.GDP.MKTP.KD](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD)
- [NY.GDP.MKTP.PP.CD](https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD)
- [SP.POP.TOTL](https://data.worldbank.org/indicator/SP.POP.TOTL)
- [NV.AGR.TOTL.ZS](https://data.worldbank.org/indicator/NV.AGR.TOTL.ZS)
- [NV.IND.TOTL.ZS](https://data.worldbank.org/indicator/NV.IND.TOTL.ZS)
- [NV.SRV.TOTL.ZS](https://data.worldbank.org/indicator/NV.SRV.TOTL.ZS)
- [NV.IND.MANF.ZS](https://data.worldbank.org/indicator/NV.IND.MANF.ZS)

The downloaded source notes identify multiple original statistical providers. No explicit additional restriction was found in those indicator metadata or the checked landing pages. Preserve attribution, including the providers in the metadata, and link the [dataset terms](https://www.worldbank.org/ext/en/legal/terms-conditions/datasets) and [summary terms](https://data.worldbank.org/summary-terms-of-use). The general third-party exceptions remain applicable; this review is not a warranty of independent underlying data rights.

## Promotion

The staging script verifies the exact reviewed manifest and every raw byte before creating the canonical directory. The registration workflow searches successful acquisition runs on main for that exact artifact; it refuses changed or missing data and never downloads a fresh WDI vintage as a substitute. Registry reports are regenerated and validation must pass before the workflow pushes to the registration branch only. The consumer adoption exemption must be removed when the analysis implementation is registered.
