# Portugal COVID-19 MTSSS monitoring workbook

> **Resolution:** retain the official-looking MTSSS workbook in legacy quarantine; remove the unrelated derived ARS model-output table.

## Evidence recovered

`Monitorizacao_COVID-19_MTSSS_27_maio_2020.xlsx` belongs to the 2020
**Indicadores COVID-19 MTSSS** monitoring-workbook series published by the
Gabinete de Estratégia e Planeamento (GEP) of the Portuguese Ministry of
Labour, Solidarity and Social Security.

Contemporary GEP material describes this series as a regularly updated set of
labour-market and social-support indicators based on sources such as Segurança
Social, IEFP and DGERT. Independent publications cite the same GEP series by
date-specific monitoring snapshots.

The filename identifies this retained workbook as the **27 May 2020** snapshot.

## Removed derived file

`Portugal_ARS.csv` was a regional model-output table with columns
`ML`, `Low_90`, `High_90`, `Low_50`, and `High_50`.

Its values are statistical estimates and interval bounds rather than raw
administrative observations. Account-wide code search found no maintained
consumer and no generating code or upstream source was recovered.

It has therefore been removed rather than preserved as raw legacy data.

## Remaining blockers

The MTSSS workbook stays in legacy because:

- the exact historical workbook download URL is not pinned;
- dataset-specific redistribution terms for the 2020 workbook have not been
  established;
- no immutable upstream identifier is available.

The source family is strong enough to retain the workbook with attribution, but
not strong enough for canonical promotion or byte mirroring.

See [the phase-four re-audit](../../docs/migrations/LEGACY_REAUDIT_2026-10-03.md).
