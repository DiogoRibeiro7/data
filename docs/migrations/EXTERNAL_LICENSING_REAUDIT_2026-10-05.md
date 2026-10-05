# External licensing re-audit — 2026-10-05

This audit covers two Phase 6 external-source records:

- `unhcr-refugee-statistics`;
- `ibm-telco-customer-churn`.

## UNHCR Refugee Population Statistics

### Decision

**Redistribution resolved: allowed.**

### Evidence

UNHCR's Refugee Data Finder methodology states that, except where otherwise
indicated, datasets in the Refugee Population Statistics Database are licensed
under the Creative Commons Attribution 4.0 International licence.

UNHCR also publishes dataset-specific Terms of Use for the Refugee Population
Statistics Database. Those terms:

- explicitly apply to the database datasets;
- identify CC BY 4.0 as the governing licence unless otherwise provided;
- require attribution to the UNHCR Refugee Population Statistics Database;
- state that the dataset-specific terms prevail over conflicting general
  website terms.

Authoritative sources:

- https://www.unhcr.org/refugee-statistics/methodology
- https://www.unhcr.org/uk/terms-use-datasets

### Registry action

The external record now uses:

`redistribution: allowed`

and its licence URL points to the UNHCR dataset Terms of Use rather than only
the generic Creative Commons deed.

No canonical bytes are added by this audit.

## IBM Telco Customer Churn sample

### Decision

**Redistribution remains unresolved; blocker classified terminal.**

### Exact source

Pinned repository commit:

`d5371f5d83a446ad5673cbcca3b814b926491f8a`

Dataset path:

`data/Telco-Customer-Churn.csv`

### Evidence

At the exact pinned commit:

- the repository includes an Apache-2.0 `LICENSE`;
- the README describes the project as an IBM code pattern;
- the README states that separately licensed third-party objects remain under
  their respective providers' licences;
- no file-level or dataset-specific licence statement covering
  `Telco-Customer-Churn.csv` was recovered.

IBM issue #22 asks specifically whether the included dataset is Apache 2.0 or
otherwise freely licensed. The issue remains open without an authoritative
answer.

Evidence:

- https://github.com/IBM/telco-customer-churn-on-icp4d/blob/d5371f5d83a446ad5673cbcca3b814b926491f8a/README.md
- https://github.com/IBM/telco-customer-churn-on-icp4d/blob/d5371f5d83a446ad5673cbcca3b814b926491f8a/LICENSE
- https://github.com/IBM/telco-customer-churn-on-icp4d/issues/22

### Registry action

The record keeps:

`redistribution: unresolved`

and adds structured resolution evidence:

- status: `terminal`;
- blocker: `dataset-vs-repository-licence-scope`;
- review date: 2026-10-05;
- three evidence URLs;
- a reopen condition requiring new IBM dataset-specific licensing evidence.

No canonical promotion or byte mirroring is justified.

## Debt impact

Before this audit:

- unresolved external records: 5;
- total provenance/licensing debt items: 7;
- structured debt items: 0.

After this audit:

- unresolved external records: 4;
- total provenance/licensing debt items: 6;
- structured debt items: 1;
- terminal debt items: 1.
