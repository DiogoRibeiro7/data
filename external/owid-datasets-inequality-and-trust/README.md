# Our World in Data datasets repository at one commit: WID pre-tax income distribution, World Wealth and Income Database top income shares (2018) and GSS interpersonal trust

External reference, no bytes stored. Publisher: Our World in Data (repository owid/owid-datasets); underlying data from the World Inequality Lab (WID.world) and NORC at the University of Chicago (General Social Survey). Source: https://github.com/owid/owid-datasets at commit `6155d4ca1ea14ef30e753010a25521eeb416e8a2` (14 April 2025; the repository is archived).

Three CSV files are read at that commit, so that a Git commit fixes the bytes:

1. **World Inequality Database (WID) - Pretax income.** WID distributional national accounts, pre-tax national income, equal-split adults. The consumer uses `P99-P100 - share of the top 1%` (per cent) for the United States, the United Kingdom and eleven continental and Nordic countries, 1960-2017. European pre-1980 values come partly from fiscal data and alternate-year observations in WID; missing years stay missing in the file.
2. **Top income shares - World Wealth and Income Database (2018).** The older fiscal-income top 1% shares, stored as fractions of one although the column is named "Pre-tax national income". Used only as a check on the first file.
3. **Interpersonal Trust - General Social Survey (GSS).** Share of American adults answering that most people can be trusted, 1972-2018.

Cite WID.world (World Inequality Lab), the World Wealth and Income Database, NORC's General Social Survey, and Our World in Data.

## Files the consumer verifies

| File | Bytes | SHA-256 | Upstream file |
| --- | ---: | --- | --- |
| `external/wid_pretax.csv` | 4,353,642 | `891d8c7bb7034d00b6d2941075d4a61200f10b31d7ce845f0b3a9fc83b1f3af7` | `datasets/World Inequality Database (WID) - Pretax income/World Inequality Database (WID) - Pretax income.csv` |
| `external/wwid_top_fiscal.csv` | 50,165 | `2c8f7748341c18a3796d4ce13b00b7fe868382f52d2016226e0834eca7317b76` | `datasets/Top income shares – World Wealth and Income Database (2018)/Top income shares – World Wealth and Income Database (2018).csv` |
| `external/gss_trust.csv` | 736 | `3ff0b3a41f774cf90437d289f5b4dc8aee47f8de37f8ffb0763a71d32542343c` | `datasets/Interpersonal Trust - General Social Survey (GSS)/Interpersonal Trust - General Social Survey (GSS).csv` |

Raw URLs (percent-encoded) are in `metadata.yaml`.

Consumer: `DiogoRibeiro7/Medium-Blog`, folder `social-contract-break-dates`, contract `data_sources/owid-datasets-inequality-and-trust.json`.

## Reuse

Our World in Data releases its own work under CC BY 4.0; third-party series keep their providers' terms. The WID.world and NORC terms for mirroring were not reviewed, so the bytes stay upstream (see the `resolution` block).
