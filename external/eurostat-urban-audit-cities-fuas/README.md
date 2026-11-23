# Eurostat city statistics (Urban Audit): population, jobs and dwellings for cities and functional urban areas

Eurostat's city statistics give the same variables for two units of each European urban area: the **city** (a local administrative unit or, for the largest, a "greater city") and its **functional urban area** (FUA: the city plus the commuting zone in which at least 15% of employed residents work in the city). The rest of the FUA, outside the city, is its ring. This record pins the six responses that one consumer uses to compare growth of residents, jobs and dwellings between centres and rings.

## Consumer contract

`Medium-Blog/centres-users-residents` downloads each response with `fetch.py` and checks it against the SHA-256 recorded in `metadata.yaml` and in the consumer's `data_sources/eurostat-urban-audit-cities-fuas.json`. All six were retrieved on 23 November 2026 (Eurostat update of 12 November 2026).

| Variable | City | FUA | Indicator |
| --- | --- | --- | --- |
| Population on 1 January | `urb_cpop1` | `urb_lpop1` | `DE1001V` |
| Total employment (jobs), place of work | `urb_clma` | `urb_llma` | `EC2020V` |
| Number of conventional dwellings | `urb_clivcon` | `urb_llivcon` | `SA1001V` |

Each response is the full indicator for all units and years, requested as `?format=JSON&lang=EN&indic_ur=<indicator>` from `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<dataset>`.

## Why a byte hash

Eurostat serves identical bytes for identical data, so the pin is the SHA-256 of each response. A new Eurostat release changes the hash and the consumer stops unless it is run with `--accept-revision`.

## Things a consumer has to handle

- **Unit codes.** Cities end in `C` and FUAs in `F`. Two Swiss FUAs (`CH003`, `CH004`) also have a cross-border total coded `T`; mixing it with the `F` unit would double count.
- **Boundaries change.** FUA and some city delineations were revised between reference years, most visibly in Germany, where many rings lose 1-3% of their population, jobs and dwellings a year in the series. A dwelling stock rarely shrinks that fast, so the consumer drops FUAs whose dwellings fall by more than 0.5% a year, or whose people or jobs move faster than 3.5% and 8% a year.
- **Years differ by country.** Not every country reports every year; the consumer takes, for each FUA, the year closest to 2015 within 2014-2016 and to 2021 within 2020-2022 in which all six series exist.

## Reuse and registry decision

Eurostat allows reuse with attribution and disclosure of changes ([copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice)). Attribution: **Source: Eurostat, city statistics (urb_cpop1, urb_lpop1, urb_clma, urb_llma, urb_clivcon, urb_llivcon)**, with the transformation applied.

**Metadata-only external record.** Eurostat remains the byte source; no responses are mirrored here or in Medium-Blog.
