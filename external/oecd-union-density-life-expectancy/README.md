# OECD SDMX responses: trade union density (DF_TUD) and life expectancy at birth (DF_LE), 13 countries, 1960-2024, retrieved 2026-11-28

External reference, no bytes stored. Publisher: Organisation for Economic Co-operation and Development (OECD); union density comes from the OECD/AIAS ICTWSS database. Source: the OECD SDMX REST interface, https://sdmx.oecd.org/public/rest/data.

Two SDMX-CSV responses for the United States, the United Kingdom, Austria, Belgium, Denmark, Finland, France, Germany, Italy, the Netherlands, Norway, Sweden and Switzerland, 1960-2024:

- **Trade union density**, per cent of employees: `OECD.ELS.SAE,DSD_TUD_CBC@DF_TUD,1.0`, key `<countries>.TUD.PT_SAL`.
- **Life expectancy at birth**, both sexes, years: `OECD.ELS.HD,DSD_HEALTH_STAT@DF_LE,1.1`, key `<countries>.A.LFEXP.Y.Y0._T.......`.

Two complete downloads 20 seconds apart on 28 November 2026 were byte-identical. The OECD serves only the current vintage, so the hashes identify this retrieval; after a revision the consumer stops unless run with `--accept-revision`.

Gaps kept as published: life expectancy for the United Kingdom is missing in 1962-1969 and 1972-1979, for Denmark in 1961-1966 and for Italy in several 1960s years; union density for the United States is missing in 1981-1982 and for France before 1971.

## Files the consumer verifies

| File | Bytes | SHA-256 | Query |
| --- | ---: | --- | --- |
| `external/tud.csv` | 58,395 | `c4b76973876f0a64f278647a3e5543159e387d39f405899162ddfd87b7a02928` | https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_TUD_CBC@DF_TUD,1.0/USA+GBR+AUT+BEL+DNK+FIN+FRA+DEU+ITA+NLD+NOR+SWE+CHE.TUD.PT_SAL?startPeriod=1960&endPeriod=2024&format=csvfile |
| `external/le.csv` | 78,897 | `e8d4eaa099fc754d9505a59478b8512a5d48c362940ee5c3c3f99215952f96bd` | https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_STAT@DF_LE,1.1/USA+GBR+AUT+BEL+DNK+FIN+FRA+DEU+ITA+NLD+NOR+SWE+CHE.A.LFEXP.Y.Y0._T.......?startPeriod=1960&endPeriod=2024&format=csvfile |

Consumer: `DiogoRibeiro7/Medium-Blog`, folder `social-contract-break-dates`, contract `data_sources/oecd-union-density-life-expectancy.json`.

## Reuse

OECD data are reusable with attribution under the OECD terms; rights to the national series inside ICTWSS were not reviewed, so redistribution of the bytes stays unresolved and nothing is mirrored.
