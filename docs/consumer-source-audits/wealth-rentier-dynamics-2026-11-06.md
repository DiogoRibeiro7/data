# Consumer source audit: wealth_rentier_dynamics

Reviewed: **2026-11-06**. Consumer revision:
[`f3e6e3a5`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/tree/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a).

This audit covers the current documented extractors and data contracts, **not**
an independently executed empirical extraction. The consumer's
[`data/README.md`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/data/README.md)
distinguishes live API covariates, local-file inputs and synthetic fixtures.

## Evidence-based dependency inventory

| Source | Consumer role | Acquisition state evidenced here | Registry disposition |
| --- | --- | --- | --- |
| WID.world wealth shares | Top-1%, top-10% and bottom-50% net-wealth shares | Optional local bulk-ZIP loader; no pinned real archive evidenced | [WID external reference](https://github.com/DiogoRibeiro7/data/tree/main/external/world-inequality-database-wealth-shares); reuse unresolved |
| OECD analytical house prices | Price-to-income/rent ratios and housing indices | Live SDMX downloader; no pinned retrieved CSV evidenced | [OECD external reference](https://github.com/DiogoRibeiro7/data/tree/main/external/oecd-analytical-house-price-indicators); per-series rights audit pending |
| OECD annual wages | Real average-wage growth from a separate OECD SDMX dataflow | Downloader implemented; no pinned retrieved CSV evidenced | [OECD annual-wages contract](https://github.com/DiogoRibeiro7/data/tree/main/external/oecd-average-annual-wages); reuse check and vintage pending |
| Eurostat `ilc_lvho07b`, `ilc_lvps15`, `gov_10a_taxag` | Housing stress, ownership by citizenship/age, tax proxies | Public API downloaders; multi-country analysis | [Cross-country Eurostat source contract](https://github.com/DiogoRibeiro7/data/tree/main/external/eurostat-multicountry-housing-tax-covariates); no snapshots. The [Portugal-only record](https://github.com/DiogoRibeiro7/data/tree/main/external/eurostat-portugal-housing-indicators) covers different responses |
| ECB DWA | Distributional wealth and liabilities | Downloader implemented; exact SDMX query and return coverage need validation | Separate candidate; no source bytes or frozen vintage recorded here |
| Banco de Portugal ISFF / HFCS | Household ownership transitions | Access-controlled microdata, explicitly local-file only | No central mirroring; access and confidentiality requirements govern use |
| Synthetic panels | Tests and offline model demonstrations | Present in project under `data/sample/` | Project-specific fixtures; do not enter canonical registry |

The top-1% WID wealth-share outcome is **absent from the assembled empirical
panel unless a user-supplied bulk ZIP is available**. An API covariate panel
or a synthetic fixture must not be advertised as an observed wealth-concentration
study when that outcome is missing.

## Next evidence gates

1. **WID acquisition**: in the consumer project, obtain an authorized dated
   bulk archive from [WID.world](https://wid.world/data/), compute its SHA-256,
   record the country members and extraction outcome, and keep the large ZIP
   out of Git. This is a consumer extraction task, not a central-registry
   redistribution authorization.
2. **OECD source rights**: inspect the OECD Data Explorer source metadata
   for each selected country and measure. Its
   [general data terms](https://www.oecd.org/en/about/terms-conditions.html)
   allow broad reuse but expressly defer to source-specific and third-party
   restrictions. Only then consider canonical mirroring of a dated, hashed
   export.
3. **Remaining covariates**: audit OECD wages and the Eurostat/ECB series
   separately by dataflow, geography, units, request and observation vintage.
   The wage and three Eurostat statistical-product contracts are now recorded;
   none yet has a pinned response. The ECB DWA query/coverage still requires
   an independent audit. A source family name alone is insufficient to
   establish reproducibility.
4. **No synthetic promotion**: keep model simulations, placeholder panels,
   confidential household files and derived research outputs in their
   appropriate projects rather than the public data registry.

## Interpretation controls

The official [OECD wage indicator](https://www.oecd.org/en/data/indicators/average-annual-wages.html)
is a *mean* wage per full-time-equivalent employee, not a median or a measure
of income inequality. It is currently expressed in constant 2025 US dollars
at purchasing-power parity, which can be rebased in future releases.

Eurostat's housing-cost overburden by income quintile is a **40% threshold
indicator for total housing costs**, not a rent-to-income ratio. The consumer's
default `ilc_lvps15` filter `citizen=NAT` selects **nationals**, not all
residents. Its `gov_10a_taxag` `D5` tax/GDP ratio includes taxes on income
and wealth and **must not be described as an observed capital-tax rate**.
These interpretation limits are part of the source contract, independent of
data acquisition status.

This audit now records four official source contracts (two OECD and one WID
source, plus the grouped Eurostat request family) with explicit boundaries.
It does **not** claim to have downloaded, checksum-verified or redistributed
new upstream data, or validated a full empirical wealth model.
