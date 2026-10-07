# Provenance and licensing debt queue

This file is generated deterministically from committed external and legacy metadata.
Do not edit it by hand.

- Total debt items: **9**
- External records: **7**
- Legacy packages: **2**
- Structured evidence: **9**
- Unstructured debt: **0**
- Actionable: **3**
- Terminal: **6**
- Age reference date: **2026-10-07**

## Blocker categories

- `dataset-vs-repository-licence-scope`: **2**
- `exact-snapshot-identity`: **1**
- `historical-export-route`: **1**
- `redistribution-rights`: **5**

## Queue

| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| external | `dgs-infoclique-mortality` | terminal | DGS publicly disseminates SICO mortality information, but its current legal notice protects site contents and no dataset-specific redistribution grant covering the historical InfoClique/SICO CSV exports was recovered. | 2026-10-05 | 2 | 2 | unresolved | Reopen only if DGS publishes dataset-specific reuse terms or an authoritative open-data licence covering the historical mortality exports. |
| external | `ibm-telco-customer-churn` | terminal | The pinned IBM repository is Apache-2.0 licensed as a code pattern, but the README explicitly separates third-party objects and no dataset-specific redistribution licence for Telco-Customer-Churn.csv was established. | 2026-10-05 | 2 | 3 | unresolved | Reopen only if IBM publishes dataset-specific terms or an authoritative licence statement covering Telco-Customer-Churn.csv. |
| external | `maize-bipolaris-disease-progress` | terminal | The pinned repository has a root MIT licence and explicitly includes maize_bipolaris.csv as data, but the licence text covers software and associated documentation and no authoritative statement was recovered that explicitly applies MIT redistribution rights to the dataset bytes. | 2026-10-05 | 2 | 3 | unresolved | Reopen only if the author or another authoritative source explicitly states that the MIT licence covers maize_bipolaris.csv, or publishes separate dataset reuse terms. |
| external | `medium-crawlfeeds-corpus` | actionable | Dataset-specific reuse and redistribution permissions, source snapshot identity, and collection provenance have not been independently established. | 2026-10-07 | 0 | 2 | unresolved | Verify exact dataset files, applicable licenses, collection permission, sample selection, timestamps, and outcome fields before any canonical promotion. |
| external | `medium-fabiochiu-articles` | actionable | Dataset-specific reuse and redistribution permissions, source snapshot identity, and collection provenance have not been independently established. | 2026-10-07 | 0 | 2 | unresolved | Verify exact dataset files, applicable licenses, collection permission, sample selection, timestamps, and outcome fields before any canonical promotion. |
| external | `medium-jansma-historical` | actionable | Dataset-specific reuse and redistribution permissions, source snapshot identity, and collection provenance have not been independently established. | 2026-10-07 | 0 | 2 | unresolved | Verify exact dataset files, applicable licenses, collection permission, sample selection, timestamps, and outcome fields before any canonical promotion. |
| external | `pordata-portugal-resident-population` | terminal | INE permits rediffusion of official statistical information with source attribution, but the historical workbook was a PORDATA-generated Excel export and no authoritative term was recovered that clearly permits mirroring that secondary-source artifact. | 2026-10-05 | 2 | 3 | unresolved | Reopen only if PORDATA or FFMS publishes terms explicitly authorizing redistribution of exported table files, or if the registry replaces the artifact with a directly sourced INE representation under INE reuse terms. |
| legacy | `country-age-sex-2019` | terminal | The retained age/sex files are strongly attributable to UN World Population Prospects 2019, whose publications are CC BY 3.0 IGO, but the exact download/export route and the lineage of the Portugal CSV/XLSX variants cannot be reconstructed sufficiently to claim file-level provenance for these historical artifacts. | 2026-10-05 | 2 | 2 | unknown | Reopen only if the original authoritative UN export identity can be tied to the retained files and the Portugal workbook/CSV lineage can be resolved. |
| legacy | `portugal-covid19` | terminal | The retained workbook is attributable to the GEP/MTSSS Indicadores COVID-19 monitoring series and dated 27 May 2020, but the exact historical workbook URL, immutable upstream identity and dataset-specific redistribution terms were not recovered. | 2026-10-05 | 2 | 2 | unknown | Reopen only if GEP/MTSSS exposes the exact 27 May 2020 workbook with stable identity and explicit redistribution terms. |

## Age semantics

Age is deterministic and content-based. When structured review dates exist,
the reference date is the latest `last_reviewed` date present in the queue.
Items without structured review dates have no age value.

Unstructured debt remains visible so introducing the queue does not hide
records that have not yet been migrated to the structured resolution model.

