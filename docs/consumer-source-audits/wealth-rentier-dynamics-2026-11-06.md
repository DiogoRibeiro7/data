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
| WID.world wealth shares | Top-1%, top-10% and bottom-50% net-wealth shares | Optional local bulk-ZIP loader; first-value pivot and country/coverage checks outstanding; no pinned real archive evidenced | [WID external reference](https://github.com/DiogoRibeiro7/data/tree/main/external/world-inequality-database-wealth-shares) and [2026-11-12 source audit](wealth-rentier-dynamics-wid-2026-11-12.md); reuse unresolved |
| OECD analytical house prices | Price-to-income/rent indices and house/rent price indices | Annual SDMX downloader; unrestricted unit/measure dimensions and first-value pivot need checking; no pinned retrieved CSV | [OECD external reference](https://github.com/DiogoRibeiro7/data/tree/main/external/oecd-analytical-house-price-indicators) and [2026-11-09 source-contract audit](wealth-rentier-dynamics-oecd-housing-2026-11-09.md); ownership and retrieval pending |
| OECD annual wages | Real average-wage growth from a separate OECD SDMX dataflow | Downloader implemented; silently deduplicates years and can mistake a multi-year gap for year-on-year growth; no pinned retrieved CSV | [OECD annual-wages contract](https://github.com/DiogoRibeiro7/data/tree/main/external/oecd-average-annual-wages) and [2026-11-09 source audit](wealth-rentier-dynamics-oecd-wages-2026-11-09.md); ownership and retrieval pending |
| Eurostat `ilc_lvho07b`, `ilc_lvps15`, `gov_10a_taxag` | Housing stress, ownership by citizenship/age, tax proxies | Public API downloaders; unvalidated returned non-time slices in two normalizers; no pinned responses | [Cross-country Eurostat source contract](https://github.com/DiogoRibeiro7/data/tree/main/external/eurostat-multicountry-housing-tax-covariates) and [2026-11-10 parser audit](wealth-rentier-dynamics-eurostat-covariates-2026-11-10.md). The [Portugal-only record](https://github.com/DiogoRibeiro7/data/tree/main/external/eurostat-portugal-housing-indicators) covers different responses |
| ECB DWA | Quarterly experimental distributional wealth and liabilities | Broad downloader exists but does not handle quarterly periods and official SDMX series keys | [ECB DWA external source](https://github.com/DiogoRibeiro7/data/tree/main/external/ecb-distributional-wealth-accounts) and [2026-11-07 compatibility audit](wealth-rentier-dynamics-ecb-dwa-2026-11-07.md); extraction blocked, no response pinned |
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
   The [2026-11-12 audit](wealth-rentier-dynamics-wid-2026-11-12.md) further
   requires country and percentile checks, rejection of conflicting duplicate
   observations, explicit outcome coverage and fraction-scale preservation.
   Source redistribution remains a **terminal** blocker for the public
   registry, independent of consumer-local validation.
2. **OECD source rights**: inspect the OECD Data Explorer source metadata
   for each selected country and measure. Its
   [general data terms](https://www.oecd.org/en/about/terms-conditions.html)
   allow broad reuse but expressly defer to source-specific and third-party
   restrictions. The [2026-11-09 audit](wealth-rentier-dynamics-oecd-housing-2026-11-09.md)
   also identifies an open unit/measure selector and first-value pivot in the
   consumer, which must be constrained and tested before using annual data.
   Only then consider canonical mirroring of a dated, hashed export.
3. **Remaining covariates**: audit Eurostat and ECB series separately by
   dataflow, geography, units, request and observation vintage. The OECD wage
   [2026-11-09 audit](wealth-rentier-dynamics-oecd-wages-2026-11-09.md)
   identifies the missing-year growth calculation and first-row deduplication
   risks. The [Eurostat audit](wealth-rentier-dynamics-eurostat-covariates-2026-11-10.md)
   records unchecked ownership dimensions, the tax first-value pivot and
   missing observation-status preservation; all three products lack pinned
   responses. The
   [2026-11-07 ECB DWA audit](wealth-rentier-dynamics-ecb-dwa-2026-11-07.md)
   now identifies the quarterly-period and series-key incompatibility that
   must be corrected in the consumer before a real extraction. A source
   family name alone is insufficient to establish reproducibility.
4. **No synthetic promotion**: keep model simulations, placeholder panels,
   confidential household files and derived research outputs in their
   appropriate projects rather than the public data registry.

## Interpretation controls

WID `shwealj992` is a net-personal-wealth **share among equal-split adults**,
expressed as a fraction of one (`0.25` means 25%). It is not an absolute
wealth stock or a series of percentage-valued observations. The
[WID consumer audit](wealth-rentier-dynamics-wid-2026-11-12.md) records the
first-value pivot, missing-outcome and geography-check risks, plus the
consumer-local extraction evidence needed before empirical use. This does
not change WID's unresolved full-archive redistribution status.

The official [OECD wage indicator](https://www.oecd.org/en/data/indicators/average-annual-wages.html)
is a *mean* wage per full-time-equivalent employee, not a median or a measure
of income inequality. It is currently expressed in constant 2025 US dollars
at purchasing-power parity, which can be rebased in future releases.
The consumer must calculate year-on-year wage growth only across consecutive
calendar years; `pct_change()` after removing missing years does not enforce
that requirement. The [OECD wage audit](wealth-rentier-dynamics-oecd-wages-2026-11-09.md)
records the downstream tests needed before empirical acquisition.

The OECD price-to-income and price-to-rent covariates are **2015-base indices**,
not percentages of housing expenditure relative to household income. Annual
analytical observations are averages of the year, not necessarily year-end
measurements. The [OECD housing audit](wealth-rentier-dynamics-oecd-housing-2026-11-09.md)
records the remaining unit and source-ownership checks.

Eurostat's housing-cost overburden by income quintile is a **40% threshold
indicator for total housing costs**, not a rent-to-income ratio. The consumer's
default `ilc_lvps15` filter `citizen=NAT` selects **nationals**, not all
residents. Its `gov_10a_taxag` `D5` tax/GDP ratio includes taxes on income
and wealth and **must not be described as an observed capital-tax rate**.
These interpretation limits are part of the source contract, independent of
data acquisition status. `D59A` means **current taxes on capital**, despite a
downstream `property_taxes_pct_gdp` alias. The
[Eurostat supplemental audit](wealth-rentier-dynamics-eurostat-covariates-2026-11-10.md)
specifies source selection, unique-key and flagged-observation tests. The
Eurostat `tessi162` view cites `ilc_lvho07b` as its source dataset; it is not
an additional API product used by the consumer.

The ECB DWA provides quarterly top-5%, top-10% and bottom-50% net-wealth
shares. The published [DWA overview](https://data.ecb.europa.eu/sites/default/files/2024-01/DWA%20Overview%20note_0.pdf)
does not substantiate the top-1% wealth-share outcome expected by the model.
Do not silently replace that outcome with a different percentile. The
[supplemental review](wealth-rentier-dynamics-ecb-dwa-2026-11-07.md)
documents the incompatible downloader and outstanding acquisition gates.

This audit now tracks five official source contracts (ECB DWA, two OECD,
one WID, and the grouped Eurostat request family) with explicit boundaries.
It does **not** claim to have downloaded, checksum-verified or redistributed
new upstream data, or validated a full empirical wealth model.
