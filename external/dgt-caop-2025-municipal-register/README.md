# DGT CAOP2025 municipal area and code register

The [Direção-Geral do Território (DGT)](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop)
publishes Portugal's official administrative map, the *Carta Administrativa
Oficial de Portugal* (CAOP). The **2025 version** was approved on
28 January 2026 and published by notice in February 2026.

The `empirical-analysis-r` housing study uses the [official CAOP2025
associated-areas ZIP](https://www.dgterritorio.gov.pt/sites/default/files/ficheiros-cartografia/Areas_Freg_Mun_Dist_Pais_CAOP2025.zip)
to validate all 308 municipality codes and labels against INE statistics.

- Outer source ZIP SHA-256:
  `350ab1362f4385f3f2177d6f8eed9003d59b604f4fffb81171b4a5c2c97847d7`.
- Exact extracted `Areas_Municipio_CAOP2025.csv` SHA-256:
  `aa3805d5a87c6def3d1d2f2a564ee3a44f82300411d6793086badc1f0f5d38f6`.
- Extraction path: nested `Areas_Freg_Mun_Dist_Pais_CAOP2025_csv.zip`.
- Coverage: **308** unique four-character `dtmn` municipality codes.

The downstream project documents four explicit name differences between
the DGT register and INE's NUTS 2024 municipality labels. It rejects
unreviewed fuzzy matches. CAOP2025 provides a current code reference;
using it does not imply municipal boundaries have remained unchanged
throughout historical price, construction or population series.

DGT's [open-data policy](https://www.dgterritorio.gov.pt/dados-abertos)
specifies **CC BY 4.0** reuse for the DGT-owned geographic data, requiring
publisher attribution. The source ZIP and exact project-local CSV are
discoverable through this record but **not duplicated** in the registry;
canonical promotion would require a registered, pinned downstream consumer
contract.
