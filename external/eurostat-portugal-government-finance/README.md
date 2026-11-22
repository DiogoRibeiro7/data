# Eurostat Portugal general government finance, GDP and bond yields

Eurostat publishes, through its [statistics API](https://ec.europa.eu/eurostat/data/database), the excessive deficit procedure (EDP) series for Portuguese general government (debt, net lending, interest payable), national-accounts GDP, and the long-term interest rate used for the Maastricht convergence criterion.

## Consumer contract

`Medium-Blog/portugal-debt-2035-probability` downloads four JSON-stat responses and checks each against the SHA-256 in `metadata.yaml`:

| Path | Code | Dataset DOI | Content |
| --- | --- | --- | --- |
| `raw/edp_pc.json` | `gov_10dd_edpt1` | [10.2908/GOV_10DD_EDPT1](https://doi.org/10.2908/GOV_10DD_EDPT1) | GD, B9, D41PAY for S13, % of GDP |
| `raw/edp_mio.json` | `gov_10dd_edpt1` | same | GD, B9, D41PAY for S13, EUR million |
| `raw/gdp.json` | `nama_10_gdp` | [10.2908/NAMA_10_GDP](https://doi.org/10.2908/NAMA_10_GDP) | B1GQ: CLV_PCH_PRE, PD_PCH_PRE_EUR, CP_MEUR |
| `raw/yld.json` | `irt_lt_mcby_a` | [10.2908/IRT_LT_MCBY_A](https://doi.org/10.2908/IRT_LT_MCBY_A) | 10-year convergence-criterion yield, annual |

All four were retrieved on 22 November 2026. Eurostat's `updated` stamps: 21 October 2026 for the EDP series (autumn notification), 11 November 2026 for GDP, 25 February 2026 for yields. The consumer rebuilds an annual panel for 1995–2025 from them at each run.

## Revisions

The API serves only the latest vintage, and the EDP and national-accounts series are revised at every April and October notification. A hash mismatch therefore means a newer vintage. In that case the consumer prints the new hashes and stops, unless it is run with `--accept-revision`. To move the pin, record the new hashes and `provider_updated` stamps here and in the consumer's `data_sources/` contract.

The `social-security-housing-investment` consumer recorded in `eurostat-portugal-housing-indicators` snapshots `irt_lt_mcby_a` independently. That retrieval is not claimed to be the same response as this one.

## Reuse and registry decision

Eurostat's [copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice) allows reuse of its statistical data with source acknowledgement under Commission Decision 2011/833/EU. Attribution should name Eurostat, the dataset code or DOI, the access date and any transformation.

**Metadata-only external record.** Eurostat remains the byte source. No responses are mirrored here or in Medium-Blog.
