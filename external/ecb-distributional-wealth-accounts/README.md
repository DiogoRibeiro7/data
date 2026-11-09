# ECB Distributional Wealth Accounts — quarterly wealth shares

The [ECB Distributional Wealth Accounts (DWA)](https://data.ecb.europa.eu/data/datasets/DWA)
combine household-sector national accounts with distributional estimates.
They are **experimental quarterly statistics**, not household microdata and
not an immutable historical release. The [ECB overview](https://data.ecb.europa.eu/sites/default/files/2024-01/DWA%20Overview%20note_0.pdf)
lists net-wealth shares for the top 5%, top 10% and bottom 50%, among other
indicators. No top-1% DWA share was verified in this audit; it must not be
substituted for the WID top-1% wealth concentration outcome.

## Official series identities

The ECB Data Portal explicitly identifies these Portuguese series:

| Published series key | Measure | Frequency/unit |
| --- | --- | --- |
| [`DWA.Q.PT.S14._Z._Z.NWA.T5.PT.S.N`](https://data.ecb.europa.eu/data/datasets/DWA/DWA.Q.PT.S14._Z._Z.NWA.T5.PT.S.N) | Net household wealth share, top 5% | Quarterly, percent |
| [`DWA.Q.PT.S14._Z._Z.NWA.T10.PT.S.N`](https://data.ecb.europa.eu/data/datasets/DWA/DWA.Q.PT.S14._Z._Z.NWA.T10.PT.S.N) | Net household wealth share, top 10% | Quarterly, percent |

The [ECB DWA catalogue](https://data.ecb.europa.eu/data/concepts/distributional-wealth-accounts)
also lists bottom-50% shares (`B50` grouping). The country and grouping
codes are dimensions of a complete series key; the fields cannot be treated
as interchangeable. The consumer's target geography covers PT, ES, FR, IT,
IE and NL. The DWA country codes are the two-letter ECB codes, unlike the
three-letter ISO codes used by the OECD extractors.

The [ECB API documentation](https://data.ecb.europa.eu/help/api/data)
defines a dataflow-relative SDMX key with individual dimensions and supports
`format=csvdata`, date ranges, revisions and historical observation versions.
The portal series URLs above are source-identity evidence, **not proof that
their corresponding API responses have been downloaded or independently
validated** in this registry.

## Verified consumer compatibility gap

The [`wealth_rentier_dynamics` implementation](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py)
currently requests:

```text
https://data-api.ecb.europa.eu/service/data/DWA/*?format=csvdata
```

This is an unconstrained wildcard request. Its normalizer has three
unverified assumptions that prevent us from calling the extraction complete:

1. It converts `time_period` to an integer `year`, but DWA periods are
   quarterly (`YYYY-Qn`). The period parser therefore loses valid quarterly
   observations, and the aggregation rule to annual data is undefined.
2. It pivots the `series`/`key` column against labels such as `top_1_share`
   and `bottom_50_share`. Official ECB series instead use complete
   dimension-coded keys (for example the two Portuguese keys above); the
   expected aliases are not mapped to published identifiers.
3. It expects `net_wealth_to_income` as another series alias and renames it
   to `wealth_to_income_ratio`, but no matching official DWA series key or
   compatible income denominator has been verified.

The broad request also retrieves many unrelated measures and countries,
increasing response size. The consumer needs exact keyed requests, explicit
indicator mapping, proper quarterly parsing, observation status handling
and a documented annualization method before these values can enter a
country-year model. None of that work is claimed to be implemented here.

## Rights and provenance

The [ESCB statistics reuse policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html)
allows reuse of unmodified public ESCB statistics with source attribution,
while excluding unauthorized third-party data and reserving revised values.
The general [ECB copyright notice](https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html)
requires users to disclose transformations explicitly. Because this consumer
would reshape or aggregate DWA observations, the rights for central
distribution of its transformed panel remain unresolved pending a specific
review; no data bytes are mirrored.

When the consumer's extraction is repaired, pin full SDMX keys, access
timestamp, ECB source release/update timestamp, observation periods/flags,
units, raw response SHA-256, and code revision. Store source responses in a
project-local data cache or the planned shared database only after those
controls are defined.
