# October 2026 IMF WEO: GDP resilience source acquisition

Reviewed 2026-11-26. Consumer: [GDP economic resilience study](https://github.com/DiogoRibeiro7/Medium-Blog/pull/776). This is a metadata-only acquisition contract, not a canonical dataset or evidence of actual returned observations.

## Official source and permitted handling

- [IMF WEO portal](https://data.imf.org/Datasets/WEO): choose **October 2026 WEO Entire Dataset in Excel**, released October 2026.
- [WEO FAQ](https://data.imf.org/en/Datasets/WEO/Frequently-Asked-Questions).
- [IMF Copyright and Usage](https://www.imf.org/en/about/copyright-and-terms): special statistical-data terms allow reuse subject to conditions, including attribution and integrity. The general terms prohibit automated bulk downloads without permission, and potential commercial reuse requires contacting copyright@imf.org. The monetized publication use case must be resolved before reproducing WEO-derived results in that publication.
- [IMF WEO Database Transition Guide](https://data.imf.org/-/media/iData/External-Storage/Documents/2C2B2F3E671A4B11ABE756E2441FD6F0/en/WEO-Database-Transition-Guide.pdf): the newer portal uses COUNTRY.ID, INDICATOR.ID, UNIT, SCALE and LATEST_ACTUAL_ANNUAL_DATA columns.

Download the edition manually from the official portal. Do not commit the workbook, raw rows, or transformed series to this public repository, and do not upload the workbook to CI artifacts. No automated download workflow is provided. Keep it in a local data directory outside the checkout. Record the exact source download link and edition at retrieval. Pending permission, WDI is the primary publication source and the WEO comparison is optional.

## Local inspection

Python 3.12+:

```powershell
python -m pip install openpyxl==3.1.5
python -m unittest discover -s tests -p test_inspect_imf_weo_gdp.py -v
python scripts/inspect_imf_weo_gdp.py --workbook "C:/data/WEOOct2026all.xlsx" --output "C:/data/weo-oct2026-coverage.json" --confirm-october-2026
```

The command uses no network access, validates the Countries worksheet and the expected horizon through 2031, records SHA-256 and byte size, checks unique country/indicator identities, and reports coverage and actual-data cutoffs. It does not export observation values. The report is local; review its contents before sharing. The edition is manually confirmed, not cryptographically authenticated by the workbook header. The parser has synthetic tests but has not yet been exercised against the real October 2026 workbook.

## Scope and interpretation

33 countries (fixed EU-27 plus US, UK, Switzerland, Japan, China and India); 1995–2031; NGDPD (current USD), PPPGDP (current international dollars), NGDP_RPCH (real GDP annual change). Preserve original unit and scale; confirm them before converting billions to dollars. EU aggregates must be computed only from compatible additive measures across fixed membership; never sum real growth rates. Reconcile common years with the pinned WDI snapshot when its registration is confirmed. WEO may revise historical values; divergence is not evidence of error without investigating definitions and vintages.

The reported actual cutoff is series-specific. Years after it up to the release year are labelled estimate_or_projection; later years are projections. Historical years with no cutoff remain unknown_actual_status. Even values through the cutoff are IMF's historical series, not independently audited national observations.

Next: obtain the local coverage report, review the terms and permission, and decide whether to retain WEO solely as a local sensitivity check or establish a permitted reusable snapshot. Do not edit generated registry catalogs until an actual source record is accepted.
