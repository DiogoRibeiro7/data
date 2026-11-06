# WID.world wealth shares — bulk database reference

The [World Inequality Database](https://wid.world/data/) publishes distributional
wealth and income estimates assembled from national accounts, surveys, tax
records and other research sources. Its [codes dictionary](https://wid.world/codes-dictionary/)
describes direct, country-level and full-database downloads. The data series
are revised as new information and methods become available; the download page
is not an immutable version identifier.

## Actual consumer contract

[`DiogoRibeiro7/wealth_rentier_dynamics`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/data/README.md)
has an optional Python loader for the WID full database ZIP. The implementation
is pinned here for inspection:

- [Bulk archive loader](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py)
- [Offline parser tests](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/tests/test_data_sources.py)

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

The consumer reads only the required country members instead of extracting
the entire archive. Its model panel has **no observed top-1% wealth-share
outcome** unless a real archive is supplied. Synthetic example panels are not
substitutes for empirical WID observations.

To use the source, download the bulk archive through the official WID data
page, keep it outside version control and run the consumer's documented
`--wid-zip` extraction command. Before a reproducible empirical release,
record the download date, archive size, SHA-256 and country-series vintages.
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
