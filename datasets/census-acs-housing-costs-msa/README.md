# Census ACS 1-year 2022 and 2023: home values, rents, property taxes, rooms and tenure

Twelve table-based summary files of the American Community Survey 1-year estimates, kept byte for byte: median value of owner-occupied homes (B25077), median gross rent (B25064), median contract rent (B25058), median real estate taxes paid (B25103), median rooms by tenure (B25021) and tenure counts (B25003), for 2022 and 2023, every geography in the release including the nation and metropolitan statistical areas. Used to set price, rent and property-tax levels in one year so that index series can be turned into dollars. Taken from the static summary-file directory because the Census data API now requires a key.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `rent-or-buy-us`) uses one year of ACS medians to turn the Case-Shiller and CPI rent indices into dollar prices and rents, and to set each area's property-tax rate. The Census data API now requires a key, so the static summary files are kept byte for byte.

## Upstream identity

- Publisher: U.S. Census Bureau, American Community Survey
- Source: https://www2.census.gov/programs-surveys/acs/summary_file/
- Retrieved: **2026-11-22** (ACS 1-year table-based summary files for 2022 and 2023, retrieved 2026-11-22T23:16Z to 23:21Z by a GitHub Actions run of this repository)
- Licence: U.S. Government work, public domain (17 U.S.C. 105) (https://www.census.gov/about/policies/open-gov/open-data.html); redistribution allowed

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/acsdt1y2022-b25003.dat` | 404,058 | `22c09f45723ed43180f25b10981af810ffc987620cc45ca876f92f39631c948b` |
| `raw/acsdt1y2022-b25021.dat` | 325,767 | `49e159e4b33bd3a64df57d2b668d6d20b9a45cbd7e09ffb6b74f60162f54dc6f` |
| `raw/acsdt1y2022-b25058.dat` | 193,615 | `266fb607162c54b779962f9b749c5aff3c4819cd8dbb5a85c282e351b7901fed` |
| `raw/acsdt1y2022-b25064.dat` | 195,396 | `be6ade6aec499d220158c9e6d15d0b51e46b825e469b6178169ca00aa0cfb911` |
| `raw/acsdt1y2022-b25077.dat` | 234,051 | `2ce7a81314c8290186972e1675f3fbea3bfd19dab53cd8f206c2964130a40eb5` |
| `raw/acsdt1y2022-b25103.dat` | 348,022 | `4b618086bbed7027b8528c106f5db653cdcee4da9831e94f93ccf54fde6f826a` |
| `raw/acsdt1y2023-b25003.dat` | 404,176 | `92fcc05c45c28592796fcbb17a935dac383ab1cd62e0bbd6a7595a48afe209ed` |
| `raw/acsdt1y2023-b25021.dat` | 325,778 | `bd082617acd8fafd2bdde3a162745abb2e8b3fe960118734ba9327f7d6b01f9d` |
| `raw/acsdt1y2023-b25058.dat` | 194,401 | `f7edc919db8537508185a682744e7d83f5a0c9b28e7c2ee9d42ee71b4701cc1f` |
| `raw/acsdt1y2023-b25064.dat` | 196,335 | `f45d5674900b087021e00a4c728ae52ff16d5fbeb856ef9198240d45887d376f` |
| `raw/acsdt1y2023-b25077.dat` | 234,323 | `c39987ce683bc4ac8d5831ac9fb67cbcdfaa9bbb81193bc3af4582ad97353723` |
| `raw/acsdt1y2023-b25103.dat` | 349,456 | `d0ddc93d6a790afa95b0e8660e0620b09117be7bcf0a857ea1e03e38a3fbcd82` |

`metadata.yaml` records what each file holds and the exact query that produced it.

## Citation

U.S. Census Bureau, American Community Survey 1-year estimates, 2022 and 2023, tables B25003, B25021, B25058, B25064, B25077 and B25103, table-based summary files, retrieved 22 November 2026.
