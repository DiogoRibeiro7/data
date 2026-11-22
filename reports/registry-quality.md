# Registry quality and coverage

This report is generated deterministically from committed repository state.
It makes no live network requests.

## Canonical registry

- Canonical datasets: **9**
- Canonical files: **49**
- Files with verified SHA-256: **49**
- Canonical datasets with complete licence metadata: **9**

## External sources

- External source records: **70**
- Redistribution resolved / unresolved: **35 / 35**
- Sources pinned to an immutable Git commit: **9**

External source usage annotations:

- Referenced consumer repositories: **25**
- Source usage references: **69**

- `causal-uplift-marketing-campaign`
- `cpd-stress-test`
- `crop-protection-predictive-science`
- `displacement-risk-lab-dynamodb`
- `ds-projects-portfolio`
- `empirical-analysis-r`
- `medium-blog/auction-entry-boem`
- `medium-blog/bid-rigging-screens`
- `medium-blog/europe-industrial-regions`
- `medium-blog/growth-finite-world`
- `medium-blog/model-swap-tails`
- `medium-blog/portugal-debt-2035-probability`
- `medium-blog/portugal-fiscal-reaction`
- `medium-blog/post-cutoff-forecasting`
- `medium-blog/ranking-extremes`
- `medium-blog/rent-or-buy-us`
- `medium-blog/suffrage-public-health`
- `medium-statistical-dynamics`
- `perishable-inventory-decision-lab`
- `porto-metro-demand-analysis`
- `portugal-housing-generations`
- `portugal-living-standards-reassessment`
- `productivity_taxation_inequality_project`
- `social-security-housing-investment`
- `wealth_rentier_dynamics`

## Canonical consumer adoption

- Active consumer repositories: **3**
- Active canonical relationships: **8**
- Deprecated relationships: **0**
- Pinned contracts: **8 / 8**
- Pinned contract coverage: **100%**
- Canonical datasets with >=1 active consumer: **8**
- Canonical datasets with zero active consumers: **1**
- Canonical dataset adoption coverage: **89%**
- Lifecycle migration coverage: **100%** (0 / 0)
- Migration required / planned / retained / migrated: **0 / 0 / 0 / 0**

Active consumers:

- `city-wage-cost-global`
- `displacement-risk-lab-dynamodb`
- `medium-blog`

## Canonical expansion

- Baseline snapshot: **snapshot-2026.10.05**
- Baseline canonical datasets: **2**
- Current canonical datasets: **9**
- Added since baseline: **7**
- Added with active consumers: **6**
- Added with exemptions: **1**
- Uncovered canonical datasets: **0**

Datasets added since baseline:

- `bls-cpi-rent-us-metros`
- `census-acs-housing-costs-msa`
- `eurostat-services-energy-time`
- `eurostat-services-relative-prices`
- `ine-portugal-new-lease-rents`
- `ons-gross-median-weekly-pay`
- `unhcr-refugee-population-2024`

Adoption exemptions:

- `ine-portugal-new-lease-rents`: Source promotion precedes the planned data-platform-lab INE adapter. The reviewed contract is pinned at cf1bd2f9de0ecdc95e6f1390c185f00b08df84db (https://github.com/DiogoRibeiro7/data-platform-lab/pull/106); it is not an implemented consumer. Remove this exemption when the platform registers its actual implementation commit, merged registry commit, canonical paths and all source hashes.

## Legacy quarantine

- Remaining packages: **2**
- Unresolved packages: **2**

## Provenance and licensing debt

- Total debt items: **38**
- External actionable / terminal: **11 / 24**
- Legacy actionable / terminal: **0 / 2**
- Oldest review date: **2026-10-05**
- Oldest deterministic debt age (days): **48**

Debt by blocker category:

- `authoritative-source-identity`: **1**
- `dataset-vs-repository-licence-scope`: **3**
- `exact-snapshot-identity`: **3**
- `historical-export-route`: **1**
- `redistribution-rights`: **29**

## Generated catalog freshness

- Canonical catalog current: **true**
- External catalog current: **true**
- Consumer catalog/graph current: **true**

## Snapshot coverage

- Snapshot/release count available from committed repository state: **false**
- Note: Published snapshot tags/releases are not counted because their presence depends on Git fetch depth and remote state rather than committed files.

## Interpretation

An unresolved redistribution state is not treated as an invalid record. It means the registry intentionally lacks sufficient evidence to claim redistribution permission.
Canonical consumer adoption is measured only from formal `consumers/` records. External-source consumer annotations remain separate source-usage hints and are not counted as canonical consumer contracts.
