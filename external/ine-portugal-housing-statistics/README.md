# INE Portugal housing, construction, and household statistics

This external record identifies official statistical series retrieved directly
from Statistics Portugal's (INE) public API for research on housing supply,
prices, population, construction, and household conditions in Portugal.

## Authoritative source and scope

- Publisher: Instituto Nacional de Estatística, I.P. (INE / Statistics Portugal).
- Interface: [INE API](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api_v2&xlang=pt).
- Illustrative series: [0000076](https://www.ine.pt/xurl/indx/0000076/PT),
  dwellings completed in new construction for family housing, and
  [0011725](https://www.ine.pt/xurl/indx/0011725/PT), its separately defined
  longer national series. The two should not be assumed equivalent.
- Attribution: **Fonte: Instituto Nacional de Estatística, I.P. – Portugal**,
  including indicator, period, and any transformations used.

This record describes official API outputs, **not** PORDATA exports or files
transcribed from PORDATA. The separate
[`pordata-portugal-resident-population`](../pordata-portugal-resident-population/README.md)
rights decision remains unchanged.

## Reuse and provenance

INE permits reuse of its statistical information under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), with attribution.
See INE's [portal terms](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_cont_inst&INST=3585857&xlang=pt)
and [API documentation](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api_v2&xlang=pt).

The downstream [`portugal-housing-generations` v1.0.0 research](https://github.com/DiogoRibeiro7/portugal-housing-generations/tree/0407faed1f08209b3d7682e19fc57e7120e62879)
records 37 API response containers retrieved on 29–30 October 2026. It maintains
an [itemized source and rights inventory](https://github.com/DiogoRibeiro7/portugal-housing-generations/blob/0407faed1f08209b3d7682e19fc57e7120e62879/docs/data-sources.md)
and [SHA-256 checksums](https://github.com/DiogoRibeiro7/portugal-housing-generations/blob/0407faed1f08209b3d7682e19fc57e7120e62879/data/SHA256SUMS).
These are *project-local retrieval identities*, not immutable upstream versions.

Some series have provisional vintages, territorial classification changes, or
non-identical statistical definitions. Consumers must retain each indicator's
metadata rather than treating overlapping date ranges as interchangeable.

## Registry decision

**Metadata-only external record.** No INE API bytes are copied into the central
registry. Source versions may change, while the research project already pins
its own exact dated responses and checksums. Canonical promotion would require
selection of a concrete reusable snapshot and a registered, pinned downstream
consumer contract.
