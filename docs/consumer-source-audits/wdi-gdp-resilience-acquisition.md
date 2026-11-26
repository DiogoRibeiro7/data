# WDI GDP resilience candidate acquisition

Run the manual **Acquire WDI GDP resilience candidate** workflow after merging.
Alternatively, from the repository root:

```bash
python -m unittest discover -s tests -p test_acquire_wdi_gdp_resilience.py -v
python scripts/acquire_wdi_gdp_resilience.py --output wdi-candidate
```

The output directory must not already exist. The default scope is 1995–2025,
33 countries (EU-27 plus US, UK, Switzerland, Japan, China and India) and eight
WDI indicators. The script batches countries per indicator, retrieves all
pages and indicator metadata, checks source and observation identities, and
writes SHA-256 checksums, retrieval URLs and timestamps, null/absent counts
and complete-year coverage to manifest.json. Raw bytes are unchanged.

Download the workflow artifact named wdi-gdp-resilience-candidate after a
successful run. Do not promote an incomplete directory or treat API access
as redistribution permission. Review indicator-specific source notes,
units and third-party terms before canonical registration. A successful
acquisition does not establish an atomic upstream vintage across indicators.
Missing data remain missing, and the sample is not the original 40-country
European map. This workflow does not automatically commit data.
