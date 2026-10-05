# DGS InfoClique mortality platform

External-source record for Portugal's public mortality platform maintained by
the Direção-Geral da Saúde (DGS).

## Source

The DGS services page exposes **DGS InfoClique - Plataforma da Mortalidade**
alongside SICO, the **Sistema de Informação dos Certificados de Óbito**.

DGS documentation identifies SICO as a source for mortality surveillance and
statistical treatment of causes of death.

Source page:

https://www.dgs.pt/servicos-on-line1.aspx

## Legacy snapshot family

The removed legacy package contained six CSV files named:

- `Dados_SICO_2020-05-31_2015.csv`
- `Dados_SICO_2020-05-31_2016.csv`
- `Dados_SICO_2020-05-31_2017.csv`
- `Dados_SICO_2020-05-31_2018.csv`
- `Dados_SICO_2020-05-31_2019.csv`
- `Dados_SICO_2020-05-31_2020.csv`

All six use the same schema of daily counts by nature-of-death category.

## Redistribution decision — terminal unresolved

The mortality information is publicly disseminated, but public accessibility is
not itself a redistribution licence.

The current DGS legal notice protects site contents and the re-audit did not
recover dataset-specific reuse terms that clearly authorize mirroring the
historical InfoClique/SICO CSV export family.

Evidence:

- https://www.dgs.pt/site/notas-legais.aspx
- https://www.dgs.pt/servicos-on-line1/sico-sistema-de-informacao-dos-certificados-de-obito.aspx

The registry therefore keeps:

`redistribution: unresolved`

and classifies the blocker as **terminal redistribution-rights**.

No historical CSV bytes are mirrored. Reopen this decision only if DGS
publishes dataset-specific reuse terms or an authoritative open-data licence
covering the historical exports.
