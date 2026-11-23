# BLS rent of primary residence: U.S. and 16 metropolitan areas, with all-items CPI-U

Eighteen responses kept byte for byte: the CPI-U index of rent of primary residence (not seasonally adjusted) for the U.S. city average and for sixteen metropolitan areas that also have an S&P CoreLogic Case-Shiller home price index, plus the all-items CPI-U. Retrieved from FRED's graph CSV endpoint, and from DBnomics for the two areas whose current BLS series FRED does not carry (Washington, and Los Angeles after 2017). Snapshotted because both services serve only the latest vintage. Metropolitan rent indices are published monthly, bimonthly, semiannually or annually depending on the area and period; each file keeps the frequency it was served in.

## Why this dataset is canonical

`DiogoRibeiro7/Medium-Blog` (folder `rent-or-buy-us`) carries each metropolitan area's rent forward and backward from a level measured in one year, so it needs these indices exactly. FRED and DBnomics serve only the latest vintage and BLS revises area definitions, so the registry keeps the responses byte for byte, with checksums.

## Upstream identity

- Publisher: U.S. Bureau of Labor Statistics, retrieved through FRED (Federal Reserve Bank of St. Louis) and DBnomics
- Source: https://www.bls.gov/cpi/
- Retrieved: **2026-11-22** (FRED fredgraph.csv with coed=2025-12-31 and DBnomics API v22, retrieved 2026-11-22T23:12Z to 23:14Z by a GitHub Actions run of this repository)
- Licence: U.S. Government work, public domain (17 U.S.C. 105) (https://www.bls.gov/opub/copyright-information.htm); redistribution allowed

## Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw/CPIAUCNS.csv` | 24,922 | `2f72ee1766c487a1ab631bfcf161ef6743858e59a331b57da36d89c5496f7fa0` |
| `raw/CUUR0000SEHA.csv` | 22,961 | `62795a0ad3241321ea98ce53732950e2ba35551ff044699749f2ef088f6376ba` |
| `raw/CUURS35ASEHA.dbnomics.json` | 28,479 | `2166c29c5e0002d0705f6e223063af5984d7a3850624a2206f94ed91861498cc` |
| `raw/CUUSA101SEHA.csv` | 1,626 | `68b99324e239ecb947d5f943cb7e0dd51630683460ff2f1c306cc2ca5d4dbfb9` |
| `raw/CUUSA103SEHA.csv` | 828 | `74ac2970a5985f3d9d79d3786ab0721b7ceebe09821e01ff3812acb37f8e66b9` |
| `raw/CUUSA207SEHA.csv` | 1,626 | `029b7c4ae128659a5808f7d6ca30a8fba5d334c721fc8aab0f03ad5f259dc983` |
| `raw/CUUSA208SEHA.csv` | 1,626 | `9829b6db8abbdc4b59e17c6973d5c446f354e3824717f007d602378188f022f3` |
| `raw/CUUSA211SEHA.csv` | 828 | `ef6d38308d569f26fe9e512d3bdfc088c366f02a119433fd170bd997e3b54957` |
| `raw/CUUSA316SEHA.csv` | 828 | `b3485b36100c4d58058780f5dbcea208a58da5f044c95967792d4c7ce61755ed` |
| `raw/CUUSA319SEHA.csv` | 1,626 | `5c1b64f96531f5ac62da29ee22308c80ffae432c334d0f5e253c8494cc8006e2` |
| `raw/CUUSA320SEHA.csv` | 1,626 | `100caed017b8d8374b3b75f337b49d3b9a50ccfe416de88bc0706f747c7b26e3` |
| `raw/CUUSA321SEHA.csv` | 771 | `f31b79d12cab2f4d8c275a42dc4c0dfdbbae7cdef7e12f99a3922c54003304b5` |
| `raw/CUUSA422SEHA.csv` | 1,626 | `b24494606a4f34cf582174a581c8001ceec1245428fca182e556ae13a95113d9` |
| `raw/CUUSA423SEHA.csv` | 1,626 | `0f35f4003e460e99491600821234142f1d3f56f2c01d8fd1a098914234b64677` |
| `raw/CUUSA424SEHA.csv` | 828 | `d3052a9b518addb597bec545b90305f48b76fdae9abaf90302317d6d5c956808` |
| `raw/CUUSA429SEHA.csv` | 486 | `10f4408cc69566ce83d3883369fcb43e67b05c0b3c8cdb15d25c698191459d62` |
| `raw/CUUSA433SEHA.csv` | 828 | `7c7822e0c7c9278b0f08ea93e6fe59fd6bb421de147bbbf708e57fe4fbd01357` |
| `raw/CUUSS49ASEHA.dbnomics.json` | 21,091 | `df46ac6c201f5efbd5bdab9b11bee98dc13d5d7f36fd5187a3d29fc9e188ecdd` |

`metadata.yaml` records what each file holds and the exact query that produced it.

## Citation

U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers, rent of primary residence (SEHA) and all items (SA0), retrieved from FRED and DBnomics, 22 November 2026.
