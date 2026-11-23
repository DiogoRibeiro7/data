# OECD: share prices, long-term bond yields and consumer prices, 23 markets

Canonical snapshot of three OECD SDMX responses that give, for each of the 23
OECD members of 1973 without Turkey, a share price index, a ten-year
government bond yield and a consumer price index, monthly where the OECD has
them, from the 1950s to December 2025. With them a reader can compute real
share price returns and approximate real bond returns over any holding period.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `long-horizon-stock-risk`) needs these
series to reproduce its numbers exactly. The OECD SDMX API serves only the
current vintage of each dataflow, so a query cannot be pinned the way a Git
commit can. The registry keeps the responses byte for byte, with checksums, so
the downstream output does not change when the OECD revises a series. Since
July 2024 OECD data are published under Creative Commons Attribution 4.0,
which allows redistribution with attribution.

## Upstream identity

- Publisher: Organisation for Economic Co-operation and Development (OECD)
- Service: SDMX REST API, SDMX-CSV 1.0 (`https://sdmx.oecd.org/public/rest/data`)
- Dataflows: `OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0` (financial market
  statistics) and `OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0` (consumer prices)
- Retrieved: **2026-11-23T19:32:14Z** to **19:32:47Z**, every query ending at 2025-12
- `metadata.yaml` records the exact query string of each file.

## Files

| File | Bytes | Observations | SHA-256 |
| --- | ---: | ---: | --- |
| `raw/finmark_share.csv` | 1,553,774 | 16,030 | `fe8d95a1b4e513a2ece424e5089a605f0c7d2df03f4efecfe3b107c3f2642efa` |
| `raw/finmark_irlt.csv` | 1,230,857 | 13,858 | `4307f2d3cafdf5d2664fdd12ebba430d2e2a6679b1c54eb724e37eebd23786f3` |
| `raw/prices_cpi.csv` | 2,483,687 | 26,326 | `4102c7d14b927160ae646aba06a342b50e50844db98a4edc910602114ecaac36` |

What each file holds:

- `finmark_share.csv`: share price indices, monthly averages, 2015 = 100.
  **Prices only, without dividends.** Most markets start between 1955 and
  1960; Belgium, Denmark, Spain, Greece, Norway and Portugal start in the
  1980s, Iceland in 1993 and Luxembourg in 1999.
- `finmark_irlt.csv`: long-term interest rates, government bonds of about ten
  years, per cent a year, monthly averages. Japan starts in 1989, Italy in
  1991, Austria in 1990 and Greece in 1997; Iceland ends in August 2022.
- `prices_cpi.csv`: consumer price index, all items, national methodology,
  not seasonally adjusted, 2015 = 100, at monthly, quarterly and annual
  frequency. Australia and New Zealand are quarterly (Australia is monthly
  only from April 2024). Japan's series in this dataflow ends in June 2021.

The markets are Australia, Austria, Belgium, Canada, Switzerland, Germany,
Denmark, Spain, Finland, France, the United Kingdom, Greece, Ireland, Iceland,
Italy, Japan, Luxembourg, the Netherlands, Norway, New Zealand, Portugal,
Sweden and the United States.

## Notes for users

- The files are SDMX-CSV with CRLF line endings and a header row; every
  observation carries `OBS_STATUS` (A normal; in the share file, 5 observations
  are B, a break, and 2 are E, estimated).
- A bond yield is not a bond return. A total return has to be approximated,
  for example by pricing a par bond of constant maturity at successive yields.
- Monthly averages smooth turning points; returns between December averages
  are close to, but not the same as, returns between month ends.

## Licence and citation

Creative Commons Attribution 4.0 International; see the
[OECD terms and conditions](https://www.oecd.org/en/about/terms-conditions.html).
Cite: OECD, Financial market statistics (DSD_STES@DF_FINMARK, version 4.0)
and Consumer prices (DSD_PRICES@DF_PRICES_ALL, version 1.0), retrieved
23 November 2026.
