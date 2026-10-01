# External source provenance and licensing audit

Audit date: **2026-10-01**

This audit checks every record under `external/` against the most authoritative upstream metadata available at review time.

The audit distinguishes:

- the licence of a repository's **code** from the licence/terms of its **data**;
- provider-wide default terms from dataset-specific terms;
- explicit redistribution permission from unresolved or restricted redistribution.

No permissive licence is inferred when dataset-specific terms are absent.

## Summary

| External record | Result | Evidence / decision |
| --- | --- | --- |
| `berkeley-earth-temperature` | verified unchanged | Berkeley Earth data page continues to state CC BY-NC 4.0 for the data products represented by this source record. |
| `fred-economic-data` | verified unchanged | FRED aggregates series from many providers; terms remain series-dependent and third-party restrictions can apply. Keeping licence unresolved at collection level is correct. |
| `ibm-telco-customer-churn` | verified unchanged | Pinned IBM commit exists. Repository code is Apache-2.0, but IBM's README states separately licensed third-party objects retain their own licences. Dataset-specific redistribution remains unresolved. |
| `jhu-csse-covid19` | **corrected** | Pinned 2020 JHU README restricts use to non-profit public-health, educational, and academic research; prohibits commercial use and redistribution of the aggregated dataset. Removed incorrect CC BY 4.0 / allowed-with-attribution claim. |
| `maize-bipolaris-disease-progress` | verified unchanged | Pinned upstream commit exists and the upstream repository carries an MIT licence. The repository explicitly presents `maize_bipolaris.csv` as raw study data. |
| `online-retail-ii` | verified unchanged | UCI Online Retail II record identifies DOI `10.24432/C5CG6D` and CC BY 4.0. |
| `our-world-in-data` | verified unchanged | OWID continues to distinguish its own material from third-party datasets; dataset-level terms remain provider-specific. Collection-level licence remains intentionally unresolved. |
| `r-base-example-datasets` | verified unchanged | R licensing page continues to describe the R distribution under GPL-2 | GPL-3; the source record points to the base `datasets` package rather than asserting an independent per-CSV licence. |
| `turing-change-point-dataset` | **corrected** | TCPD README states the repository **code** is MIT, while individual data files often have their own licences and some cannot be redistributed. Removed collection-level MIT claim and set redistribution to dataset-specific. |
| `ucdp-conflict-data` | verified unchanged | UCDP download guidance continues to use CC BY 4.0 for current datasets, with citation requirements. |
| `unhcr-refugee-statistics` | verified unchanged | UNHCR Refugee Population Statistics continues to state CC BY 4.0 unless otherwise indicated. |
| `world-bank-greenhouse-gas` | **corrected** | World Bank indicator metadata identifies the underlying source as Climate Watch Historical GHG Emissions (1990–2020), World Resources Institute, with CC BY-NC 4.0. Replaced the incorrect generic World Bank CC BY 4.0 assumption. |

## Corrected records

### JHU CSSE COVID-19

The previous registry record incorrectly represented the pinned historical snapshot as:

- licence: CC BY 4.0;
- redistribution: allowed with attribution.

The pinned source README at commit
`dd07d05ff02d8aea12cab868e8a36c0e31cadf66`
instead states restrictive historical terms, including:

- use limited to non-profit public-health, educational, and academic research;
- commercial use prohibited;
- redistribution of the website or aggregated dataset prohibited.

The external record now preserves those historical terms instead of projecting a later/general licence onto the 2020 snapshot.

### Turing Change Point Dataset

The previous record treated the repository's MIT software licence as the licence for the full dataset collection.

TCPD's own README explicitly states:

- code is MIT-licensed;
- individual data files often have their own licences;
- some time series cannot be redistributed because of licensing restrictions.

The registry now records:

- no collection-level data licence;
- redistribution: `dataset-specific`;
- attribution required;
- upstream repository as the source for per-series metadata/licensing.

### Climate Watch / World Bank WDI greenhouse-gas series

The previous record used:

- publisher: World Bank;
- generic World Bank CC BY 4.0 default.

Indicator-specific World Bank metadata for `EN.ATM.GHGT.KT.CE` identifies:

- source: **Climate Watch Historical GHG Emissions (1990–2020), World Resources Institute**;
- licence: **CC BY-NC 4.0**.

The registry now points to Climate Watch/WRI as the underlying publisher/source while retaining the WDI indicator identifier in the Medium-Blog provenance block.

## Verified pinned GitHub identities

The following pinned commits were checked and still exist:

- IBM Telco Customer Churn:
  `d5371f5d83a446ad5673cbcca3b814b926491f8a`
- JHU CSSE COVID-19:
  `dd07d05ff02d8aea12cab868e8a36c0e31cadf66`
- maize Bipolaris disease-progress:
  `d793d54c17ad404df2f6618d2681c993fcf144cf`

## Policy consequence

External records are discovery/provenance records, not licence grants.

For future audits:

1. prefer dataset-specific metadata over provider defaults;
2. distinguish repository software licences from data licences;
3. preserve historical terms for pinned historical snapshots;
4. leave licence/redistribution unresolved when authoritative evidence is insufficient;
5. do not silently mutate terms automatically—record changes through review.
