# JHU CSSE COVID-19 time series

Authoritative source record for the Johns Hopkins University Center for Systems Science and Engineering COVID-19 time-series data formerly stored under `legacy/jhu-covid19-time-series/`.

## Authoritative source

- Publisher: Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE)
- Repository: https://github.com/CSSEGISandData/COVID-19
- Historical source commit: `dd07d05ff02d8aea12cab868e8a36c0e31cadf66`
- Commit date: 2020-06-08
- Terms: repository-specific historical usage restrictions, not CC BY 4.0

The pinned 2020 README states that the website/data were provided for non-profit public-health, educational, and academic research purposes; commercial use was prohibited; and redistribution of the website or aggregated dataset was prohibited.

The upstream repository was later archived after Johns Hopkins ceased live COVID-19 reporting.

## Legacy snapshot identity

The five files previously retained in this repository were traced to the source commit above by Git blob identity.

| Former local file | Upstream file at pinned commit | Git blob SHA |
| --- | --- | --- |
| `time_series_covid_19_confirmed.csv` | `time_series_covid19_confirmed_global.csv` | `8971d90ba64f6f879ef5667f65e4b8be7ab448e9` |
| `time_series_covid_19_confirmed_US.csv` | `time_series_covid19_confirmed_US.csv` | `7aa25298d035acf6073bbeb3631ebb38b73cea52` |
| `time_series_covid_19_deaths.csv` | `time_series_covid19_deaths_global.csv` | `5b3a31095cd976836fe69c6026bf3e5e52f76e04` |
| `time_series_covid_19_deaths_US.csv` | `time_series_covid19_deaths_US.csv` | `ee5a796f1525d59f6de6741ca93970b93b9d80bd` |
| `time_series_covid_19_recovered.csv` | `time_series_covid19_recovered_global.csv` | `f3f257135aba93b7c4759600c0e0ddfe3347d63c` |

Because every historical file is recoverable from one exact upstream commit and no current repository consumer was found, the duplicate local legacy package was removed. This external record preserves provenance without claiming redistribution rights that the pinned source terms do not grant.
