# Registry quality and coverage

This report is generated deterministically from committed repository state.
It makes no live network requests.

## Canonical registry

- Canonical datasets: **4**
- Canonical files: **4**
- Files with verified SHA-256: **4**
- Canonical datasets with complete licence metadata: **4**

## External sources

- External source records: **13**
- Redistribution resolved / unresolved: **9 / 4**
- Sources pinned to an immutable Git commit: **3**

External source usage annotations:

- Referenced consumer repositories: **4**
- Source usage references: **6**

- `cpd-stress-test`
- `crop-protection-predictive-science`
- `displacement-risk-lab-dynamodb`
- `productivity_taxation_inequality_project`

## Canonical consumer adoption

- Active consumer repositories: **3**
- Active canonical relationships: **4**
- Deprecated relationships: **0**
- Pinned contracts: **4 / 4**
- Pinned contract coverage: **100%**
- Canonical datasets with >=1 active consumer: **4**
- Canonical datasets with zero active consumers: **0**
- Canonical dataset adoption coverage: **100%**

Active consumers:

- `city-wage-cost-global`
- `displacement-risk-lab-dynamodb`
- `medium-blog`

## Canonical expansion

- Baseline snapshot: **snapshot-2026.10.05**
- Baseline canonical datasets: **2**
- Current canonical datasets: **4**
- Added since baseline: **2**
- Added with active consumers: **2**
- Added with exemptions: **0**
- Uncovered canonical datasets: **0**

Datasets added since baseline:

- `ons-gross-median-weekly-pay`
- `unhcr-refugee-population-2024`

Adoption exemptions:

- None

## Legacy quarantine

- Remaining packages: **2**
- Unresolved packages: **2**

## Provenance and licensing debt

- Total debt items: **6**
- External actionable / terminal: **0 / 4**
- Legacy actionable / terminal: **0 / 2**
- Oldest review date: **2026-10-05**
- Oldest deterministic debt age (days): **0**

Debt by blocker category:

- `dataset-vs-repository-licence-scope`: **2**
- `exact-snapshot-identity`: **1**
- `historical-export-route`: **1**
- `redistribution-rights`: **2**

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
