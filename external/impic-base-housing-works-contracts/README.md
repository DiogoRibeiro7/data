# IMPIC Portal BASE public housing works contracts

The [Portal BASE](https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/),
maintained by IMPIC, provides public procurement records and signed contract
documents. The `social-security-housing-investment` research project records
**21 housing works contracts** selected for estimating observed procurement
costs, with one structured detail record and one signed PDF per contract.

## Project-local provenance

The downstream `data/sources/housing_cost_sources.json` manifest pins:

- 21 individual record URLs, detail JSON snapshots, SHA-256 hashes and sizes.
- 21 signed contract PDF URLs, SHA-256 hashes and sizes, with an indication of
  which PDFs have machine-readable text.
- A retrieval date of 30 October 2026 for this research collection.

For example, [contract 10927705](https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id=10927705)
has a project-local JSON SHA-256 of
`ff8b12c0aca4be416efc6123fbfcf8a85a3dc5b5861cbcda59684df4f2699d5a`;
the associated [signed contract PDF](https://www.base.gov.pt/Base4/pt/resultados/?type=doc_documentos&id=2172498&ext=.pdf)
has SHA-256
`838660c3519ae238ea81dd39f6aec672cd646a04e9180e31b07d695b8c28b1dd`.
These digests identify downstream files, not versioned upstream releases.

Contract price is **not** automatically final construction cost. Scope may
include design, land or other expenses; VAT treatment and gross construction
area require contract-level verification. The downstream research explicitly
checks units and qualifying contracts, and marks unreadable scanned terms
as not verified.

## Reuse distinction

IMPIC [documents public data extraction](https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/)
and also publishes a [bulk contracts dataset (2012–2026)](https://dados.gov.pt/pt/datasets/contratos-publicos-portal-base-impic-contratos-de-2012-a-2026/)
on dados.gov.pt with the licence designation **“Outra (Domínio Público)”**.
The latter label applies to its corresponding bulk open-data resource; it
cannot simply be transferred to every individual Portal BASE page, signed
contract, attachment, or third-party content.

This registry keeps the selected-contract collection **external-only**. A
candidate canonical *structured* subset would require record-level identity
checks against a pinned public-domain bulk export. No signed contract PDFs
or project-local JSON/CSV files are mirrored here.
