# Rosés-Wolf database on regional GDP, version 7 (2025)

Regional GDP (1990 and 2011 international dollars), population, area and the shares of agriculture, industry and mining, and services in total employment for 173 European regions in 16 countries: NUTS-2 units of 2010, a few merged, and NUTS-1 units for the United Kingdom. Benchmark years 1900, 1910, 1925, 1938, 1950, 1960, 1970, 1980, 1990, 2000, 2010 and 2015, with population and GDP annually to 2022 and employment shares for 2021. Documented in Joan R. Rosés and Nikolaus Wolf (eds), *The Economic Development of Europe's Regions: A Quantitative History since 1900*, Routledge, 2018. Citation requested by the authors: Rosés-Wolf database on regional GDP, version 7 (2025).

## Consumer contract

`Medium-Blog/europe-industrial-regions` reads two files that a user downloads by hand from the CEPR data-set page and places in the folder's `data/raw/`:

- `RosesWolf_RegionalGDP_v7.xlsx` (258,083 bytes), from https://cepr.org/system/files/2025-10/RosesWolf_RegionalGDP_v7.xlsx;
- `RosesWolf_RegionalGDP_shapefile.zip` (2,506,562 bytes), from https://cepr.org/system/files/2022-11/RosesWolf_RegionalGDP_shapefile.zip. Its 275 polygons carry `NUTS_CODE`; AT123, DE712 and DE912 are the merged workbook regions AT12+AT13, DE71+DE72 and DE91+DE92.

The consumer checks both files against the SHA-256 in `metadata.yaml` before use.

## Why the bytes are not stored

No licence is stated, and the host refuses automated downloads; see the `resolution` block.
