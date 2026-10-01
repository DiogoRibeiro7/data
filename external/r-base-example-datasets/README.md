# R base example datasets

Authoritative source record for the built-in R `datasets` package examples that were formerly stored under `legacy/r-example-datasets/`.

The removed legacy files were:

- `InsectSprays.csv` — the built-in `InsectSprays` dataset;
- `PlantGrowth.csv` — the built-in `PlantGrowth` dataset.

## Authoritative sources

- R `datasets` package documentation: https://search.r-project.org/R/refmans/datasets/html/00Index.html
- `InsectSprays`: https://search.r-project.org/R/refmans/datasets/html/InsectSprays.html
- `PlantGrowth`: https://search.r-project.org/R/refmans/datasets/html/PlantGrowth.html
- R licensing: https://www.r-project.org/Licenses/

R is distributed under `GPL-2 | GPL-3`. The two datasets are shipped with the base `datasets` package and can be loaded directly in R; separate CSV copies are unnecessary.

The historical CSVs in this repository used an R `write.csv`-style serialization with quoted fields and row names. They are semantically the same built-in datasets, but not byte-identical to the current Rdatasets CSV mirror.

No current consumer of the legacy CSV filenames was found, so the duplicate serialized copies were removed.
