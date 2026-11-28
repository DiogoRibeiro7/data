# Eurostat government spending and GDP: independent candidate review

Reviewed on 28 November 2026; acquisition run [46149016389](https://github.com/DiogoRibeiro7/data/actions/runs/46149016389), artifact 15263844907. ZIP SHA-256 `f22e9143755113213826bfc941e022c93f5e17f1da328002332704c585cfff06` matched GitHub's artifact digest. Manifest SHA-256 `464eabbea0850dfa7d0114901286181fb64f94631cc6bb526b74725915979842`. Three original responses (139,986 bytes total) match every audited size and SHA-256. Only these exact bytes may be promoted.

| Source file | Requested | Non-null | Missing | Flags |
| --- | ---: | ---: | ---: | ---: |
| fiscal.json | 9,207 | 9,203 | 4 | 47 |
| growth.json | 837 | 809 | 28 | 20 |
| nominal_gdp.json | 837 | 837 | 0 | 20 |
| Total | 10,881 | 10,849 | 32 | 87 |

All 27 countries and 31 years are present in each response's dimension grid. Fiscal B9 and TR each have two missing values; nine other fiscal series are complete. GDP growth has 28 missing values; nominal GDP is complete. Across the three files, 58 observations are provisional (p) and 29 have a break in time series (b), including any flags attached to missing values. No imputation. TE and B1G complete for all 837 country-years.

Dataset codes and dimensions checked: gov_10a_main annual S13 PC_GDP, eleven requested ESA items; nama_10_gdp annual B1GQ with CLV_PCH_PRE or CP_MEUR. The source publisher is ESTAT in all three raw responses; SOURCE_INSTITUTIONS annotations name Eurostat. Fiscal update 2026-10-21; GDP update 2026-11-27. France 2025 TE 57.3%, B1G 16.6%, final consumption 24.1%, cash/other non-in-kind benefits 19.4%, purchased transfers in kind 6.4%. This later vintage differs from the March 2026 INSEE headline of 57.2%; do not present them as the same vintage. Nominal GDP and growth for France 2025 are provisional. GDP ratios may reflect slightly different GDP vintages; reconstructed nominal expenditure is approximate, not a separately observed nominal fiscal series.

General-government GVA is not all public ownership; the residual includes other institutional sectors and taxes less subsidies on products. Fiscal items may overlap and must not be added as mutually exclusive categories. Derived associations cannot identify causal effects.

## Reuse review

[Eurostat's statistical data reuse policy](https://ec.europa.eu/eurostat/help/copyright-notice), checked 2026-11-28, authorises commercial and non-commercial redistribution with source acknowledgement subject to listed exceptions and dataset-specific notices. All observations here refer to EU member states; source annotations name Eurostat, and no third-party restriction is identified in the responses. Use the actual statistical-data reuse terms, not an assumed CC BY licence for the dataset. Cite the customised data codes and access date, mark changes, and include a non-responsibility disclaimer for derived outputs. This is not a warranty concerning rights in independently sourced third-party material.

## Promotion

The preparation workflow downloads the exact run/artifact, verifies the reviewed manifest and each source file, stages canonical data, regenerates registry reports, validates all tests and pushes a separate registration branch. It does not write to main, merge anything, or fetch a newer vintage. The temporary adoption exemption is removed after the downstream consumer pins this registry revision.
