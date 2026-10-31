# BIS Portugal residential property price indices

The [Bank for International Settlements (BIS)](https://data.bis.org/topics/RPP/BIS%2CWS_SPP%2C1.0/Q.PT.N.628)
publishes the selected residential property price series for Portugal
in the `BIS,WS_SPP,1.0` data structure.

| Series | Description | Original SDMX CSV | Project-local SHA-256 |
| --- | --- | --- | --- |
| `Q.PT.N.628` | Nominal index, 2010 = 100 | [BIS export](https://stats.bis.org/api/v1/data/WS_SPP/Q.PT.N.628?format=csvfile) | `9483ceb875bd933c8535d8ccac45a79ab5c6aa34fa4fb67a41ef823d88f65fc5` |
| `Q.PT.R.628` | CPI-deflated real index, 2010 = 100 | [BIS export](https://stats.bis.org/api/v1/data/WS_SPP/Q.PT.R.628?format=csvfile) | `91a19672b4184107b05ed8ff28dc0f5633b4fe75e2f09a4432b47a436233f7f7` |

The downstream `empirical-analysis-r` housing study retrieved these original
CSV files on **26 October 2026**, with upstream update date
24 September 2026. Its pinned responses cover **1988-Q1–2026-Q1**;
the live provider may have since added new quarters. No missing periods
are interpolated.

## Measurement break

BIS [country documentation](https://www.bis.org/statistics/pp_selected_documentation.pdf)
identifies two different Portugal input series:

- **1988-Q1–2007-Q4:** advertised property prices from Confidencial
  Imobiliário.
- **From 2008-Q1:** transaction-based housing prices from INE.

Growth comparisons across this break must acknowledge the change in the
measurement source. These are **national indices**, not municipality-level
sale medians or price levels in euros per square metre; the real series is
already CPI-deflated.

BIS [permits use of statistical data](https://data.bis.org/help/legal)
subject to attribution, no implied endorsement and conditions including
no additional charge for the statistics in commercial products. Those
conditions cover Data Portal statistics, not a blanket licence to copy
BIS publications, logos or third-party works. **External-only reference:**
the research project already pins its response files; no bytes are mirrored.
