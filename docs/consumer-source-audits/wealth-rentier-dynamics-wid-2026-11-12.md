# Supplemental consumer audit: WID net-personal-wealth shares

Reviewed: **2026-11-12**. Downstream code inspected at
[`bf0e75b9`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/data_sources.py),
with the [extractor orchestration](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/datasets.py),
[data guide](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/data/README.md)
and [offline tests](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/tests/test_data_sources.py).
This is a static source-contract review, **not** evidence of a successful
country extraction, dataset version or observed empirical result.

## Statistical series and its scale

The [publisher's codes dictionary](https://wid.world/codes-dictionary/)
defines a distributed-variable key as a series, percentile, geography and
year; its `s` series type is a **fraction of total wealth or income**, not
a percentage number. The consumer selects:

| Dimension | Code | Meaning |
| --- | --- | --- |
| Variable | `shwealj992` | Share of **net personal wealth** distributed among equal-split adults (age 20+). Both wealth concept and population must remain fixed. |
| Percentile | `p99p100` | Top 1% wealth share: model's main observed outcome, `top_1_wealth_share`. |
| Percentile | `p90p100` | Top 10% share, `top_10_wealth_share`. |
| Percentile | `p0p50` | Bottom 50% share, `bottom_50_wealth_share`. |
| Country | `PT`, `ES`, `FR`, `IT`, `IE`, `NL` | Six separate country series selected by the consumer. |
| Unit | fraction of 1 | A source value of `0.25` corresponds to 25% of total personal wealth. The consumer must not divide it by 100 again. |

An equal-split adult series is not an individual-ownership or household-unit
series; a wealth *share* is not a mean wealth level or a national-currency
stock. Because the underlying balance sheet is **net** of debts, investigate
negative or apparently unusual lower-tail shares instead of blindly clipping
all values to `[0, 1]`.

WID also offers specific-series and country-level bulk downloads, in addition
to its [full-database download](https://wid.world/data/). The current research
pipeline is configured for a **user-supplied local full-database ZIP**; this
does not establish that a particular direct ZIP URL is a supported immutable
API. The archive revision is not pinned in the registry.

## What the consumer actually does

The CLI accepts `--wid-zip data/wid_all_data.zip` and runs
`extract_wid_wealth_shares()` for each requested country. The active loader,
`load_wid_wealth_shares_from_bulk_zip()`, opens only
`WID_data_<CC>.csv` in that ZIP, uses semicolon-separated rows, filters
`variable=shwealj992` to the three exact percentiles and pivots to
country-year shares. `assemble_country_year_panel()` merges files named
`wid_country_<cc>.csv` when available. Synthetic fixtures are not substituted
for an observed WID response.

There is also a *different* path: `download_wid_country()` requests a
country ZIP and passes its first CSV member to `normalize_wid_country_data()`.
That older normalizer pivots by `variable` and renames legacy indicator codes;
it does **not** select `shwealj992` by a separate `percentile` dimension.
The existing mock tests for that path use older example codes. Treat the
paths as distinct, not two equivalent proofs of obtaining the same outcome.

## Verified downstream risks

1. **Silent selection**: after filtering variable and percentile,
   `pivot_table(index="year", columns="metric", values="value",
   aggfunc="first")` will select one value for repeated year/percentile
   combinations. The loader does not check whether duplicates agree or
   reflect a changed WID definition or mixed country members.
2. **Country label substitution**: the loader trusts the archive member name
   and assigns its requested `country_code` to every normalized row without
   validating any embedded `country` field. A mislabeled member could
   therefore produce plausible-looking data for the wrong geography.
3. **Coverage and missing outcome**: the loader checks for the *existence*
   of `top_1_wealth_share` as a column, not non-null observations for the
   model's requested country-year period. The extraction orchestration can
   also report a failed country without aborting all other downloads.
4. **No pinned observation vintage**: neither the source archive SHA-256 nor
   its per-country member checksum, acquisition date, WID metadata notes or
   transformation revision is carried into the normalized country-year CSV.
   Re-running an unpinned archive download may change the series.
5. **Unit/cross-source ambiguity**: the CSV output columns do not encode that
   shares are fractional values for equal-split adults. Later joins with
   percent-valued Eurostat covariates or alternative population definitions
   need explicitly recorded units and provenance.

These are **implementation risks identified from code**. No live ZIP was
retrieved here, so this audit does not assert actual duplicates, invalid
geographies, gaps, suspicious wealth shares or changes between WID vintages.

## Acceptance criteria for a first empirical WID acquisition

1. Download a dated WID archive from the publisher; keep raw data out of the
   public central registry and version control. Record original URL or page,
   UTC timestamp, byte count, SHA-256, archive member list, country metadata
   and selected variable/population codes in a consumer-local manifest.
2. Read each of the six country members, validate country codes **inside**
   available source rows, all required headers, `shwealj992`, the three
   requested percentile codes, numeric years and non-null numeric values.
3. Before pivoting, prove unique `(country, variable, percentile, year)` keys.
   Accept byte-identical duplicate rows only under a documented policy; reject
   conflicting duplicates and report affected series explicitly.
4. Preserve shares as fractions of one; describe conversions to percentages
   only for display. Use source-specific plausibility checks and inspect any
   nonstandard lower-tail values; never replace missing shares with zero.
5. Report six-country coverage separately for top 1%, top 10% and bottom 50%,
   including year ranges, missing observations and source methodological
   flags. Reject an empirical fixed-effects run without adequate observed
   outcome coverage, even when covariates are present.
6. Add offline ZIP fixtures that exercise conflicting duplicates, a wrong
   embedded country, a missing `p99p100` year, a missing country member,
   nonnumeric and missing values, the correct fraction scale, and the legacy
   country-download path. Verify panel assembly does not silently invent a
   top-1% outcome from ECB DWA or synthetic files.
7. Preserve the exact input checksum and consumer revision in resulting
   artifacts and make provenance checks reproducible before citing country-
   year estimates. Keep country-specific WID methodological notes and
   changes in the empirical release documentation.

## Registry decision and rights boundary

The publisher's [open-access data portal](https://wid.world/data/) and
[download instructions](https://wid.world/codes-dictionary/) allow study of
the source, but the previously reviewed WID pages did not establish explicit
permission to mirror the **entire bulk archive** in this public registry.
The existing `redistribution: unresolved`, `review_status: terminal`, and
`terminal: true` remain unchanged. This supplemental audit improves the
consumer acquisition contract; it does **not** reopen the distribution-rights
decision, claim new publisher permission or register a raw-data snapshot.
