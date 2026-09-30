# Portugal COVID-19 legacy data

> **Resolution:** retained in legacy quarantine because the package has mixed lineage.

## Evidence recovered

`Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx` belongs to the 2020 **Indicadores COVID-19 MTSSS** monitoring-workbook series published by the Portuguese Ministry of Labour, Solidarity and Social Security / GEP.

`Portugal_ARS.csv`, however, is a derived-looking regional estimate table with fields such as `ML`, `Low_90`, `High_90`, `Low_50`, and `High_50`. Its generating model and upstream inputs were not recovered.

## Concrete blockers

- exact historical MTSSS workbook URL/terms not pinned;
- `Portugal_ARS.csv` derivation and upstream inputs unknown;
- package-level redistribution terms unresolved.

The two files should not be promoted together as one canonical dataset.

See [the resolution audit](../../docs/migrations/LEGACY_RESOLUTION.md).
