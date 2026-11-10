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

The independent `social-security-housing-investment` project also pins INE
snapshots, separately from the 37 files above. Its source manifests identify
construction cost **index** `0011748` (base 2021 = 100; not an absolute
construction cost in €/m²), new-lease rent indicators `0014698`, `0014711`
and `0014697`, census indicators and housing sales-price indicator `0012255`.
Those responses have their own reference periods, territorial versions and
SHA-256 checksums; adding this consumer does not claim identical snapshots.

The separate `empirical-analysis-r` housing study also records dated INE
snapshots, including 2022-methodology sales-price indicator `0012255`
(NUTS 2024) and resident-population indicator `0012918`. It distinguishes
older price methodology, missing published cells and municipality codes
verified against the independent DGT CAOP2025 register. This consumer
association does not reuse another project's retrieval hashes.

## Registry decision

**Metadata-only external record.** No INE API bytes are copied into the central
registry. Source versions may change, while the research project already pins
its own exact dated responses and checksums. Canonical promotion would require
selection of a concrete reusable snapshot and a registered, pinned downstream
consumer contract.

## Verified municipal series for wealth and rentier dynamics (November 2026)

The [wealth/rentier dynamics research](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/pull/63)
consumes municipal INE observations. The source identities below were checked against
INE's API metadata in [the R client audit](https://gitlab.com/DiogoRibeiro7/ine-data-client/-/merge_requests/38);
the 2021 Census extracts were separately validated in
[the Census acquisition](https://gitlab.com/DiogoRibeiro7/ine-data-client/-/merge_requests/39)
before the research repository committed its observed CSV snapshots.

| INE indicator | Measurement | Reference | Territorial classification | Municipality code | Extra dimension |
| --- | --- | --- | --- | --- | --- |
| `0012517` | Vacant dwellings, percent | 2021 Census | Census/NUTS2024 (`05320`) | 4 digits, level 5 | none |
| `0012466` | Private households, count | 2021 Census | Census/NUTS2024 (`05320`) | 4 digits, level 5 | household size `T` (total) |
| `0013249` | Completed family dwellings, count | annual | NUTS2024 (`05257`) | 7 digits, level 5 | promoter `T` (total) |
| `0008269` | Net migration, signed count | annual | NUTS2013 (`03505`) | 7 digits, level 5 | none |

The verified Census extract contains 308 municipal records per indicator,
without missing values. Its exact raw and normalised source hashes are recorded
in the downstream [Census snapshot PR](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/pull/63).
The annual flow acquisition is a **separate, unverified extraction stage**; the
[manual R-client job proposal](https://gitlab.com/DiogoRibeiro7/ine-data-client/-/merge_requests/40)
must not be mistaken for a validated or committed annual dataset.

### Reuse boundaries

- This registry records identifiers, provenance and consumers. It does **not**
  run INE ingestion, hold a mutable database, or copy these research snapshots.
- Keep each territorial classification and vintage explicit. In particular,
  `0008269` NUTS2013 and `0013249` NUTS2024 cannot be joined by raw
  geographic codes without a documented concordance.
- Treat counts and percentages as distinct units; do not sum percentages.
- A future cross-project canonical snapshot requires raw source bytes,
  transformation provenance, SHA-256 evidence, licensing and a pinned consumer
  contract under the existing registry policy.
- A separate Python data-engineering runtime can ingest and serve approved
  snapshots by following [the provider-neutral handoff](../../docs/INGESTION_HANDOFF.md);
  no database provider is selected by this record.
