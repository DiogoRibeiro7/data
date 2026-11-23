# INE Portugal municipal population, housing, schools, transport and hospital indicators

Statistics Portugal (INE) publishes, through its [public API](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api_v2&xlang=pt), municipal series on resident population, the 2021 census (dwellings, households, crowding, commuting), local housing prices and rents, declared income, births and deaths, school enrolment rates and hospitals. This record pins the 46 responses that one consumer uses to compare population growth with the capacity of housing, schools, transport and hospitals in the 308 municipalities.

## Consumer contract

`Medium-Blog/portugal-infrastructure-saturation` downloads each response with `fetch.py` and checks it against the content hash recorded in `metadata.yaml` and in the consumer's `data_sources/ine-portugal-municipal-infrastructure.json`. All 46 were retrieved on 23 November 2026.

| Theme | Indicators |
| --- | --- |
| Population | `0008273` (estimates, NUTS 2013), `0012918` (estimates, NUTS 2024), `0014630` (census 2021 by age), `0011631` (census 2021 residence one year before), `0011613` (census 2021 density), `0012450` births, `0012538` deaths |
| Housing | `0014624` dwellings by occupancy, `0014622` main residences by tenure, `0012507` crowding, `0012534` and `0012488` dwelling and household change 2011-2021, `0012255` median sale price, `0014698` median new-lease rent, `0012741` median income per tax household |
| Transport | `0011794` and `0011795` mean commute by mode, `0011655` out-commuting share, `0012340` census work/study interactions with Lisboa and Porto |
| Schools | `0009550`, `0009552`, `0009555` (2011/12) and `0012616`, `0012614`, `0012615` (2024/25) gross enrolment rates |
| Hospitals | `0012885` hospitals, `0012893` beds in public universal-access and PPP hospitals, `0012892` bed occupancy |

## Why a content hash

Every INE response carries the time of extraction (`DataExtracao`), so two downloads of identical data differ byte for byte. The pin is therefore the SHA-256 of the indicator code, INE's last-update date (`DataUltimoAtualizacao`) and the data block (`Dados`), serialised as compact JSON with sorted keys in UTF-8. Two downloads of the same vintage give the same hash; a revision does not, and the consumer then stops unless it is run with `--accept-revision`.

The annual population estimates (`0008273`, `0012918`) are the series INE published on 22 June 2026: its first estimates built entirely from administrative sources (for 2025), with 2021-2024 revised by the same method. The revised estimate for 31 December 2021 exceeds the 2021 census count by about 256,000 residents, most of them in the Lisbon area. Consumers should not mix census counts and revised estimates in one ratio without saying so.

## Reuse and registry decision

INE allows reuse of its statistical information under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: **Fonte: Instituto Nacional de Estatística, I.P. – Portugal**, with the indicator code, the period and any transformation.

**Metadata-only external record.** INE remains the byte source; no responses are mirrored here or in Medium-Blog. The broader INE housing family is described in [`ine-portugal-housing-statistics`](../ine-portugal-housing-statistics/README.md); this record does not claim that its responses are the same snapshots as that record's consumers.
