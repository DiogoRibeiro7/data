# S&P CoreLogic Case-Shiller home price indices, national and 20 metropolitan areas, monthly, Datahub mirror

External reference, no bytes stored. Publisher: S&P Dow Jones Indices and CoreLogic; mirrored by Datahub as datasets/house-prices-us. Source: https://github.com/datasets/house-prices-us.

The Datahub package declares ODC-PDDL-1.0 for its packaging and names FRED's release tables of the S&P CoreLogic Case-Shiller indices as its source. The indices are a trademarked, copyrighted S&P Dow Jones Indices product, so the PDDL declaration is treated as the mirror's statement, not the originator's grant, and no bytes are kept here. The consumer downloads the two files from the pinned mirror commit and checks their SHA-256. Not seasonally adjusted levels, January 2000 = 100; the mirror writes 0.000 for months before a city's series starts (Atlanta 1987-1990), which the consumer treats as missing. Cite S&P CoreLogic Case-Shiller Home Price Indices.

## Files the consumer verifies

| File | Bytes | SHA-256 | URL |
| --- | ---: | --- | --- |
| `raw/cities-month-NSA.csv` | 86,315 | `6008236a64acf943e008d76c46cd183caee453ad8b859f2a666627fea95a5f86` | https://raw.githubusercontent.com/datasets/house-prices-us/eec55f4eb350a9bfbf4fc83d2489a42f9cbc66e0/data/cities-month-NSA.csv |
| `raw/national-month.csv` | 16,145 | `018008c5fe6e0297a735c2a37f7fa57a3e26aeed458d3cff35b885a437575c63` | https://raw.githubusercontent.com/datasets/house-prices-us/eec55f4eb350a9bfbf4fc83d2489a42f9cbc66e0/data/national-month.csv |

Consumer: `DiogoRibeiro7/Medium-Blog`, folder `rent-or-buy-us`, contract `data_sources/sp-corelogic-case-shiller-datahub.json`.
