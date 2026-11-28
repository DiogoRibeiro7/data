# OECD health systems panel — mortality, expenditure and covariates, 2000-2023

Eight OECD SDMX responses that, together, give a country-year panel of the 38 OECD members: avoidable, treatable and preventable mortality, life expectancy, health expenditure and its financing, tobacco and alcohol consumption, real GDP per person, population by age and weekly excess mortality since March 2020. The OECD remains the byte source; nothing is mirrored here.

## What the source provides

Publisher: Organisation for Economic Co-operation and Development (OECD), through its public SDMX REST interface (`https://sdmx.oecd.org/public/rest/data`). Terms: [OECD Terms and Conditions](https://www.oecd.org/en/about/terms-conditions.html), with series-specific third-party rights still to be verified, hence `redistribution: unresolved`.

The responses used, each with the exact query recorded in `metadata.yaml` together with byte count and SHA-256 of the 2026-11-28 retrieval:

- Avoidable, treatable and preventable mortality, age-standardised per 100,000: `OECD.ELS.HD,DSD_HEALTH_STAT@DF_AM`.
- Life expectancy at birth: `OECD.ELS.HD,DSD_HEALTH_STAT@DF_LE`.
- Health expenditure (System of Health Accounts): `OECD.ELS.HD,DSD_SHA@DF_SHA`, requested with the key `.A.EXP_HEALTH.USD_PPP_PS+PT_B1GQ+PT_EXP_HLTH._T+HF1+HF3.._T+HC6._T._T...` (USD PPP per person, share of GDP, share of health expenditure; all financing schemes, government and compulsory schemes, and preventive care). The consumer keeps the total-provider, total-mode rows and writes `sha_slim.csv`; the recorded hash is of that derived file.
- Tobacco and alcohol consumption: `OECD.ELS.HD,DSD_HEALTH_LVNG@DF_HEALTH_LVNG_TC` and `@DF_HEALTH_LVNG_AC`.
- Real GDP per person: `OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HVPVOB`.
- Population by age: `OECD.ELS.SAE,DSD_POPULATION@DF_POP_HIST`.
- Weekly excess mortality: `OECD.ELS.HD,DSD_HEALTH_MORTALITY@DF_MORTALITY_EXCESS` (from 2020; first consumer only).

## Consumers

- `medium-blog/oecd-health-spending-outcomes`: treatable mortality against spending (cross-section, fixed effects, long differences), a 72-specification efficiency curve and 2020-22 excess deaths.
- `medium-blog/oecd-health-austerity`: event study of the post-2009 health spending cuts against treatable mortality and life expectancy.

Both run the same `fetch_data.py` and rebuild the panel at every run; no CSV is committed in either folder.

## Why the bytes are not mirrored

The OECD dataflows are revised and extended, so a stored copy would drift from the publisher, and rights to the individual national series have not been cleared for redistribution. The record therefore pins one retrieval by hash and keeps the publisher as the source. All eight files were byte-identical across two full downloads about 80 minutes apart on 2026-11-28; that shows short-run stability, not immutability.

## Known data characteristics

- Treatable mortality has no observations for Greece before 2014, Ireland starts in 2007 and Portugal has gaps in 2004-2006 and 2020-2021.
- Real health expenditure per person falls by 17% and 11% for Luxembourg in 2011 and 2012 and rises by 28% for Sweden and 15% for Japan in 2011, with no matching movement in GDP per person; the consumers treat these as series breaks.
- Constant-price USD PPP series can be rebased by later OECD releases.

## Open items

See the `resolution` block: add run-time hash verification to both consumers and verify series-level ownership before considering a canonical snapshot.
