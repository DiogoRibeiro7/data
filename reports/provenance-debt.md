# Provenance and licensing debt queue

This file is generated deterministically from committed external and legacy metadata.
Do not edit it by hand.

- Total debt items: **9**
- External records: **7**
- Legacy packages: **2**
- Structured evidence: **9**
- Unstructured debt: **0**
- Actionable: **0**
- Terminal: **9**
- Age reference date: **2026-10-14**

## Blocker categories

- `dataset-vs-repository-licence-scope`: **2**
- `exact-snapshot-identity`: **1**
- `historical-export-route`: **1**
- `redistribution-rights`: **5**

## Queue

| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| external | `dgs-infoclique-mortality` | terminal | DGS publicly disseminates SICO mortality information, but its current legal notice protects site contents and no dataset-specific redistribution grant covering the historical InfoClique/SICO CSV exports was recovered. | 2026-10-05 | 9 | 2 | unresolved | Reopen only if DGS publishes dataset-specific reuse terms or an authoritative open-data licence covering the historical mortality exports. |
| external | `ibm-telco-customer-churn` | terminal | The pinned IBM repository is Apache-2.0 licensed as a code pattern, but the README explicitly separates third-party objects and no dataset-specific redistribution licence for Telco-Customer-Churn.csv was established. | 2026-10-05 | 9 | 3 | unresolved | Reopen only if IBM publishes dataset-specific terms or an authoritative licence statement covering Telco-Customer-Churn.csv. |
| external | `maize-bipolaris-disease-progress` | terminal | The pinned repository has a root MIT licence and explicitly includes maize_bipolaris.csv as data, but the licence text covers software and associated documentation and no authoritative statement was recovered that explicitly applies MIT redistribution rights to the dataset bytes. | 2026-10-05 | 9 | 3 | unresolved | Reopen only if the author or another authoritative source explicitly states that the MIT licence covers maize_bipolaris.csv, or publishes separate dataset reuse terms. |
| external | `medium-crawlfeeds-corpus` | terminal | The Hugging Face card declares CC BY-SA 3.0, but the corpus contains scraped third-party Medium article bodies and no authoritative evidence establishes Crawlfeeds' right to relicense all embedded article text. Under the registry's conservative policy, redistribution remains unresolved and the record is terminal external-only. | 2026-10-14 | 0 | 5 | unresolved | Reopen only with authoritative rights evidence covering the pinned bytes. Retain external-only status; independently establish permitted local research use before acquisition. |
| external | `medium-fabiochiu-articles` | terminal | The Hugging Face dataset declares MIT and exposes revision 979af3bcd84565e3f47b9eca752d8ec112824953, but full-text files reproduce third-party Medium article bodies and no evidence establishes the publisher's authority to relicense that content. Redistribution remains unresolved and the record is terminal external-only. | 2026-10-11 | 3 | 4 | unresolved | Reopen only if authoritative evidence establishes redistribution rights for the exact full-text or no-text file(s), assessed separately. |
| external | `medium-jansma-historical` | terminal | The pinned research repository documents collection of roughly 1.4 million Medium stories and says the dataset was published for public use on Kaggle, but the actual dataset is off-repository, the GitHub repository has no LICENSE, and no authoritative dataset-specific redistribution licence for the exact Kaggle object was recovered. The record is terminal external-only. | 2026-10-11 | 3 | 4 | unresolved | Reopen only if the exact Kaggle object/version and authoritative dataset-specific redistribution terms are recovered. |
| external | `pordata-portugal-resident-population` | terminal | INE permits rediffusion of official statistical information with source attribution, but the historical workbook was a PORDATA-generated Excel export and no authoritative term was recovered that clearly permits mirroring that secondary-source artifact. | 2026-10-05 | 9 | 3 | unresolved | Reopen only if PORDATA or FFMS publishes terms explicitly authorizing redistribution of exported table files, or if the registry replaces the artifact with a directly sourced INE representation under INE reuse terms. |
| legacy | `country-age-sex-2019` | terminal | The retained age/sex files are strongly attributable to UN World Population Prospects 2019, whose publications are CC BY 3.0 IGO, but the exact download/export route and the lineage of the Portugal CSV/XLSX variants cannot be reconstructed sufficiently to claim file-level provenance for these historical artifacts. | 2026-10-05 | 9 | 2 | unknown | Reopen only if the original authoritative UN export identity can be tied to the retained files and the Portugal workbook/CSV lineage can be resolved. |
| legacy | `portugal-covid19` | terminal | The retained workbook is attributable to the GEP/MTSSS Indicadores COVID-19 monitoring series and dated 27 May 2020, but the exact historical workbook URL, immutable upstream identity and dataset-specific redistribution terms were not recovered. | 2026-10-05 | 9 | 2 | unknown | Reopen only if GEP/MTSSS exposes the exact 27 May 2020 workbook with stable identity and explicit redistribution terms. |

## Age semantics

Age is deterministic and content-based. When structured review dates exist,
the reference date is the latest `last_reviewed` date present in the queue.
Items without structured review dates have no age value.

Unstructured debt remains visible so introducing the queue does not hide
records that have not yet been migrated to the structured resolution model.
