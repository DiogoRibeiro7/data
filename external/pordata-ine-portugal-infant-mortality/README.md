# INE/PORDATA Portugal infant mortality, 1960 onward

The [PORDATA infant mortality indicator](https://www.pordata.pt/en/portugal/infant%2Bmortality%2Brate-528)
reproduces annual statistics sourced from Portugal's Instituto Nacional de
Estatística (INE). Its unit is **deaths of live-born children under one year
per 1,000 live births** in the reference period, not deaths per population.

The `portugal-living-standards-reassessment` project currently records three
manually transcribed official observations in
`data/external/infant_mortality_landmarks.csv`:

| Year | Deaths under one per 1,000 live births |
| --- | ---: |
| 1960 | 77.5 |
| 1974 | 37.9 |
| 1990 | 10.9 |

The source was checked on **31 October 2026**. The PORDATA table was last
updated **5 August 2026** and now covers 1960–2025. These three points
**cannot identify a pre/post-1974 trend break** or any policy effect.

## Published comparability warnings

- The source flags **1980 as a series break**. In 1960–1979, the source's
  birth and death counts included events irrespective of the relevant
  mother's/deceased person's residence, because foreign and unknown
  residence could not be separated. From 1980, it excludes residents abroad
  and includes events with unknown residence. This alters the measured
  population underlying the rate.
- The source also marks **2021 as a series break**. Do not assume the
  1980 and 2021 markers have the same reason; obtain the specific metadata
  and any methodology notes before fitting long-run change-point models.
- According to PORDATA, INE revised the 2021–2024 figures in June 2026.
  Preserve a dated source version if later revisions change the table.

Read the publisher's [indicator metadata](https://www.pordata.pt/en/MetaInfoPage_Temp_Popup.aspx?DatabaseModeId=1&ExpandMeta=True&GeographicGroupId_Level1=1075&LanguageId=2&MicroIDs=528&ShowLinkAdditionalNotes=True&ShowPrinterIcon=True&WorkMicroVersionId=0)
and [symbol legend](https://www.pordata.pt/en/Simbology_PopUp.aspx?DatabaseModeId=1).

The three downstream points are **registered events**, unlike modeled
World Bank/UN IGME mortality estimates. Do not splice these series or
interpret a change in definition as a political treatment effect.

## Rights and status

PORDATA is a secondary distributor of INE statistics. Its open webpage
does not itself grant a clearly documented licence to mirror the complete
export file or republish its compilation in this registry. Rights for
that artifact remain **unresolved**. This entry is metadata only; no
historical PORDATA workbook or CSV is copied into `data`.
