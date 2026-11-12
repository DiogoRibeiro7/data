# WID.world wealth shares — bulk database reference

The [World Inequality Database](https://wid.world/data/) publishes distributional
wealth and income estimates assembled from national accounts, surveys, tax
records and other research sources. Its [codes dictionary](https://wid.world/codes-dictionary/)
describes direct, country-level and full-database downloads. The data series
are revised as new information and methods become available; the download page
is not an immutable version identifier.

## Actual consumer contract

[`DiogoRibeiro7/wealth_rentier_dynamics`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/data/README.md)
has an optional Python loader for the WID full database ZIP. The implementation
is pinned here for inspection:

- [Bulk archive loader](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/src/wealth_dynamics/data_sources.py)
- [Offline parser tests](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/bf0e75b91f68911e306627f257baf52893f0e91c/tests/test_data_sources.py)

| Contract field | Consumer expectation |
| --- | --- |
| Local archive | `data/wid_all_data.zip`, provided by the user |
| Member filename | `WID_data_<CC>.csv` (two-letter country code) |
| Delimiter | Semicolon |
| Required columns | `variable`, `percentile`, `year`, `value` |
| Variable | `shwealj992`: net personal wealth share, equal-split adults |
| Percentile `p99p100` | Top 1% wealth share |
| Percentile `p90p100` | Top 10% wealth share |
| Percentile `p0p50` | Bottom 50% wealth share |
| Initial countries | PT, ES, FR, IT, IE, NL |
| Units | Fraction of total net personal wealth: `0.25` means **25%**, not `0.25%` |
| Population | Adults aged 20+, equal-split between adult household members (`j992`) |

The consumer reads only the required country members instead of extracting
the entire archive. Its model panel has **no observed top-1% wealth-share
outcome** unless a real archive is supplied. Synthetic example panels are not
substitutes for empirical WID observations.

The official [WID codes dictionary](https://wid.world/codes-dictionary/)
specifies the share unit as a fraction of one and distinguishes individual,
equal-split and tax-unit populations. These are wealth *shares*, not mean
household wealth, absolute euros or an interchangeable percentage-point scale.
Signed net wealth may produce unusual lower-tail shares; a generic hard
`[0, 1]` clipping rule is not an adequate data-quality check.

The [2026-11-12 WID consumer audit](../../docs/consumer-source-audits/wealth-rentier-dynamics-wid-2026-11-12.md)
identifies four extraction gates before empirical use:

1. Verify each country member's embedded geography, `shwealj992` and the
   exact `percentile` keys, then record coverage per country and year.
2. Reject repeated `(year, variable, percentile)` rows with conflicting
   values. The current bulk normalizer uses `aggfunc="first"`, which would
   silently choose an observation when duplicates exist.
3. Require non-null top-1% outcomes for the intended empirical sample;
   presence of the *column* does not establish completeness of its values.
4. Pin archive SHA-256, file/member provenance and transformation revision.
   The separate `download_wid_country()`/`normalize_wid_country_data()` path
   uses a different legacy code pivot and should not be taken as evidence
   that the current `shwealj992` extraction succeeded.

These are code-level risks, **not** a claim of faulty values in a downloaded
WID response. The official dictionary also documents country-specific bulk
downloads; the full-database ZIP is the consumer's configured local-file
path, not the only access option offered by the publisher.

To use the source, download the bulk archive through the official WID data
page, keep it outside version control and run the consumer's documented
`--wid-zip` extraction command. Before a reproducible empirical release,
record the download date, archive size, SHA-256, per-member checksums and
country-series vintages. Preserve the country metadata notes alongside
values where available.
The current project documentation does **not** identify a frozen WID archive
checksum, and this registry does not invent one.

## Reuse decision

The WID pages describe *open-access data* and make the database available for
download. No explicit terms covering redistribution of the complete bulk ZIP
in a separate public repository were established in the reviewed WID pages.
Accessibility is not treated as an affirmative full-archive licence.

**Metadata only; redistribution unresolved.** No ZIP or extracted WID country
tables are copied here. Reassess central storage only with explicit publisher
reuse terms and a verified snapshot checksum. The World Inequality Report's
separate website notices should not be assumed to govern this database.
