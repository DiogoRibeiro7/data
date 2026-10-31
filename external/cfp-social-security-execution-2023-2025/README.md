# CFP Social Security execution and FEFSS transfers, 2023–2025

The [Conselho das Finanças Públicas (CFP)](https://www.cfp.pt/pt/publicacoes/sectores-das-administracoes-publicas/evolucao-orcamental-da-seguranca-social-e-da-cga-em-2025)
publishes annual reports on Portuguese Social Security execution alongside
the Excel data underlying its figures. The research consumer
`social-security-housing-investment` records three exact upstream workbooks in
`data/sources/cfp_reports.json`.

| Reporting year | CFP report | Source annex | SHA-256 of project-local XLSX | Annual adjusted surplus | FEFSS transfers received |
| --- | --- | --- | --- | ---: | ---: |
| 2023 | 06/2024 | [XLSX](https://www.cfp.pt/uploads/publicacoes_ficheiros/cfp-rel-06-2024-ds_final.xlsx) | `286cc589a5d479af7ab183ab349ea92d72fcc24ab25e553d07c195a000d5f0c0` | €5,485m | €4,558m |
| 2024 | 03/2025 | [XLSX](https://www.cfp.pt/uploads/publicacoes_ficheiros/cfp-rel-06-2024-ds.xlsx) | `972b8632a53681bcb6330cfeb3923a47be8e3e2892c36cee964df58a0499e4c6` | €5,595m | €4,132m |
| 2025 | 04/2026 | [XLSX](https://www.cfp.pt/uploads/publicacoes_ficheiros/cfp-rel-04-2026-ds.xlsx) | `d9f28e424ab62b807015ab5ff048063acd60cc474d5e078b1cad14d6236cba6d` | €6,657m | €4,534m |

Values are **observed annual adjusted budget balances** as reported in each
*own-year* workbook, in millions of euros. The 2024 comparison value in the
2025 workbook has a different adjustment basis; it must not silently replace
the 2024 own-year adjusted balance. Monthly balance series are **cumulative
year-to-date** observations. The 2025 FEFSS end-year asset figure (€41,947m)
is a **stock**, not a Social Security budget surplus or an investable cash flow.

Research snapshots were retrieved on 30 October 2026. The hashes above come
from the downstream manifest, not a fresh registry download. Data from these
workbooks do not establish that any surplus can legally be reallocated to
housing; policy and FEFSS rules require separate analysis.

The downloadable annexes are public, but no specific redistribution licence
was verified for these bytes. **External reference only; no files or CSV
extracts are copied into this registry.**
