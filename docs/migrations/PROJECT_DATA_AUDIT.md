# Research and project data audit

## Scope

This audit covers the first cross-repository migration batch tracked in issue #6:

- `Time-Series-Additive-Models`
- `nuclear_vs_wind_solar_cleanliness`
- `cpd-stress-test`
- `productivity_taxation_inequality_project`
- `health-data-science`
- `euro_area_development_model`
- `displacement-risk-lab-dynamodb`
- `crop-protection-predictive-science`

The goal is to distinguish reusable source data from project-local fixtures, derived outputs and reproducibility snapshots.

## Decision framework

Each candidate is classified as one of:

- **migrate** — appropriate to move into the central canonical dataset registry;
- **external-source-only** — register provenance centrally but keep bytes at the authoritative publisher or project snapshot;
- **keep-local** — fixture, synthetic sample, derived artifact, or intentionally vendored reproducibility input;
- **investigate** — provenance or redistribution terms are not yet sufficient for central reuse.

## Repository inventory

### Time-Series-Additive-Models

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/legacy/gm_sales.csv/.xlsx` | investigate | historical Quandl-era data; repo explicitly marks it legacy/non-canonical and provenance is incomplete |
| `data/legacy/recessions.csv/.xlsx` | investigate | same legacy policy; no maintained code depends on it |
| `data/legacy/tesla_search_terms.csv` | investigate | legacy Git-LFS snapshot with unresolved upstream provenance |

**Decision:** no migration. The repository itself says these files are retained only for provenance.

### nuclear_vs_wind_solar_cleanliness

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/raw/lifecycle_emissions_ipcc_ar5.csv` | external-source-only | third-party IPCC source data; repository data licence explicitly does not relicense upstream material |
| `data/lifecycle_emissions_ipcc_ar5.csv` | keep-local / duplicate | exact Git-blob duplicate of the raw copy |
| `data/processed/lifecycle_emissions_normalized.csv` | keep-local | deterministic derived output |
| `data/multimetric_cleanliness_reference.csv` | keep-local | project-produced literature-informed reference model under the project's CC BY 4.0 data licence |
| `data/grid_carbon_intensity.csv` | keep-local | approximate project reference table, not exact national accounting |
| `data/regions/*.json` | keep-local | project configuration/reference mixes with illustrative financing assumptions |

**Decision:** no raw byte migration. The IPCC source should be cited from its authoritative publication; project-produced reference tables remain with the analysis that defines them.

