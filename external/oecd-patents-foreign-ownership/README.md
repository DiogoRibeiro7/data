# OECD patent statistics: foreign ownership of domestic inventions (PCT and EPO, priority date)

Patent applications with at least one inventor resident in the country, and those owned by applicants abroad. The consumer reads, for every reporting country, the count of inventions (partner W), those owned abroad (WXD, world excluding the domestic country) and those owned by US applicants, under the PCT (9P50_1) and the EPO (6F0), by priority date; and, for six inventor countries, the counts by every owner country.

## Pinned identity

Retrieved on 24 November 2026. The consumer checks each response against the SHA-256 below and stops if the publisher has revised it.

| File | Dataflow | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `patents_foreign.csv` | `DSD_PATENTS@DF_PATENTS_FOREIGN` | 3,013,768 | `18bfd5d3990bae6ae861b3d504bea33b58b66deea39d4b162de70f6b4af90c66` |
| `patents_owners.csv` | `DSD_PATENTS@DF_PATENTS_FOREIGN` | 3,037,908 | `68739f108ef6d8a4d8677c3d8a666be68e5daac3da6a0311939855095cd45d1a` |

Requests:

- `patents_foreign.csv`: <https://sdmx.oecd.org/public/rest/data/OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_FOREIGN,1.0/9P50_1+6F0.A.AP.PATN.PRIORITY..W+WXD+USA....?format=csvfile>
- `patents_owners.csv`: <https://sdmx.oecd.org/public/rest/data/OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_FOREIGN,1.0/9P50_1.A.AP.PATN.PRIORITY.GBR+DEU+FRA+ITA+NLD+SWE.....?format=csvfile>

The OECD endpoint refuses Python's default user-agent string; the consumer sends its own.

## Licence

OECD Terms and Conditions (verify any third-party or series-specific rights). No bytes are mirrored in this registry.

## Consumers

- `medium-blog/uk-innovation-ownership`: `DiogoRibeiro7/Medium-Blog`, folder `uk-innovation-ownership`, fetched and checked by `fetch_data.py`.
