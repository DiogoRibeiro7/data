# OECD Global Pension Statistics: asset-backed pension investment and private-equity allocation

Asset-backed pension investment (measure 1000) as a percentage of GDP, all plan types and vehicles, and private-equity funds (measure 1286) as a percentage of pension-fund assets, all reporting countries.

## Pinned identity

Retrieved on 24 November 2026. The consumer checks each response against the SHA-256 below and stops if the publisher has revised it.

| File | Dataflow | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `pensions.csv` | `DSD_FP@DF_FPS` | 370,270 | `0dc315320409fa873c18d7b097e4ee1b305650274d930dab083c3f17763dc01d` |

Requests:

- `pensions.csv`: <https://sdmx.oecd.org/public/rest/data/OECD.DAF.CM,DSD_FP@DF_FPS,1.0/.A.1000+1286.PT_B1GQ+PT_AS._T._T._T+PF?format=csvfile>

The OECD endpoint refuses Python's default user-agent string; the consumer sends its own.

## Licence

OECD Terms and Conditions (verify any third-party or series-specific rights). No bytes are mirrored in this registry.

## Consumers

- `medium-blog/uk-innovation-ownership`: `DiogoRibeiro7/Medium-Blog`, folder `uk-innovation-ownership`, fetched and checked by `fetch_data.py`.
