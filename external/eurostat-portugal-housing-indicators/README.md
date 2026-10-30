# Eurostat Portugal housing, income, and household indicators

The [Eurostat database](https://ec.europa.eu/eurostat/data/database) publishes
statistical series used to study Portuguese house prices, income, tenure,
housing-cost burden, rents, household composition, and population structure.

## Source identities

The [`portugal-housing-generations` v1.0.0 research project](https://github.com/DiogoRibeiro7/portugal-housing-generations/tree/0407faed1f08209b3d7682e19fc57e7120e62879)
pins 18 JSON responses retrieved on 29 October 2026, plus retrieval records
where available. The exact list, API query parameters, access dates, provider
update timestamps and dataset DOIs are in its
[source inventory](https://github.com/DiogoRibeiro7/portugal-housing-generations/blob/0407faed1f08209b3d7682e19fc57e7120e62879/docs/data-sources.csv);
the [checksum manifest](https://github.com/DiogoRibeiro7/portugal-housing-generations/blob/0407faed1f08209b3d7682e19fc57e7120e62879/data/SHA256SUMS)
identifies the actual response files.

Examples of published Eurostat series:

| Code | Statistic | Dataset DOI |
| --- | --- | --- |
| `prc_hpi_a` | Annual house-price index | [10.2908/PRC_HPI_A](https://doi.org/10.2908/PRC_HPI_A) |
| `ilc_di03` | Mean and median income by age and sex | [10.2908/ILC_DI03](https://doi.org/10.2908/ILC_DI03) |
| `ilc_lvho07c` | Housing-cost overburden by tenure | [10.2908/ILC_LVHO07C](https://doi.org/10.2908/ILC_LVHO07C) |
| `prc_hicp_aind` | Annual HICP and rent-price index | [10.2908/PRC_HICP_AIND](https://doi.org/10.2908/PRC_HICP_AIND) |

These are different statistical products, not a single harmonized raw table.
Any reuse must preserve dataset codes, units, filters, geography, observation
periods, and provider update dates.

## Reuse and registry decision

Eurostat's [copyright and reuse notice](https://ec.europa.eu/eurostat/help/copyright-notice)
authorizes reuse of Eurostat statistical data and metadata for commercial and
non-commercial purposes with source acknowledgement, under Commission Decision
2011/833/EU. It specifies exceptions for third-party and certain non-EU data;
the named Portuguese statistical series are not part of those exceptions.

Attribution should identify **Eurostat**, the dataset code/DOI, access date,
and any changes or transformations. The Eurostat copyright policy is not being
relabelled as a blanket Creative Commons licence for all source material.

**Metadata-only external record.** The historical API responses remain in the
research project with checksums. No upstream commit or immutable provider
revision is claimed, and no dataset bytes are duplicated here.