### cpd-stress-test

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/tcpd/nile.json` | external-source-only | cache of the Turing Change Point Dataset |
| `data/tcpd/well_log.json` | external-source-only | cache of the Turing Change Point Dataset |
| `data/mauna_loa_co2.csv` | investigate | real-data validation snapshot; source is not documented strongly enough in the repository |

The TCPD loader already uses the Alan Turing Institute repository as the authoritative source and treats the local files as caches.

**Decision:** register TCPD centrally; keep benchmark caches local for offline paper reproduction.

### productivity_taxation_inequality_project

| Candidate group | Classification | Reason |
| --- | --- | --- |
| OWID Grapher CSV caches | external-source-only | authoritative source is OWID, but many Grapher datasets contain third-party material whose original provider terms still apply |
| `fred_productivity_wages.csv` | external-source-only | FRED terms are series-dependent and can include third-party restrictions |
| generated `outputs/*.csv` | keep-local | analysis outputs, not source datasets |

The notebook already downloads public sources and uses `data/` as a cache.

**Decision:** centralize source records for OWID and FRED; do not promote cached CSVs.

### health-data-science

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/puf_early.csv` | keep-local | explicitly synthetic, generated for examples/tests, contains no real NCDB patient data |

**Decision:** no migration.

### euro_area_development_model

| Candidate group | Classification | Reason |
| --- | --- | --- |
| `data/raw/world_bank_country_panel.csv` | external-source-only | API cache from World Bank |
| `data/raw/country_panel.csv` | keep-local | combined project panel with project-specific provenance/transformation rules |
| `data/raw/coverage.csv`, `conflicts.csv`, coverage reports | keep-local | diagnostics / build artifacts |
| `data/fixtures/illustrative_country_panel.csv` | keep-local | fixture |
| `data/metadata/*.csv`, source registry | keep-local | project metadata required to interpret the model |
| `data/monetary/euro_area_snapshot_2026-05.json` | keep-local | calibrated project snapshot |
| duplicate copy under `src/monetary_sfc/data/` | keep-local / intentional package resource | same Git blob, packaged for runtime use |

The repository already has a mature source registry covering World Bank, Eurostat, OECD, ILOSTAT, WHO, UNDP, ECB, BIS and IMF.

**Decision:** do not duplicate the project's curated panel or metadata into the central repository. The central repository should point to authoritative providers, while this project retains its versioned reproducibility snapshots.

### displacement-risk-lab-dynamodb

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/raw/gdelt_events.csv` | keep-local | bundled deterministic synthetic data |
| `data/raw/ucdp_events.csv` | keep-local | bundled deterministic synthetic data |
| `data/raw/unhcr_population.csv` | keep-local | bundled deterministic synthetic data |
| `data/raw/world_bank_indicators.csv` | keep-local | bundled deterministic synthetic data |
| `reports/sample_run/raw/*` | keep-local / duplicate | exact Git-blob copies generated for the sample report |

The source-like filenames are intentionally synthetic. The real-source ingestion helpers target GDELT, UCDP, UNHCR and World Bank APIs.

**Decision:** no migration of bundled bytes. Register UCDP and UNHCR authoritative sources centrally because they are reusable public sources for future real-data workflows.

### crop-protection-predictive-science

| Candidate | Classification | Reason |
| --- | --- | --- |
| `data/processed/synthetic_field_trials.csv` | keep-local | controlled synthetic demonstration |
| `data/processed/hop_trial_primary.csv` | keep-local | project-specific derived analysis input |
| `data/raw/maize_bipolaris.csv` | keep-local + external-source-only | intentionally vendored exact Git object for offline reproduction; upstream repository is MIT licensed |
| `data/raw/richardson_gent_hop_downy_mildew.csv` | keep-local / investigate | public research data with excellent provenance, but upstream repository exposes no licence file |
| `data/raw/corvallis_monthly_weather_2009_2025.csv` | keep-local | manually transcribed coarse environmental proxy with project-specific provenance |
| result CSV/TXT files | keep-local | derived research outputs |

**Decision:** retain the reproducibility inputs inside the scientific project. Register the MIT-licensed maize Bipolaris upstream dataset centrally as a reusable source record. Do not centralize the hop trial until redistribution terms are explicit.

## Duplicate findings

The audit found several exact Git-blob duplicates, but most are intentional or project-local:

- `nuclear_vs_wind_solar_cleanliness/data/lifecycle_emissions_ipcc_ar5.csv` duplicates `data/raw/lifecycle_emissions_ipcc_ar5.csv`;
- `euro_area_development_model/data/monetary/euro_area_snapshot_2026-05.json` duplicates the packaged copy under `src/monetary_sfc/data/`;
- `displacement-risk-lab-dynamodb/reports/sample_run/raw/*` duplicates `data/raw/*`.

These are not central-registry migration candidates. Cleanup should happen only inside the owning project when it does not weaken offline reproducibility or packaging.

## Central source records added by this audit

This migration batch adds source records for:

- Our World in Data Grapher;
- FRED;
- Turing Change Point Dataset;
- UCDP;
- UNHCR Refugee Statistics;
- the public MIT-licensed maize Bipolaris disease-progress source.

The existing central records for World Bank, UCI Online Retail II and Berkeley Earth remain unchanged.

## Final migration set

### Canonical byte migrations

**None.**

No audited project contains a dataset that should be moved out of its owning repository into `datasets/` without reducing reproducibility, duplicating authoritative upstream data, or overstating redistribution rights.

### Source-registry migrations

The six source families above are centralized under `external/`.

### Keep-local

Synthetic fixtures, generated outputs, project-specific reference tables, reproducibility snapshots and packaged runtime resources remain in their current projects.

## Consequence for future repository work

New project repos should prefer:

1. authoritative upstream retrieval when practical;
2. a local immutable snapshot when offline reproducibility requires it;
3. provenance/checksum metadata in the project;
4. a central `external/` source record when the upstream dataset is reusable across projects.

The central `data` repository should not become a mirror of every project cache.
