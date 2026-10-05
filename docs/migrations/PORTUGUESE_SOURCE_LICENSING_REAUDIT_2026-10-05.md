# Portuguese public-source licensing re-audit — 2026-10-05

This Phase 6 audit covers:

- `dgs-infoclique-mortality`;
- `pordata-portugal-resident-population`.

## DGS InfoClique / SICO mortality

### Decision

**Redistribution remains unresolved; blocker classified terminal.**

DGS publicly disseminates mortality information through its online services and
SICO. However, the current DGS legal notice protects site content, and no
dataset-specific licence or reuse statement was recovered that clearly covers
redistribution of the historical InfoClique/SICO CSV export family.

Public access therefore does not establish permission to mirror the historical
export bytes.

Evidence:

- https://www.dgs.pt/site/notas-legais.aspx
- https://www.dgs.pt/servicos-on-line1/sico-sistema-de-informacao-dos-certificados-de-obito.aspx

Registry classification:

- review status: `terminal`;
- blocker: `redistribution-rights`;
- review date: `2026-10-05`;
- reopen condition: new authoritative DGS dataset-specific reuse terms.

## PORDATA resident population

### Decision

**Redistribution remains unresolved; blocker classified terminal.**

INE permits rediffusion of official statistical information with source
attribution. The historical registry artifact, however, was a
PORDATA-generated Excel export rather than a directly sourced INE object.

The INE reuse rule therefore does not automatically establish redistribution
rights for PORDATA's secondary-source serialization. No authoritative
PORDATA/FFMS term was recovered that clearly permits mirroring the historical
Excel bytes.

Evidence:

- https://www.ine.pt/ine_novidades/CSE_2017/105/
- https://www.pordata.pt/About.aspx
- https://www.pordata.pt/Portugal/Populacao%2Bresidente%2B%2Bestimativas%2Ba%2B31%2Bde%2BDezembro%2Btotal%2Be%2Bpor%2Bgrupo%2Betario-7

Registry classification:

- review status: `terminal`;
- blocker: `redistribution-rights`;
- review date: `2026-10-05`;
- reopen condition: explicit PORDATA/FFMS redistribution terms, or replacement
  with a directly sourced INE representation governed by INE reuse terms.

## Debt impact

Before this audit:

- structured debt items: **1**;
- terminal debt items: **1**;
- unstructured debt items: **5**.

After this audit:

- structured debt items: **3**;
- terminal debt items: **3**;
- unstructured debt items: **3**.

The total debt count remains **6** because neither historical export is promoted
or removed by this audit.
