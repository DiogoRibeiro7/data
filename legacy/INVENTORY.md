# Legacy quarantine inventory

## Current state

Resolution audit date: **2026-10-03**

- Initial root data files inventoried: **37**
- Initial unique Git blobs: **36**
- Initial legacy packages: **9**
- Legacy packages remaining after resolution: **4**
- Packages replaced by external source records: **3**
- Obsolete project-input packages removed: **2**
- Canonical datasets promoted by this audit: **0**

## Package resolution

| Package | Status | Resolution / blocker |
| --- | --- | --- |
| `country-age-sex-2019` | retained | Re-audit strongly identifies UN WPP 2019 as the source family; exact historical download/export route and Portugal workbook/CSV lineage remain unresolved. |
| `covid19-modeling` | removed | Mixed Kaggle/OWID/manual project inputs; no consumers; no coherent reusable dataset identity. |
| `italy-covid19` | removed | Re-audit identified a hand-assembled research helper table authored by Marco Ferrante from public Italian Government/AIFA sources; no consumers; not a reusable authoritative dataset. |
| `jhu-covid19-time-series` | externalized | Five files traced by Git blob identity to JHU commit `dd07d05ff02d8aea12cab868e8a36c0e31cadf66`; replaced by `external/jhu-csse-covid19/`. |
| `portugal-covid19` | retained | Re-audit narrows package to the 27 May 2020 GEP/MTSSS monitoring workbook; orphaned `Portugal_ARS.csv` model output removed; exact historical workbook URL and redistribution terms remain unresolved. |
| `portugal-population-2018` | retained | Exact publisher/export route and terms unresolved. |
| `portugal-sico-mortality` | retained | DGS/SICO source family identified; exact export route and redistribution terms unresolved. |
| `r-example-datasets` | externalized | Built-in R datasets; redundant CSV serializations removed; replaced by `external/r-base-example-datasets/`. |
| `telco-customer-churn` | externalized | IBM sample identified; normalized contents match IBM archived CSV; replaced by `external/ibm-telco-customer-churn/`. |

No current consumer of the distinctive removed legacy filenames was found outside this repository.

See [the full resolution audit](../docs/migrations/LEGACY_RESOLUTION.md).

## Historical root migration record

The table below is preserved as the original root-to-legacy migration record. Paths marked as moved may subsequently have been resolved by the package decisions above.

## Inventory

