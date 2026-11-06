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
| WID.world wealth shares | Top-1%, top-10% and bottom-50% net-wealth shares | Optional local bulk-ZIP loader; no pinned real archive evidenced | [WID external reference](../../external/world-inequality-database-wealth-shares/README.md); reuse unresolved |
| OECD analytical house prices | Price-to-income/rent ratios and housing indices | Live SDMX downloader; no pinned retrieved CSV evidenced | [OECD external reference](../../external/oecd-analytical-house-price-indicators/README.md); per-series rights audit pending |
| OECD annual wages | Real wage growth from a separate OECD SDMX dataflow | Downloader implemented; no pinned retrieved CSV evidenced | Future source-contract candidate; **not** included in the housing-price record |
| Eurostat `ilc_lvho07b`, `ilc_lvps15`, `gov_10a_taxag` | Housing stress, ownership by age, tax proxies | Public API downloaders; multi-country analysis | Existing [Portugal-specific Eurostat record](../../external/eurostat-portugal-housing-indicators/README.md) is not a blanket licence or snapshot for all countries and series |
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
   A source family name alone is insufficient to establish reproducibility.
4. **No synthetic promotion**: keep model simulations, placeholder panels,
   confidential household files and derived research outputs in their
   appropriate projects rather than the public data registry.

This PR records two existing source dependencies with explicit boundaries.
It does **not** claim to have downloaded WID's ZIP, verified its contents or
validated a full empirical wealth model.
