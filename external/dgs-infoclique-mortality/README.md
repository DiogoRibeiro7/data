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

All six use the same schema of daily counts by nature-of-death category:

- road accident;
- work accident;
- possible suicide;
- possible homicide;
- other accident;
- unknown.

The 2015-2019 files contain complete calendar years. The 2020 file is a partial
year snapshot and ends on 10 June 2020.

The filenames share the snapshot marker `2020-05-31`, indicating one
historical export family rather than six unrelated datasets.

## Why the CSV bytes are not stored

No maintained repository consumes these files.

The exact historical export endpoint and export procedure were not recovered,
and the current DGS site states that its content is all rights reserved.

The registry therefore records the authoritative public mortality platform but
does not mirror the historical CSV exports.

## Redistribution

Redistribution is **unresolved**.

Consumers should retrieve current information from DGS and comply with the
terms applicable to the source platform.
