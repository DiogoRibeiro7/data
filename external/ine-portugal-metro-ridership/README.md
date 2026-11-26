# INE Portugal metro survey, Lisbon airport passengers, regional bus and river-line passengers

Statistics Portugal (INE) publishes, through its [public API](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api_v2&xlang=pt), a monthly survey of the three Portuguese metro systems (Metropolitano de Lisboa, Metro do Porto, Metro Sul do Tejo) and annual surveys of road and river passenger transport. This record pins the seven responses that one consumer uses to study the fall in Lisbon metro ridership in 2025 and 2026.

## Consumer contract

`Medium-Blog/lisbon-metro-ridership` downloads each response with `fetch.py` and checks it against the hash recorded in `metadata.yaml` and in the consumer's `data_sources/ine-portugal-metro-ridership.json`. All seven were retrieved on 26 November 2026.

| Theme | Indicator | Periods |
| --- | --- | --- |
| Passengers carried, by metro system (thousands) | `0000898` | January 2004 to August 2026, monthly |
| Passenger-km, by metro system (thousands) | `0000899` | January 2004 to August 2026, monthly |
| Place-km offered, by metro system (thousands) | `0000900` | January 2004 to August 2026, monthly |
| Passengers embarked, Lisbon airport (LPPT), all traffic | `0000861` | January 2015 to August 2026, monthly |
| Passengers disembarked, Lisbon airport (LPPT), all traffic | `0000862` | January 2015 to August 2026, monthly |
| Passengers of road transport companies, by NUTS II region of origin and type of service (thousands) | `0013815` | 2023 to 2025 |
| Passengers on inland waterway lines, by line | `0000896` | 2019, 2023 to 2025 |

The same consumer also re-downloads two population responses pinned in [`ine-portugal-municipal-infrastructure`](../ine-portugal-municipal-infrastructure/README.md).

## Why a data hash

Every INE response carries the time of extraction (`DataExtracao`) and the date of the indicator's last update (`DataUltimoAtualizacao`). For the monthly metro and airport series that date moves every month, when INE adds a new month, even if none of the months requested here changes. Each query therefore names its periods, and the pin is the SHA-256 of the indicator code (`IndicadorCod`) and the data block (`Dados`) only, serialised as compact JSON with sorted keys in UTF-8. A revision of a requested month changes the hash and the consumer stops unless it is run with `--accept-revision`.

## Things a consumer has to handle

- **Metro passengers** for Lisbon equal the operator's total: trips on a valid ticket plus its estimate of fare evasion (4.8 million in 2024). Metro Sul do Tejo appears in the series from 2014; earlier months are zero.
- **Place-km** measure capacity (places, seated and standing, times kilometres), not frequency: longer trains raise them without more trains.
- **Passenger-km** move irregularly in some months of 2023 and 2024; ratios built on them should be read over whole years.
- **Bus passengers** are counted by the NUTS II region where the trip starts, on the 2024 NUTS: the Lisbon metro area is split into Grande Lisboa (`1A`) and Península de Setúbal (`1B`). Regular services are type of service `111`.
- **Airport passengers** are the sum of embarked and disembarked, all traffic (`dim_3 = T`, `dim_4 = T`).

## Reuse and registry decision

INE allows reuse of its statistical information under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: **Fonte: Instituto Nacional de Estatística, I.P. – Portugal**, with the indicator code, the period and any transformation.

**Metadata-only external record.** INE remains the byte source; no responses are mirrored here or in Medium-Blog.
