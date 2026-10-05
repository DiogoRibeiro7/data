# Provenance and licensing debt queue

This file is generated deterministically from committed external and legacy metadata.
Do not edit it by hand.

- Total debt items: **6**
- External records: **4**
- Legacy packages: **2**
- Structured evidence: **3**
- Unstructured debt: **3**
- Actionable: **0**
- Terminal: **3**
- Age reference date: **2026-10-05**

## Blocker categories

- `dataset-vs-repository-licence-scope`: **1**
- `redistribution-rights`: **2**
- `unstructured`: **3**

## Queue

| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| external | `dgs-infoclique-mortality` | terminal | DGS publicly disseminates SICO mortality information, but its current legal notice protects site contents and no dataset-specific redistribution grant covering the historical InfoClique/SICO CSV exports was recovered. | 2026-10-05 | 0 | 2 | unresolved | Reopen only if DGS publishes dataset-specific reuse terms or an authoritative open-data licence covering the historical mortality exports. |
| external | `ibm-telco-customer-churn` | terminal | The pinned IBM repository is Apache-2.0 licensed as a code pattern, but the README explicitly separates third-party objects and no dataset-specific redistribution licence for Telco-Customer-Churn.csv was established. | 2026-10-05 | 0 | 3 | unresolved | Reopen only if IBM publishes dataset-specific terms or an authoritative licence statement covering Telco-Customer-Churn.csv. |
| external | `maize-bipolaris-disease-progress` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unresolved | Backfill structured resolution evidence. |
| external | `pordata-portugal-resident-population` | terminal | INE permits rediffusion of official statistical information with source attribution, but the historical workbook was a PORDATA-generated Excel export and no authoritative term was recovered that clearly permits mirroring that secondary-source artifact. | 2026-10-05 | 0 | 3 | unresolved | Reopen only if PORDATA or FFMS publishes terms explicitly authorizing redistribution of exported table files, or if the registry replaces the artifact with a directly sourced INE representation under INE reuse terms. |
| legacy | `country-age-sex-2019` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unknown | Backfill structured resolution evidence. |
| legacy | `portugal-covid19` | — | Structured resolution evidence not yet recorded. | — | — | 0 | unknown | Backfill structured resolution evidence. |

## Age semantics

Age is deterministic and content-based. When structured review dates exist,
the reference date is the latest `last_reviewed` date present in the queue.
Items without structured review dates have no age value.

Unstructured debt remains visible so introducing the queue does not hide
records that have not yet been migrated to the structured resolution model.
