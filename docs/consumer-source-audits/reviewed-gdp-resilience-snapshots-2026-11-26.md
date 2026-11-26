# Reviewed GDP resilience source snapshots — 26 November 2026

## Validation and provenance

The uploaded candidate ZIP archives were opened and their manifest-listed source bytes independently hashed; original raw observations and source metadata are retained. Both World Bank products have explicit CC BY 4.0 dataset-catalog licenses, subject to attribution and provider exceptions.

| Candidate | Archive SHA-256 | Manifest SHA-256 | Raw files | Raw bytes |
|---|---|---|---:|---:|
| WDI | 67e93b7dd51b71588cd4f01b10b4c2b98309eef25ece82d3df52b26927f16747 | 45807a39fe812ba771fb88812509cdd55c23b2f0cc020de799bde86cb2e1838f | 24 | 1843115 |
| CWON | 93ef389dc2c831231a72c84e6d7b18087a4d5ae6263d3e5bb5260b83b8b62003 | 9c64681577f4f4bf89f4e135ec05772bfb2712e8fcde52beaa8050be7145f6be | 16 | 1432199 |

- [WDI catalog and license](https://datacatalog.worldbank.org/infrastructure-data/search/dataset/0037712/world-development-indicators). Eight series, 33 countries, 1995–2025; 8,116 observed and 68 explicit nulls. USA broad-sector shares missing in 1995–1996 and 2022–2025; Japan missing 2025. Manufacturing missing all years for Bulgaria. Retain all gaps.
- [CWON catalog and license](https://datacatalog.worldbank.org/search/dataset/0042066/wealth-accounting). Seven series, 33 requested countries, 1995–2020; 5,821 observed, 182 absent cells and three explicit nulls. Independent checks of all rows confirmed unique country-year identities, matching indicator and source IDs, finite observed values, matching manifest coverage. Cyprus is absent across all seven series; Bulgaria is missing total wealth, foreign assets and foreign liabilities in 1995. Complete 32-country common window 1996–2020. The source-before and source-after files are byte-identical; store the first copy only, preserving both URLs and timestamps in the unchanged manifest.
- WDI observation vintage 2026-11-11; retrieved 2026-11-26 17:58:51.604028Z–17:58:59.867295Z. CWON vintage 2024-10-08; retrieved 2026-11-26 20:00:03.488609Z–20:00:07.058258Z.

## CWON indicator interpretation

| Series | Observed | Null | Absent |
|---|---:|---:|---:|
| NW.TOW.PC — national comprehensive wealth per capita | 831 | 1 | 26 |
| NW.PCA.PC — produced capital per capita | 832 | 0 | 26 |
| NW.HCA.PC — human capital per capita | 832 | 0 | 26 |
| NW.NCA.TOTL.PC — renewable natural capital per capita | 832 | 0 | 26 |
| NW.NCA.SSOI.PC — nonrenewable natural capital per capita | 832 | 0 | 26 |
| NW.NFA.PC — foreign assets per capita | 831 | 1 | 26 |
| NW.NFL.PC — foreign liabilities per capita | 831 | 1 | 26 |

Several API sourceNote/sourceOrganization fields still describe constant 2018 US dollars and the 2021 edition, or are empty. Do not rewrite those raw fields. The indicator titles, Wealth Accounts 2024 catalog and [official 2024 methodology](https://www.worldbank.org/en/publication/the-changing-wealth-of-nations), [total wealth indicator](https://esgdata.worldbank.org/data/indicators?income=all&ind=NW.TOW.PC&lang=en&region=all&transform=level), [produced capital indicator](https://esgdata.worldbank.org/data/indicators?income=all&ind=NW.PCA.PC&lang=en&region=all&transform=level) and [nonrenewable natural capital indicator](https://esgdata.worldbank.org/data/indicators?ind=NW.NCA.SSOI.PC&lang=en) identify the revised real chained 2019-dollar Törnqvist measures. Resolve any remaining series-specific uncertainty before publishing findings. Foreign assets and liabilities are distinct series, not net foreign assets. Real chained components are nonadditive; do not reconstruct national wealth by addition or aggregate country-level chained wealth levels into an EU total.

Bulgaria total wealth 1996 = 192.051105905385 versus 52,911.7852856376 in 2020; the extraordinary growth implied by the baseline requires investigation. Report sensitivity excluding Bulgaria and using later endpoints. The primary balanced window is 1996–2020; sensitivity 1995–2020 excluding Cyprus and Bulgaria. Do not treat missingness, valuation changes, and physical-capital changes as equivalent.

## Promotion

After merging the registration tooling, run the manual **Register reviewed GDP resilience snapshots** workflow on main. It searches successful acquisition runs for the exact reviewed manifest SHA-256; it never refetches the source APIs. If missing or expired, stop rather than substitute a different vintage. The workflow validates the registry and pushes a new branch `register/reviewed-gdp-resilience-snapshots` only; no automatic main write or merge. Open the data PR from that branch after success. The earlier WDI PR #286 was still open and the canonical path was absent at review; do not merge it concurrently with the combined promotion.

Local alternative: extract the two original ZIPs outside the checkout and run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/promote_reviewed_gdp_snapshots.py --wdi /path/to/wdi --cwon /path/to/cwon
```

Regenerate and verify using the commands in the registration workflow before committing. Temporary adoption exemptions must be removed after the downstream analysis pins its actual data paths and hashes. No IMF workbook or data is included.