| Original root path | Group | Size | Git blob SHA | Status | New path / note |
| --- | --- | ---: | --- | --- | --- |
| `China-2019.csv` | country-age-sex-2019 | 512 | `98adad73ae93f73cbea8756585e21d3203c6999e` | moved | legacy/country-age-sex-2019/raw/China-2019.csv |
| `Dados_SICO_2020-05-31_2015.csv` | portugal-sico-mortality | 12542 | `655bc761d947a4c2eb17b8872bec0f2fe0adb327` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2015.csv |
| `Dados_SICO_2020-05-31_2016.csv` | portugal-sico-mortality | 12576 | `f9369884e7f653ad2d4dfcd8dfb2c49757bdf608` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2016.csv |
| `Dados_SICO_2020-05-31_2017.csv` | portugal-sico-mortality | 12542 | `48f107c194f74a232c2af457d365f2a3d224f848` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2017.csv |
| `Dados_SICO_2020-05-31_2018.csv` | portugal-sico-mortality | 12542 | `38cf14e5f557ee722d6a54058d35dc976146e5a1` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2018.csv |
| `Dados_SICO_2020-05-31_2019.csv` | portugal-sico-mortality | 12542 | `c589a69e26e9482644d4e00377c201518a918dc8` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2019.csv |
| `Dados_SICO_2020-05-31_2020.csv` | portugal-sico-mortality | 5640 | `ae96b27a51958c76e4978446558737377d387d5f` | moved | legacy/portugal-sico-mortality/raw/Dados_SICO_2020-05-31_2020.csv |
| `Dataset_Italy_COVID_19.xlsx` | italy-covid19 | 12339 | `43460f5601b3b0c4993526ed3c53bb25339fa3e8` | removed | derived research helper; no current consumer; source links point to Italian Government/AIFA pages |
| `Denmark-2019.csv` | country-age-sex-2019 | 430 | `2387fffb7300c76f236f42d75b137678152d1abe` | moved | legacy/country-age-sex-2019/raw/Denmark-2019.csv |
| `France-2019.csv` | country-age-sex-2019 | 473 | `25596c84036ffa63be16b0ed3b79c7a05cefe7d1` | moved | legacy/country-age-sex-2019/raw/France-2019.csv |
| `full_data_logistic.csv` | covid19-modeling | 2083 | `cb644f9d9e11257cb13668bb986ec041ee43a60e` | moved | legacy/covid19-modeling/raw/full_data_logistic.csv |
| `Germany-2019.csv` | country-age-sex-2019 | 475 | `08debabcf893ea878fe96d191f83e9598836ddd2` | moved | legacy/country-age-sex-2019/raw/Germany-2019.csv |
| `InsectSprays.csv` | r-example-datasets | 836 | `ea4aeb903a2e46280f8a2e34e99588d4efdcaffa` | moved | legacy/r-example-datasets/raw/InsectSprays.csv |
| `Italy-2019.csv` | country-age-sex-2019 | 474 | `5f850f4355e8a0a280a0317ec582f2913451c6b2` | moved | legacy/country-age-sex-2019/raw/Italy-2019.csv |
| `Japan-2019.csv` | country-age-sex-2019 | 479 | `9b3fb35f9fa99a5afae528b39013cd18da693f52` | moved | legacy/country-age-sex-2019/raw/Japan-2019.csv |
| `locations_population.csv` | covid19-modeling | 9979 | `58e47c2b7e3f68f623cdcb6fb68bb5b55a34093e` | moved | legacy/covid19-modeling/raw/locations_population.csv |
| `Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx` | portugal-covid19 | 91305 | `724f2a87714f883494231a838baecbb32adf5d4c` | moved | legacy/portugal-covid19/raw/Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx |
| `Netherlands-2019.csv` | country-age-sex-2019 | 434 | `5432e18b05c27aa320242e27af25c22854c1c066` | moved | legacy/country-age-sex-2019/raw/Netherlands-2019.csv |
| `PlantGrowth.csv` | r-example-datasets | 518 | `b01e3601e569bf7e1ccbabbb3957b873f6c0446e` | moved | legacy/r-example-datasets/raw/PlantGrowth.csv |
| `populacao_residente_2018.xlsx` | portugal-population-2018 | 16882 | `8997eb72cc474f6379f9e40cf4618feb130c8557` | moved | legacy/portugal-population-2018/raw/populacao_residente_2018.xlsx |
| `Portugal_ARS.csv` | portugal-covid19 | 24616 | `c3db9ebe0d9dcbc32098e12c313c27881c14a2be` | removed | orphaned statistical model output; no maintained consumer or generating code recovered |
| `Portugal-2019_1.csv` | country-age-sex-2019 | 434 | `1569acc9bd03c9e0c62d47ee82a951377a473edf` | moved | legacy/country-age-sex-2019/raw/Portugal-2019_1.csv |
| `Portugal-2019.csv` | country-age-sex-2019 | 231 | `fcf0ba9f7ba94f3fb7810ae2bd1bbceecc1b4ae5` | moved | legacy/country-age-sex-2019/raw/Portugal-2019.csv |
| `Portugal-2019.xlsx` | country-age-sex-2019 | 8599 | `c30b196cabd57e19700fc991d7e488e21b035d15` | moved | legacy/country-age-sex-2019/raw/Portugal-2019.xlsx |
| `Spain-2019.csv` | country-age-sex-2019 | 468 | `5e4cb2cac21bc3bb872df0df8f0479b5f802a7f4` | moved | legacy/country-age-sex-2019/raw/Spain-2019.csv |
| `Sweden-2019.csv` | country-age-sex-2019 | 433 | `530367dfc106bfd97a128e965f98863c0b30d895` | moved | legacy/country-age-sex-2019/raw/Sweden-2019.csv |
| `Switzerland-2019.csv` | country-age-sex-2019 | 432 | `d48b3b0be08dc807258daefcb5ee79c3f8cad5f5` | moved | legacy/country-age-sex-2019/raw/Switzerland-2019.csv |
| `telco_customer_churn.txt` | telco-customer-churn | 977501 | `883e5973eb88d03fe9db9e36109a82a2968683a1` | exact duplicate removed | removed; exact duplicate of retained Telco file |
| `Telco-Customer-Churn.txt` | telco-customer-churn | 977501 | `883e5973eb88d03fe9db9e36109a82a2968683a1` | moved | legacy/telco-customer-churn/raw/Telco-Customer-Churn.txt |
| `time_series_covid_19_confirmed_US.csv` | jhu-covid19-time-series | 1416653 | `7aa25298d035acf6073bbeb3631ebb38b73cea52` | moved | legacy/jhu-covid19-time-series/raw/time_series_covid_19_confirmed_US.csv |
| `time_series_covid_19_confirmed.csv` | jhu-covid19-time-series | 132170 | `8971d90ba64f6f879ef5667f65e4b8be7ab448e9` | moved | legacy/jhu-covid19-time-series/raw/time_series_covid_19_confirmed.csv |
| `time_series_covid_19_deaths_US.csv` | jhu-covid19-time-series | 1272958 | `ee5a796f1525d59f6de6741ca93970b93b9d80bd` | moved | legacy/jhu-covid19-time-series/raw/time_series_covid_19_deaths_US.csv |
| `time_series_covid_19_deaths.csv` | jhu-covid19-time-series | 97372 | `5b3a31095cd976836fe69c6026bf3e5e52f76e04` | moved | legacy/jhu-covid19-time-series/raw/time_series_covid_19_deaths.csv |
| `time_series_covid_19_recovered.csv` | jhu-covid19-time-series | 112796 | `f3f257135aba93b7c4759600c0e0ddfe3347d63c` | moved | legacy/jhu-covid19-time-series/raw/time_series_covid_19_recovered.csv |
| `train.csv` | covid19-modeling | 969831 | `95712d1fd4ac5e510e73a1f87ddf28d74263f409` | moved | legacy/covid19-modeling/raw/train.csv |
| `United Kingdom-2019.csv` | country-age-sex-2019 | 473 | `1916842372700377f63c3ec8a5b4e6afa80e798c` | moved | legacy/country-age-sex-2019/raw/United Kingdom-2019.csv |
| `United States of America-2019.csv` | country-age-sex-2019 | 503 | `5aa524e915103b12fb6b6c4171ec8e8bf61d0170` | moved | legacy/country-age-sex-2019/raw/United States of America-2019.csv |

## Integrity

Moved files reuse their existing Git blob SHA. No dataset bytes are transformed by this reorganization.

