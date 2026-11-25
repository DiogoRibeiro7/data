# Our World in Data: CO2 and greenhouse gas emissions

A pinned file from the [our-world-in-data](../our-world-in-data/) access layer:
[owid/co2-data](https://github.com/owid/co2-data).

## Pinned identity

| Field | Value |
| --- | --- |
| Repository | `owid/co2-data` |
| Commit | `22d9a01321ddec951b36f2bfc66e05dc6ad50ad8` |
| Path | `owid-co2-data.csv` |
| SHA-256 | `300fb68fe6b0d514ed7f5cf773df77d7e24a495438d84b76e2f39eba1584a0f7` |

## Licence

OWID-produced data are CC BY 4.0. Third-party series keep their providers'
terms. The columns used downstream are third-party:

- territorial and consumption-based CO2: Global Carbon Budget (2026);
- GDP: Maddison Project Database 2023, with the citation rules recorded in
  [maddison-project-database-2023](../maddison-project-database-2023/);
- population: OWID's compilation from various sources (2024).

World GDP is given only for Maddison benchmark years before 2015.

## Consumers

- `medium-blog/growth-finite-world`: `DiogoRibeiro7/Medium-Blog`, folder
  `growth-finite-world`, fetched and checked by `fetch_data.py`.
- `medium-blog/estado-novo-legacy`: `DiogoRibeiro7/Medium-Blog`, folder
  `estado-novo-legacy`, contract `data_sources/owid-co2-data.json`, fetched
  and checked by `fetch.py`; reads `iso_code`, `year`, `gdp` and `population`.
