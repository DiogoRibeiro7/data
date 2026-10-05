# Provenance and licensing debt queue

This file is generated deterministically from committed external and legacy metadata.
Do not edit it by hand.

- Total debt items: **6**
- External records: **4**
- Legacy packages: **2**
- Structured evidence: **1**
- Unstructured debt: **5**
- Actionable: **0**
- Terminal: **1**
- Age reference date: **2026-10-05**

## Blocker categories

- `dataset-vs-repository-licence-scope`: **1**
- `unstructured`: **5**

## Queue

| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| external | `dgs-infoclique-mortality` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unresolved | Backfill structured resolution evidence. |
| external | `ibm-telco-customer-churn` | terminal | The pinned IBM repository is Apache-2.0 licensed as a code pattern, but the README explicitly separates third-party objects and no dataset-specific redistribution licence for Telco-Customer-Churn.csv was established. | 2026-10-05 | 0 | 3 | unresolved | Reopen only if IBM publishes dataset-specific terms or an authoritative licence statement covering Telco-Customer-Churn.csv. |
| external | `maize-bipolaris-disease-progress` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unresolved | Backfill structured resolution evidence. |
| external | `pordata-portugal-resident-population` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unresolved | Backfill structured resolution evidence. |
| legacy | `country-age-sex-2019` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unknown | Backfill structured resolution evidence. |
| legacy | `portugal-covid19` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unknown | Backfill structured resolution evidence. |

## Age semantics

Age is deterministic and content-based. When structured review dates exist,
the reference date is the latest `last_reviewed` date present in the queue.
Items without structured review dates have no age value.

Unstructured debt remains visible so introducing the queue does not hide
records that have not yet been migrated to the structured resolution model.
