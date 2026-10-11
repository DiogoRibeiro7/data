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
- Age reference date: **2026-10-11**

## Blocker categories

- `dataset-vs-repository-licence-scope`: **2**
- `exact-snapshot-identity`: **1**
- `historical-export-route`: **1**
- `redistribution-rights`: **5**

## Queue

| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| external | `dgs-infoclique-mortality` | terminal | DGS publicly disseminates SICO mortality information, but its current legal notice protects site contents and no dataset-specific redistribution grant covering the historical InfoClique/SICO CSV exports was recovered. | 2026-10-05 | 6 | 2 | unresolved | Reopen only if DGS publishes dataset-specific reuse terms or an authoritative open-data licence covering the historical mortality exports. |
| external | `ibm-telco-customer-churn` | terminal | The pinned IBM repository is Apache-2.0 licensed as a code pattern, but the README explicitly separates third-party objects and no dataset-specific redistribution licence for Telco-Customer-Churn.csv was established. | 2026-10-05 | 6 | 3 | unresolved | Reopen only if IBM publishes dataset-specific terms or an authoritative licence statement covering Telco-Customer-Churn.csv. |
| external | `maize-bipolaris-disease-progress` | terminal | The pinned repository has a root MIT licence and explicitly includes maize_bipolaris.csv as data, but the licence text covers software and associated documentation and no authoritative statement was recovered that explicitly applies MIT redistribution rights to the dataset bytes. | 2026-10-05 | 6 | 3 | unresolved | Reopen only if the author or another authoritative source explicitly states that the MIT licence covers maize_bipolaris.csv, or publishes separate dataset reuse terms. |
| external | `medium-crawlfeeds-corpus` | actionable | The Hugging Face source and current schema are established: the card labels the corpus CC BY-SA 3.0, describes a web-scraped Medium sample/subset, and exposes engagement, timestamp and full-text fields. The immutable dataset revision and authority to redistribute third-party article bodies remain unresolved. | 2026-10-11 | 0 | 2 | unresolved | In #196, verify the legal scope of the dataset-card CC BY-SA 3.0 declaration for scraped third-party article content and establish an immutable dataset revision/file identity before any promotion. |
| external | `medium-fabiochiu-articles` | actionable | The Hugging Face dataset is identifiable and declares MIT; the viewer exposes revision 979af3bcd84565e3f47b9eca752d8ec112824953 and files with heterogeneous text/no-text schemas. Whether the dataset licence authorizes redistribution of copied third-party Medium article text remains unresolved. | 2026-10-11 | 0 | 3 | unresolved | In #196, determine whether MIT applies validly to the exact dataset bytes, especially third-party article text, and whether a no-text subset has a safer redistribution profile. |
| external | `medium-jansma-historical` | actionable | The research repository and methodology are identifiable at commit c0cc836bcdfbd3bd1d986bb967978d92ee43dac9. The README documents roughly 1.4 million stories across 95 popular subjects and points to a Kaggle dataset, but the actual dataset object is off-repository and no repository LICENSE establishes dataset redistribution rights. | 2026-10-11 | 0 | 3 | unresolved | In #196, identify the exact Kaggle dataset/version and authoritative licence/redistribution terms for those bytes; absent such evidence, classify the record terminal external-only. |
| external | `pordata-portugal-resident-population` | terminal | INE permits rediffusion of official statistical information with source attribution, but the historical workbook was a PORDATA-generated Excel export and no authoritative term was recovered that clearly permits mirroring that secondary-source artifact. | 2026-10-05 | 6 | 3 | unresolved | Reopen only if PORDATA or FFMS publishes terms explicitly authorizing redistribution of exported table files, or if the registry replaces the artifact with a directly sourced INE representation under INE reuse terms. |
| legacy | `country-age-sex-2019` | terminal | The retained age/sex files are strongly attributable to UN World Population Prospects 2019, whose publications are CC BY 3.0 IGO, but the exact download/export route and the lineage of the Portugal CSV/XLSX variants cannot be reconstructed sufficiently to claim file-level provenance for these historical artifacts. | 2026-10-05 | 6 | 2 | unknown | Reopen only if the original authoritative UN export identity can be tied to the retained files and the Portugal workbook/CSV lineage can be resolved. |
| legacy | `portugal-covid19` | terminal | The retained workbook is attributable to the GEP/MTSSS Indicadores COVID-19 monitoring series and dated 27 May 2020, but the exact historical workbook URL, immutable upstream identity and dataset-specific redistribution terms were not recovered. | 2026-10-05 | 6 | 2 | unknown | Reopen only if GEP/MTSSS exposes the exact 27 May 2020 workbook with stable identity and explicit redistribution terms. |

## Age semantics

Age is deterministic and content-based. When structured review dates exist,
the reference date is the latest `last_reviewed` date present in the queue.
Items without structured review dates have no age value.

Unstructured debt remains visible so introducing the queue does not hide
records that have not yet been migrated to the structured resolution model.
