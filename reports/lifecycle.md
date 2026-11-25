# Canonical dataset lifecycle

This report is generated deterministically from committed canonical metadata
and the committed consumer catalog. Do not edit it by hand.

- Canonical datasets: **13**
- Active: **13**
- Deprecated: **0**
- Superseded: **0**
- Replacement edges: **0**
- Active consumer relationships: **12**
- Current consumer relationships: **12**
- Migration required: **0**
- Migration planned: **0**
- Intentionally retained: **0**
- Historical migrated relationships: **0**
- Migration needed: **0**
- Migration resolution coverage: **100%**

## Dataset lifecycle

| Dataset | Status | Direct replacement | Preferred dataset | Consumers | Migration needed |
| --- | --- | --- | --- | ---: | ---: |
| `bls-cpi-rent-us-metros` | active | -- | bls-cpi-rent-us-metros | 1 | 0 |
| `census-acs-housing-costs-msa` | active | -- | census-acs-housing-costs-msa | 1 | 0 |
| `eurostat-eu-convergence-education` | active | -- | eurostat-eu-convergence-education | 1 | 0 |
| `eurostat-food-vat-incidence` | active | -- | eurostat-food-vat-incidence | 1 | 0 |
| `eurostat-material-use` | active | -- | eurostat-material-use | 1 | 0 |
| `eurostat-services-energy-time` | active | -- | eurostat-services-energy-time | 1 | 0 |
| `eurostat-services-relative-prices` | active | -- | eurostat-services-relative-prices | 1 | 0 |
| `ine-portugal-new-lease-rents` | active | -- | ine-portugal-new-lease-rents | 0 | 0 |
| `oecd-share-prices-bond-yields-cpi` | active | -- | oecd-share-prices-bond-yields-cpi | 1 | 0 |
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
| `medium-blog` | `bls-cpi-rent-us-metros` | current | `bls-cpi-rent-us-metros` | -- |
| `medium-blog` | `census-acs-housing-costs-msa` | current | `census-acs-housing-costs-msa` | -- |
| `medium-blog` | `eurostat-eu-convergence-education` | current | `eurostat-eu-convergence-education` | -- |
| `medium-blog` | `eurostat-food-vat-incidence` | current | `eurostat-food-vat-incidence` | -- |
| `medium-blog` | `eurostat-material-use` | current | `eurostat-material-use` | -- |
| `medium-blog` | `eurostat-services-energy-time` | current | `eurostat-services-energy-time` | -- |
| `medium-blog` | `eurostat-services-relative-prices` | current | `eurostat-services-relative-prices` | -- |
| `medium-blog` | `oecd-share-prices-bond-yields-cpi` | current | `oecd-share-prices-bond-yields-cpi` | -- |
| `medium-blog` | `online-retail-ii` | current | `online-retail-ii` | -- |

## Semantics

- Missing lifecycle metadata is interpreted as `active`.
- Replacement edges are derived from committed `supersedes` and `superseded_by` declarations.
- A superseded dataset's preferred replacement is the active terminal dataset in its replacement chain.
- Active consumers of superseded/deprecated datasets are classified as required, planned, or retained.
- Retained historical consumption requires an explicit rationale.
- Deprecated historical relationships may record migration.status=migrated when a matching active target relationship exists.
