# Canonical dataset lifecycle

This report is generated deterministically from committed canonical metadata
and the committed consumer catalog. Do not edit it by hand.

- Canonical datasets: **4**
- Active: **4**
- Deprecated: **0**
- Superseded: **0**
- Replacement edges: **0**
- Active consumer relationships: **4**
- Current consumer relationships: **4**
- Migration required: **0**
- Migration planned: **0**
- Intentionally retained: **0**
- Historical migrated relationships: **0**
- Migration needed: **0**
- Migration resolution coverage: **100%**

## Dataset lifecycle

| Dataset | Status | Direct replacement | Preferred dataset | Consumers | Migration needed |
| --- | --- | --- | --- | ---: | ---: |
| `online-retail-ii` | active | -- | online-retail-ii | 1 | 0 |
| `ons-gross-median-weekly-pay` | active | -- | ons-gross-median-weekly-pay | 1 | 0 |
| `ucdp-ged-25-1` | active | -- | ucdp-ged-25-1 | 1 | 0 |
| `unhcr-refugee-population-2024` | active | -- | unhcr-refugee-population-2024 | 1 | 0 |

## Replacement chains

- No supersession chains are currently registered.

## Consumer migration state

| Consumer | Dataset | State | Preferred dataset | Rationale |
| --- | --- | --- | --- | --- |
| `city-wage-cost-global` | `ons-gross-median-weekly-pay` | current | `ons-gross-median-weekly-pay` | -- |
| `displacement-risk-lab-dynamodb` | `ucdp-ged-25-1` | current | `ucdp-ged-25-1` | -- |
| `displacement-risk-lab-dynamodb` | `unhcr-refugee-population-2024` | current | `unhcr-refugee-population-2024` | -- |
| `medium-blog` | `online-retail-ii` | current | `online-retail-ii` | -- |

## Semantics

- Missing lifecycle metadata is interpreted as `active`.
- Replacement edges are derived from committed `supersedes` and `superseded_by` declarations.
- A superseded dataset's preferred replacement is the active terminal dataset in its replacement chain.
- Active consumers of superseded/deprecated datasets are classified as required, planned, or retained.
- Retained historical consumption requires an explicit rationale.
- Deprecated historical relationships may record migration.status=migrated when a matching active target relationship exists.
