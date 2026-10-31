# Metro do Porto whole-network validations, 2022–2024

Metro do Porto's [Sustainability Report 2022–2024](https://www.metrodoporto.pt/metrodoporto/uploads/document/file/748/rs_2022_2024.pdf),
section 9.1 (report page 25), publishes rounded annual card-validations
across the **entire** metro network.

| Year | Published approximate network validations |
| --- | ---: |
| 2022 | 65.2 million |
| 2023 | 79.1 million |
| 2024 | 89.8 million |

The independent research consumer `porto-metro-demand-analysis` records a
small manual transcription named
`metro_porto_network_validations_2022_2024.csv`, whose SHA-256 is
`e271266604e742063d2aff89c4f3338b07f011507a609cff54398226e830a865`
at commit `b35a2337949b71db0ad4e1ecb995f4091986620e`.

These published one-decimal-million values differ in precision from the exact
integer network passengers in AMT's 2022–2024 statutory operator reports.
Network-wide card validations do not measure Line B station entries, unique
travellers, or an origin–destination matrix. Avoid combining differently
defined measures without an explicit reconciliation.

The PDF is publicly accessible, but the examined report does not establish
dataset-specific redistribution terms for a centrally mirrored CSV.
**External-only, terminal unresolved rights**. No report or transcribed data
bytes are stored here.
