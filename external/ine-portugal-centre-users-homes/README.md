# INE Portugal municipal in-commuting, employees by place of work, tourist beds and dwellings completed

Statistics Portugal (INE) publishes, through its [public API](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api_v2&xlang=pt), municipal series that count the people who use a municipality without living in it, and the dwellings added to it. This record pins the nine responses that one consumer uses to compare the users and the residents of Lisbon, Porto and the rest of their metro areas.

## Consumer contract

`Medium-Blog/centres-users-residents` downloads each response with `fetch.py` and checks it against the content hash recorded in `metadata.yaml` and in the consumer's `data_sources/ine-portugal-centre-users-homes.json`. All nine were retrieved on 23 November 2026.

| Theme | Indicator | Periods |
| --- | --- | --- |
| People entering the municipality to work or study, % of its residents (census 2021) | `0011654` | 2021 |
| Full-time employees on full pay by place of work and size of establishment (MTSSS/GEP, Quadros de Pessoal) | `0012650` | 2021, 2024 |
| Bed capacity in tourist accommodation establishments, total of all types | `0013366` | 2023, 2025 |
| Dwellings completed in new construction for family housing, total of all promoters | `0013249` | 2022 to 2025 |

The same consumer also re-downloads 18 responses pinned in [`ine-portugal-municipal-infrastructure`](../ine-portugal-municipal-infrastructure/README.md).

## Why a content hash

Every INE response carries the time of extraction (`DataExtracao`), so two downloads of identical data differ byte for byte. The pin is therefore the SHA-256 of the indicator code, INE's last-update date (`DataUltimoAtualizacao`) and the data block (`Dados`), serialised as compact JSON with sorted keys in UTF-8. A revision changes the hash and the consumer stops unless it is run with `--accept-revision`.

## Things a consumer has to handle

- **Quadros de Pessoal** covers employers that file the annual return (essentially the private sector); public administration and the self-employed are outside it. The indicator counts full-time employees on full pay only. Two establishment-size bands are withheld for confidentiality in 2021 in the Porto metro area (Arouca, Espinho).
- **Tourist beds** come from INE's survey of stays in hotels and other accommodation. Local accommodation enters the survey only above a size threshold, so small short-term rentals are not counted.
- **Dwellings completed** in 2024 and 2025 are INE estimates of completed works, and figures from 2021 on are preliminary. Dwellings created by rehabilitation, extension or conversion are not in this indicator. INE's sign `-` (nil) is a zero.

## Reuse and registry decision

INE allows reuse of its statistical information under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: **Fonte: Instituto Nacional de Estatística, I.P. – Portugal**, with the indicator code, the period and any transformation; for `0012650`, the primary source is MTSSS/GEP, Quadros de Pessoal.

**Metadata-only external record.** INE remains the byte source; no responses are mirrored here or in Medium-Blog.
