# Supplemental consumer audit: ECB Distributional Wealth Accounts

Reviewed: **2026-11-07**. Consumer code examined at
[`f3e6e3a5`](https://github.com/DiogoRibeiro7/wealth_rentier_dynamics/blob/f3e6e3a5b035b65d883ddd70f082f1fb6b34bc0a/src/wealth_dynamics/data_sources.py).
This is a source-code and upstream-documentation review, not a successful
download or a claim that the current empirical panel contains DWA data.

## Findings

| Area | Consumer assumption | Official ECB contract / consequence |
| --- | --- | --- |
| Request scope | `DWA/*?format=csvdata`, then filter by country locally | An unconstrained query does not pin a specific data series or limit transfer size; the ECB supports exact, dimension-coded SDMX keys and country filters. |
| Time | Convert `time_period` directly to numeric `year` | DWA series are **quarterly** (`YYYY-Qn`), so direct numeric conversion does not produce a valid annual year. |
| Indicator names | Pivot `key` values and rename `top_1_share`, `bottom_50_share`, `net_wealth_to_income` | ECB keys identify complete dimensional series; there is no verified mapping from those consumer aliases to the actual DWA keys. |
| Wealth concentration | Downstream expects a top-1% outcome | The [ECB overview](https://data.ecb.europa.eu/sites/default/files/2024-01/DWA%20Overview%20note_0.pdf) lists **top 5%, top 10% and bottom 50%** DWA shares; it does not establish a top-1% series. WID top-1% is a distinct source requirement. |
| Source vintage | No raw hash or observed period metadata pinned | ECB series are revised; repeating the same query without a dated response and checksum does not reproduce a prior analysis. |

The public ECB portal supplies an example of an explicit top-5% Portugal
series:
[`DWA.Q.PT.S14._Z._Z.NWA.T5.PT.S.N`](https://data.ecb.europa.eu/data/datasets/DWA/DWA.Q.PT.S14._Z._Z.NWA.T5.PT.S.N).
The [top-10% Portugal key](https://data.ecb.europa.eu/data/datasets/DWA/DWA.Q.PT.S14._Z._Z.NWA.T10.PT.S.N)
is likewise documented. Those official identities are linked by the
[source contract](https://github.com/DiogoRibeiro7/data/tree/main/external/ecb-distributional-wealth-accounts),
not yet backed by a verified raw CSV in this registry.

## Consumer acceptance criteria for a future acquisition PR

1. Select **explicit** `DWA` series keys and countries; confirm coverage and
   official measure names before downloading.
2. Parse quarters without dropping them; for annual panels, specify whether
   to select Q4, average quarters, or use another substantively justified
   aggregation. Do not silently treat quarterly values as annual values.
3. Map `T5`, `T10` and `B50` wealth-group measures to descriptive columns,
   preserving percentages, periods and observation flags. Do not manufacture
   `top_1_wealth_share` from top-5% or top-10% data.
4. Validate source CSV schema with fixture-based tests, then acquire actual
   responses and record full URL, timestamp, release vintage, raw SHA-256 and
   normalization revision. Identify missing countries or groups explicitly.
5. Cite the ECB and check the [ESCB reuse policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html)
   before publishing transformed/redistributed outputs. Use separate
   permissions for confidential household microdata.

The central `data` registry documents the source and the **blocking contract
gap**. The consumer must be updated in its own PR; this registry PR does not
change its downloader or state that the missing observed wealth data are now
available.
