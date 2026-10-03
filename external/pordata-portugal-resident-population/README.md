# Portugal resident population estimates by age group

External-source record for the PORDATA series **População residente, estimativas
a 31 de dezembro: total e por grupo etário**.

## Source

- Publisher/interface: PORDATA, Fundação Francisco Manuel dos Santos
- Statistical source: Instituto Nacional de Estatística (INE)
- Series: annual resident-population estimates at 31 December, total and
  five-year age groups
- PORDATA source page:
  https://www.pordata.pt/Portugal/Populacao%2Bresidente%2B%2Bestimativas%2Ba%2B31%2Bde%2BDezembro%2Btotal%2Be%2Bpor%2Bgrupo%2Betario-7

The live PORDATA table exposes the same age-group schema as the removed legacy
workbook: total, `0-04`, `05-09`, ..., `80-84`, and `85 ou mais`.

## Legacy workbook attribution

The former `legacy/portugal-population-2018/raw/populacao_residente_2018.xlsx`
contained annual rows through 2018 using exactly that schema.

The 2018 row totals **10,276,617**, with age-band values matching published
2018 INE population estimates.

Office metadata records `OutSystemsApplications` as the workbook creator and
a creation timestamp of 2020-05-14. PORDATA documents OutSystems as part of its
technology stack and provides Excel export from the matching table. Taken
together, these facts strongly identify the historical workbook as a PORDATA
export of the INE-backed series.

## Why the bytes are not stored

The local workbook is an application-generated export, not an immutable
publisher artifact. No maintained repository consumes it.

PORDATA and INE revise historical population estimates over time, so the live
series may no longer reproduce every historical value from the 2020 export.

The registry therefore records the reusable public source and removes the local
Excel copy.

## Redistribution

Redistribution is recorded as **unresolved**.

The current PORDATA site is copyrighted by Fundação Francisco Manuel dos Santos,
and the registry has not recovered terms that clearly authorize mirroring the
historical Excel export bytes. Consumers should retrieve data from the source
and observe the applicable source terms.
