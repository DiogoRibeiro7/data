# Eurostat cross-country housing and tax covariates

The [`wealth_rentier_dynamics` data-source module](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/data_sources.py)
requests three **separate** Eurostat statistical products through the
JSON-stat API. They supply covariates for a cross-country wealth model; they
are not equivalent to the Portugal-only datasets registered in
[the earlier housing source record](https://github.com/DiogoRibeiro7/data/tree/main/external/eurostat-portugal-housing-indicators).

| Eurostat dataset | What the downloader requests | What it actually measures |
| --- | --- | --- |
| [`ilc_lvho07b`](https://doi.org/10.2908/ILC_LVHO07B) | `geo={GEO}&quantile=QU1&freq=A&unit=PC` by default | Percentage of the lowest-income-quintile population in households whose total housing costs exceed 40% of disposable income, net of housing allowances. This includes housing costs beyond rent. |
| [`ilc_lvps15`](https://doi.org/10.2908/ILC_LVPS15) | `geo={GEO}&tenure=OWN&sex=T&unit=PC&citizen=NAT` by default, with age/time varying | Owner-occupied housing **among nationals**, broken down by age; it is not the ownership rate for all residents. Eurostat labels this as distribution by citizenship and tenure for people aged 18 and over. |
| [`gov_10a_taxag`](https://doi.org/10.2908/GOV_10A_TAXAG) | `geo={GEO}&unit=PC_GDP&sector=S13`, with tax item/time varying | General-government receipts as a percentage of GDP; `D5` = current taxes on income and wealth, `D91` = capital taxes, and `D59A` = current taxes on capital. `D5` is **not an effective tax rate on capital**. |

Each request has the form:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{DATASET}?{FILTERS}
```

The consumer's country-year panel uses **PT, ES, FR, IT, IE and NL**. Its
`fetch_eurostat_housing_overburden` can accept custom filters; the table
documents its defaults. Its `fetch_eurostat_home_ownership_by_age` also lets
callers choose another `citizen` category, although the default is `NAT`.
The tax normalizer renames `D5` to `capital_tax_rate_proxy`; that is a **proxy
label chosen by the model**, not a Eurostat definition. Likewise, its output
column `property_taxes_pct_gdp` for `D59A` is a consumer alias for the broader
*current taxes on capital* item, not an official all-property-tax measure.
Empirical claims about capital-tax rates or resident-wide ownership must
retain these caveats. Eurostat's [`tessi162` indicator](https://doi.org/10.2908/TESSI162)
is a derived view **sourced from** `ilc_lvho07b`, not a fourth downloaded
product or a replacement for its DOI.

## Consumer-side validation gates

The [2026-11-10 source audit](../../docs/consumer-source-audits/wealth-rentier-dynamics-eurostat-covariates-2026-11-10.md)
records parser risks observed at the pinned consumer revision:

- The housing-overburden normalizer rejects multiple non-time slices, but
  discards the selected category codes. A single *wrong* `quantile`, `unit` or
  `freq` slice therefore still needs explicit verification before use.
- The ownership normalizer assumes one selected `geo`, `citizen`, `tenure`,
  `sex` and `unit` without checking the decoded values. Because it emits only
  `(country, year, age, home_ownership_rate)`, multiple unexpected slices can
  produce ambiguous repeated keys or mislabeled observations.
- The tax normalizer uses `pivot_table(..., aggfunc="first")` for `na_item`
  and `year`, without validating the other dimension codes. If a future
  response contains duplicate candidates, the chosen value could be silent.
- Both ownership and tax decoders process the values but discard Eurostat
  observation-status flags. Missing or flagged observations need explicit
  handling and an audit trail before publication.

These are **code-level risks**, not evidence of actual duplicates or wrong
official values in a downloaded response. The corrective parser tests and
first real acquisition belong in the consumer repository.

## Reproducibility and reuse

Eurostat [says its API serves the latest dataset versions](https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-introduction)
without providing past-version queries. Re-running the same URL can yield
revised values. Capture the exact query and country, returned JSON bytes and
SHA-256, retrieval date, dataset and structure update timestamps, filters,
statistical unit, DOI, source warnings and consumer transformation revision.
Treat the three responses as independently versioned inputs; never merge
their provenance into a single undifferentiated file.

Eurostat's [copyright and reuse notice](https://ec.europa.eu/eurostat/help/copyright-notice)
permits reuse of statistical data for commercial and non-commercial purposes
with source acknowledgement and disclosure of modifications. Its exceptions
for third-party material or specifically restricted data must still be
respected. No actual dataset snapshots have been downloaded or committed in
the central registry under this record.
