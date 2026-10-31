# Conta Geral do Estado: Social Security execution, 2013–2025 editions

Portugal's Ministry of Finance publishes [Conta Geral do Estado (CGE)](https://www.eo.gov.pt/politicaorcamental/Paginas/Conta-Geral-do-Estado.aspx)
tables as annual Excel files. The 13 edition years from **2013 through 2025**
provide execution observations with reference years **2012–2025**.

The research consumer `social-security-housing-investment` pins each edition,
official download URL, exact file size, SHA-256, worksheet, accounting unit,
and edition/reference-year mapping in
`data/sources/cge_social_security_accounts.json`.

Two examples of the upstream file identities:

| Edition | Official XLS/XLSX | Project-recorded SHA-256 | Accounting coverage |
| --- | --- | --- | --- |
| 2013 | [Quadros.xls](https://www.eo.gov.pt/politicaorcamental/ContaGeraldoEstado/2013/Quadros.xls) | `e6da45eb57e9f2b67130eba3a443dd0f85baf47677943f781b5935de0a498aad` | 2012 comparison and 2013 own-year |
| 2025 | [CGE2025_QuadrosGraficos.xlsx](https://www.eo.gov.pt/politicaorcamental/ContaGeraldoEstado/CGE2025_QuadrosGraficos.xlsx) | `559f7a0d32ffa4818ce83885cc1d6e7e1aa507b058d2c9f66bc125738f1df7c0` | 2024 comparison and 2025 own-year |

The Ministry's annual CGE execution tables and IGFSS's separately published
*Conta da Segurança Social* are related, **not interchangeable**. A
comparison-year figure in a later CGE edition is a different reporting
vintage; use the appropriate own-year account and document any revisions.
Amounts can have different units across releases and worksheets. Derived
model parameters, adjusted CFP balances, and 2026 forecasts are outside
this source family.

The example hashes are from research files retrieved on 30 October 2026;
they were not revalidated by this registry. **Metadata only.** No upstream
workbook or transcribed dataset is mirrored, because redistribution terms
for those files remain unresolved.
