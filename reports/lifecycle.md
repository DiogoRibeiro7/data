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
- Migration needed: **0**

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

| Consumer | Dataset | State | Preferred dataset |
| --- | --- | --- | --- |
| `city-wage-cost-global` | `ons-gross-median-weekly-pay` | current | `ons-gross-median-weekly-pay` |
| `displacement-risk-lab-dynamodb` | `ucdp-ged-25-1` | current | `ucdp-ged-25-1` |
| `displacement-risk-lab-dynamodb` | `unhcr-refugee-population-2024` | current | `unhcr-refugee-population-2024` |
| `medium-blog` | `online-retail-ii` | current | `online-retail-ii` |

## Semantics

- Missing lifecycle metadata is interpreted as `active`.
- Replacement edges are derived from committed `supersedes` and `superseded_by` declarations.
- A superseded dataset's preferred replacement is the active terminal dataset in its replacement chain.
- Consumer migration state is informational here; explicit retention/waiver semantics are defined separately.
