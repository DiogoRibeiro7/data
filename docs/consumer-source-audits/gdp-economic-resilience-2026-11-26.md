# GDP composition and economic resilience: consumer source audit

Reviewed 2026-11-26. Consumer: [Medium-Blog research protocol](https://github.com/DiogoRibeiro7/Medium-Blog/blob/main/research/gdp-economic-resilience/RESEARCH_PROTOCOL.md), PR #776. Registry inspected at commit `22df7acf5999f4947fb6b9155135e38104b321c8`. This is a metadata/catalog audit, not a live extraction or observation-level validation. No generated catalog or existing canonical data is modified.

## Reuse first

All paths below are relative to datasets/ at the inspected commit. SHA-256 values are declared in the corresponding metadata.yaml, not independently recomputed in this audit.

| Path | SHA-256 | Intended use |
|---|---|---|
| eurostat-services-energy-time/raw/nama_10_a10.json | 6a100cf6bbe75ca4d0e88203bc12a35088c740bc48491b037cca0b4f2816a652 | A*10 nominal and real GVA, 1995 onward |
| eurostat-services-energy-time/raw/nama_10_a10_e.json | 6dc6ddbdcd9054101f4df1f7fe86044b6786f2feda6beeabc5ea5d0c49bce425 | Employment and hours |
| eurostat-services-relative-prices/raw/nama_10_a64.json | 11ee27e6a719fc8a255c7b48ddae42c3301e0632578191e5e7545c0b2602a8c4 | Detailed GVA, compensation and other income components |
| eurostat-services-relative-prices/raw/nama_10_a64_e.json | c0c90f441e21612bec574d7cf0df0ea6852b313e3e6a0e2530dfe16138139bc9 | Detailed hours |
| eurostat-material-use/raw/nama_10_gdp.json | 8adaef8903d9b0838d2e615e75142e1007ec43eab615dd9aa3e57f95c5fd3956 | EU GDP current prices and chain-linked volumes, 2000 onward |
| eurostat-eu-convergence-education/raw/nama_10_pc.json | 15b5e3f72789bbd76fa4c17f890aae40d80cd11c0a2f6acce7265d52a7b1e4ff | GDP and actual individual consumption per capita in PPS |
| eurostat-eu-convergence-education/raw/nama_10_lp_ulc.json | 456047b0f1b71e4e659dc7104696a5feb72a3dde045995ed0a10286bc62fe071 | Comparative productivity per hour/person |
| eurostat-services-energy-time/raw/nama_10_pc.json | 03811a0d57751b88dd24005689e98e29776d949121011dc711369d51cdba25f8 | Real per capita GDP and consumption |
| eurostat-services-energy-time/raw/nama_10_pe.json | 72f9cb832d04789ea347d057d49b6dd41fd1405e883fc6c50df09f1a1d1429dc | Population |

Existing Eurostat data are covered by the recorded Eurostat reuse policy. Actual geographic and year coverage must be checked from payloads, especially UK and Switzerland. A*10 includes manufacturing C nested in B-E; exclude C from the ten-sector concentration calculation. For A*64 exclude nested J61, Q86, Q87_Q88 from section-level totals; audit omitted sections and reconciliation residual before any HHI calculation. Use CP_MEUR for additive GVA shares and CLV20_MEUR for within-series real growth, not additive cross-sector shares. Never sum EU aggregate and member states. Preserve missing values and flags. Distinct November retrievals are not an atomic vintage.

Other existing external records: AMECO autumn 2026 and archived vintages are candidates for macro robustness, Maddison 2023 for historical context, ECB distributional wealth accounts for household wealth (not comprehensive national wealth), Eurostat inward FATS ICT for ownership context. Do not treat these as canonical snapshots.

## Missing or insufficient coverage: acquisition queue

These are candidate upstream sources, not newly registered records. The inspected catalogs do not show dedicated records for the following study inputs.

| Priority | Product | Requested data / scope | Source |
|---|---|---|---|
| P0 | World Development Indicators | NY.GDP.MKTP.CD, NY.GDP.MKTP.PP.CD, NY.GDP.MKTP.KD, SP.POP.TOTL, NV.AGR.TOTL.ZS, NV.IND.TOTL.ZS, NV.IND.MANF.ZS, NV.SRV.TOTL.ZS; 1995 onward | https://data.worldbank.org/ |
| P0 | IMF WEO | NGDPD, PPPGDP, NGDP_RPCH; dated edition, actual vs estimates separately | https://www.imf.org/en/Publications/WEO/weo-database |
| P1 | Changing Wealth of Nations | Real comprehensive wealth per capita and asset components; release-specific coverage | https://www.worldbank.org/en/publication/the-changing-wealth-of-nations |
| P1 | OECD STAN | Harmonised industry GVA, hours, employment, capital measures where available | https://www.oecd.org/en/data/datasets/structural-analysis-database.html |
| P1 | OECD TiVA / ICIO | Domestic and foreign value added, input-output coefficients, release-specific classifications | https://www.oecd.org/en/topics/sub-issues/trade-in-value-added.html |
| P2 | ILOSTAT and occupational AI exposure research | Employment by occupation, ISCO mapping, separate dated exposure methodology | https://ilostat.ilo.org/ |
| P2 | UN Comtrade | Annual product-level export concentration and import dependencies, HS revisions and reporter coverage | https://comtradeplus.un.org/ |
| P2 | OECD household accounts | Real household disposable income per capita; distinguish adjusted vs unadjusted and gross vs net | https://data-explorer.oecd.org/ |

WDI request template: `https://api.worldbank.org/v2/country/{ISO3}/indicator/{INDICATOR}?format=json&source=2&date=1995:2025&per_page=1000`. Validate pagination, source identity, indicator metadata, observation units and per-indicator terms before promotion. Query EU members individually and aggregate only compatible additive measures; do not substitute a changing-membership region. WDI sector shares use GDP as denominator and are not automatically a complete GVA partition. WEO estimates must not be conflated with observations.

## Acceptance and sequence

1. Reuse pinned Eurostat files; verify checksums, dimensions, flags, key uniqueness, units and coverage in the consumer before creating active consumer contracts.
2. Acquire WDI responses in the registry using a manual reproducible ingestion workflow, one indicator/country query or documented batch per response; preserve raw bytes, pagination and retrieval metadata. Verify source-specific redistribution rights (including third-party exceptions) before canonical promotion.
3. Register other sources as external where rights or exact vintages remain unresolved. No unverified raw data in Git.
4. Produce missingness and common-year coverage matrices before selecting comparison years; do not impute missing observations as zero.
5. Keep code and figures in Medium-Blog, and manuscript in research-articles-medium. Do not publish numerical claims until computed from pinned inputs.

No new canonical dataset, external record or consumer relationship is claimed by this audit. The next PR should implement the P0 WDI acquisition and validation workflow; other acquisition tasks can follow independently.
