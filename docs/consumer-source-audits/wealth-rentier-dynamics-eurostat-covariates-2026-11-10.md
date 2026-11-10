# Supplemental consumer audit: Eurostat cross-country housing and tax series

Reviewed: **2026-11-10**. Consumer code inspected at
[`bf0e75b9`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/data_sources.py).
This is a source-definition and static parser audit, **not** a live API
extraction, country-year coverage check or verification of observed values.

## Three independent API contracts

All queries use `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{DATASET}`.
The analysis panel targets **PT, ES, FR, IT, IE and NL**, one response per
dataset/country. The consumer's defaults and normalizer outputs are:

| Dataset and DOI | Request filters | Consumer output | Statistical meaning / excluded interpretation |
| --- | --- | --- | --- |
| [`ilc_lvho07b`](https://doi.org/10.2908/ILC_LVHO07B) | `geo={GEO}`, `quantile=QU1`, `freq=A`, `unit=PC`; filters may be overridden | `rent_burden_bottom_quintile` | Share of people in the lowest income quintile whose *total housing costs*, net of allowances, exceed 40% of disposable household income, also net of allowances; not rent paid as a share of income. |
| [`ilc_lvps15`](https://doi.org/10.2908/ILC_LVPS15) | `geo={GEO}`, `tenure=OWN`, `sex=T`, `unit=PC`, `citizen=NAT`; age/time vary | `(year, age, home_ownership_rate)` | Ownership in the reporting-country-citizenship population aged 18+, by age; not owner-occupancy among *all residents*. `citizen` can be overridden. |
| [`gov_10a_taxag`](https://doi.org/10.2908/GOV_10A_TAXAG) | `geo={GEO}`, `unit=PC_GDP`, `sector=S13`; `na_item`/time vary | `capital_tax_rate_proxy` plus three tax/GDP fields | `D5`: current taxes on income and wealth; `D91`: capital taxes; `D59A`: current taxes on capital. Each value is government receipts **as % of GDP**, not an effective tax rate applied to a capital-income or wealth base. |

The official Eurostat [housing-cost indicator `tessi162`](https://doi.org/10.2908/TESSI162)
identifies `ilc_lvho07b` as its **source dataset**. Its separate indicator code
is useful definitional evidence, not a fourth download or a substitute for
the `ilc_lvho07b` raw-series identity. The official
[`ilc_lvps15` table](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvps15/default/table?lang=en)
defines the population as those aged 18 and over; its citizenship categories
and age groups must be retained when making comparisons. Eurostat's
[`gov_10a_taxag` table](https://ec.europa.eu/eurostat/databrowser/view/gov_10a_taxag/default/table?lang=en)
identifies the accounts framework. `D59A` maps to the Eurostat item *current
taxes on capital* even though the consumer calls it `property_taxes_pct_gdp`.

## Verified parser risks (no observed data inferred)

1. **Housing overburden (`normalize_eurostat_housing_overburden`)**:
   The decoder checks for multiple non-time slices and filters an available
   geography dimension. It does **not** validate that a *single* returned
   slice has the intended `quantile=QU1`, `unit=PC`, and `freq=A` values. A
   one-slice payload for another category could be accepted and mislabeled.
   Missing value/status flags are not retained in the output.
2. **Ownership (`normalize_eurostat_ownership_by_age`)**:
   The generic JSON-stat decoder exposes dimension codes, but the normalizer
   discards `geo`, `citizen`, `tenure`, `sex`, `unit` and frequency without
   checking them. A payload containing unexpected categories can yield
   repeated `(country, year, age)` keys or an apparently valid but incorrect
   series. Overlapping age bands must not be treated as disjoint weights.
3. **Taxes (`normalize_eurostat_capital_taxes`)**:
   The decoder does not verify `geo`, `unit=PC_GDP`, `sector=S13` or frequency.
   Its `pivot_table(index="year", columns="na_item", values="value",
   aggfunc="first")` silently takes one candidate if distinct dimensional
   slices share the same year/item. The result assigns `D5` to
   `capital_tax_rate_proxy`, a research proxy label rather than an observed
   capital-tax rate. The `D59A` output alias is similarly narrower than the
   official tax-item definition.
4. **Provenance and quality**: The generic JSON-stat decoder extracts cell
   values but does not carry upstream observation `status` flags into
   normalized files. The final country-year/age tables contain neither raw
   request identity nor raw checksum. None of the responses is currently
   pinned in this registry.

These findings are verified from the *code paths*, not from live returned
Eurostat cells. In particular, no claim is made that duplicates, missing
years, non-default dimensions or unreliable flags occur in any specific
country response.

## Downstream acceptance criteria

1. Reject non-matching returned dimension codes, including `geo`, `freq`,
   `unit`, `quantile`/`citizen`/`tenure`/`sex`/`sector` as applicable. Select
   the intended measure *before* discarding dimension columns; do not assume
   a valid HTTP response is uniquely identified by query parameters.
2. Validate uniqueness at the appropriate grain: `(country, year)` for QU1
   housing overburden and selected tax items, and `(country, year, age)` for
   ownership; reject conflicting duplicate observations, never pick a first
   value silently. Track absent `D5` or age bands separately from zero.
3. Propagate original Eurostat `status` and missing-cell information, record
   source update/structure timestamps, and distinguish unavailable, provisional
   and low-reliability observations under an explicit analysis policy.
4. Use offline JSON-stat fixtures for wrong-but-single categories, two
   citizenship/tenure/sector slices, duplicate tax candidates, sparse values,
   an incorrect geography, non-annual frequency, flagged observations and
   legitimate one-series results. Regression tests must assert exact columns,
   labels, uniqueness and missing-value behavior.
5. Save *separate* request manifests for each dataset/geography: complete URL
   and filter map, DOI, UTC fetch time, Eurostat `updated`/structure dates if
   present, raw response byte length and SHA-256, returned dimension codes,
   flags, coverage and pinned consumer transformation revision. Since Eurostat
   [serves current rather than archived API versions](https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-introduction),
   identical URLs do not imply identical observation vintages.
6. Retain Eurostat attribution and modification notices in any publication,
   subject to its [reuse-policy exceptions](https://ec.europa.eu/eurostat/help/copyright-notice).

## Registry disposition

Keep the grouped Eurostat record **metadata-only** and the provenance blocker
**actionable** until the consumer supplies the above tests and dated, hashed
per-product exports. This audit does not insert raw responses, infer observed
housing stress or capital taxation, or approve a canonical data release.
