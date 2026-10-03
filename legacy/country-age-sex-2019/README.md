# Country age/sex population snapshots (2019)

> **Resolution:** retained in legacy quarantine after re-audit on 2026-10-03.

These historical male/female population snapshots are strongly consistent with
the **United Nations World Population Prospects 2019 Revision**, but the exact
download/export route for the retained files is still not proven.

## Evidence recovered

Most country CSV files use 5-year age bands from `0-4` through `100+` with
male/female counts, matching the structure of UN WPP age/sex population data.

The strongest recovered evidence is Portugal:

- `Portugal-2019_1.csv` sums to **10,226,178** residents;
- WHO material that explicitly cites **UN population prospects, 2019** reports
  Portugal's 2019 population as **10,226,178**;
- the current PopulationPyramid.net Portugal 2019 page instead reports
  **10,343,213** and states that it uses the **WPP 2024 revision**.

This confirms that the retained 5-year Portugal snapshot belongs to an older UN
WPP revision and is consistent with WPP 2019 rather than the current WPP 2024
series.

The United Nations WPP 2019 publication confirms that detailed results were
distributed as Excel/ASCII downloads and through the WPP data-query system.

## Portugal variants

The package contains three Portugal artifacts:

- `Portugal-2019_1.csv`: 5-year age bands, total 10,226,178;
- `Portugal-2019.csv`: manually aggregated 10-year-style bands;
- `Portugal-2019.xlsx`: workbook whose exact relationship to the CSV files is
  still not established.

The aggregated CSV is very close to the 5-year file grouped into broader bands,
but at least two values differ slightly. It therefore must not be treated as a
lossless derivative without further evidence.

## Consumer search

Account-wide code search for the distinctive filenames found no maintained
consumer outside this repository.

## Licensing

UN WPP 2019 publications are made available under **CC BY 3.0 IGO**, but the
registry does not yet have enough evidence that these exact retained CSV/XLSX
files were downloaded directly from an authoritative UN endpoint rather than
through an intermediary/export service.

Because exact file provenance is not established, the package is not promoted
or externalized solely on the basis of the likely source family.

## Remaining blockers

- exact original download/export route for the retained files is not proven;
- exact relationship of the Portugal workbook to the two CSV variants remains
  unresolved;
- the broader-band Portugal CSV appears to contain small discrepancies from a
  direct aggregation of the 5-year file;
- file-level redistribution evidence for these exact historical artifacts is
  therefore not strong enough for canonical promotion.

## Decision

**Retain in legacy quarantine.**

The re-audit materially strengthens the source attribution to UN WPP 2019, but
does not meet the registry's standard for canonical or external replacement.

See [the phase-four re-audit](../../docs/migrations/LEGACY_REAUDIT_2026-10-03.md).
