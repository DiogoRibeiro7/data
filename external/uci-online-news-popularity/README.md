# UCI Online News Popularity

This source supports a separately labelled **non-Medium alternative study** of
social-network share counts for observed Mashable articles. It cannot supply
Medium findings, author concentration, or complete publication counts.

The [authoritative UCI record](https://archive.ics.uci.edu/dataset/332/online+news+popularity)
licenses the statistical dataset under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Its description explicitly separates the statistics from the original articles,
whose text is not distributed in the dataset. Research reuse of these licensed
statistical files is accepted with attribution and a description of modifications.
This does not clear retrieval of linked article bodies or imply Mashable endorsement.

Citation: Fernandes, K., Vinagre, P., Cortez, P., & Sernadela, P. (2015).
*Online News Popularity* [Dataset]. UCI Machine Learning Repository.
[DOI:10.24432/C5NS3V](https://doi.org/10.24432/C5NS3V).

## Snapshot identity

Downloaded directly from the [UCI ZIP endpoint](https://archive.ics.uci.edu/static/public/332/online+news+popularity.zip)
on 2026-10-14. The endpoint is mutable and supplies no immutable Git revision;
identity is the following locally measured content hash, not an invented version.

| File | Bytes | Local SHA-256 |
| --- | ---: | --- |
| `online-news-popularity.zip` | 7,476,401 | `dba2ae526f62ccef6f2f8efb53b0268319f4d0d2719bb98d88958cfe31d58a22` |
| `OnlineNewsPopularity/OnlineNewsPopularity.csv` | 24,311,769 | `b66d9088632308cc27fa35af847650d174a5a50503987c4e511de94a99d1c218` |
| `OnlineNewsPopularity/OnlineNewsPopularity.names` | 12,102 | `7a50337dec4e453988d79052e7ade89bfa1f28d15834e45f72d923001fa6aff2` |

The 61 documented columns include URL, `timedelta`, statistical features and
`shares`. There are no author identifiers or precise publication timestamps.
The URL path can supply a date with explicitly limited provenance. The landing
page and names file advertise 39,797 instances; downstream work must count the
CSV itself and report any difference. Source age and URL-derived age must be
compared without silently forcing agreement.

The actual retrieved CSV has **39,644 rows**, all retained for article-level
share analysis: no duplicate URLs, missing article IDs, or invalid share counts
were found. The 153-row difference from the documentation is not an analysis
exclusion. URL dates span 2013-01-07 through 2014-12-27 (720 observed dates).
Source ages range from 8 to 731 days; 9,463 rows disagree by 1–5 days with the
age implied by the documented 2015-01-08 acquisition date and URL path date.
Both representations are retained without correction. These are local audit
findings for the pinned hash, not a new claim about the sampling frame.

Only metadata and provenance are recorded here. Raw files, extracts, and analysis
outputs remain project-local. No canonical dataset promotion is proposed.
