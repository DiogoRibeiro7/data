# Eurostat employed persons by NUTS 2 region, Portugal

Eurostat's regional labour-market statistics give the number of employed persons by NUTS 2 region from the Labour Force Survey. This record pins one response, for Portugal and the two NUTS 2 regions of the Lisbon metro area, used by one consumer to set jobs against metro ridership.

## Consumer contract

`Medium-Blog/lisbon-metro-ridership` downloads the response with `fetch.py` and checks it against the SHA-256 recorded in `metadata.yaml` and in the consumer's `data_sources/eurostat-regional-employment-pt.json`. Retrieved on 26 November 2026.

| Dataset | Query | Content |
| --- | --- | --- |
| `lfst_r_lfe2emp` | `geo=PT, PT1A, PT1B; sex=T; age=Y15-74; from 2019` | Employed persons aged 15–74, thousands, annual |

## Why a byte hash

Eurostat serves identical bytes for identical data, so the pin is the SHA-256 of the response. An update changes the hash and the consumer stops unless it is run with `--accept-revision`.

## Things a consumer has to handle

- **Regions** follow the 2024 NUTS: `PT1A` is Grande Lisboa and `PT1B` the Península de Setúbal, which together are the Lisbon metro area (`PT17` in the 2021 NUTS).
- **Labour Force Survey** figures count people by place of residence, not by place of work.

## Reuse and registry decision

Eurostat data may be reused under the Commission's [reuse policy](https://ec.europa.eu/eurostat/help/copyright-notice) (Decision 2011/833/EU), with acknowledgement of the source.

**Metadata-only external record.** Eurostat remains the byte source; no responses are mirrored here or in Medium-Blog.
