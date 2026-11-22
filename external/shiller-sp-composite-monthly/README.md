# Shiller S&P Composite, monthly, from 1871

Robert Shiller's monthly series for the S&P Composite and its predecessors:
price, dividends, earnings, consumer price index and the cyclically adjusted
price-to-earnings ratio (CAPE), from January 1871. The originator publishes it
on his [Yale data page](http://www.econ.yale.edu/~shiller/data.htm); the
byte source pinned here is the Datahub mirror
[datasets/s-and-p-500](https://github.com/datasets/s-and-p-500).

## Pinned identity

| Field | Value |
| --- | --- |
| Repository | `datasets/s-and-p-500` |
| Commit | `87a2284276f79d75041c71c8f6d9f2aa1c965e84` |
| Path | `data/data.csv` |
| SHA-256 | `b797a3c8de4586af837b86a156b05f49be11ffab99e13171dae763b2a11bdf79` |

## Licence

The mirror's `datapackage.json` declares ODC-PDDL-1.0. Shiller publishes the
underlying data without an explicit licence, so treat the declaration as the
mirror's and cite Shiller. No bytes are mirrored in this registry.

## Coverage notes

At the pinned commit, earnings and dividends end in June 2023 and CPI in
September 2023; later rows carry the price only. CAPE is written as 0, not
missing, for the first ten years.

## Consumers

- `medium-blog/growth-finite-world`: `DiogoRibeiro7/Medium-Blog`, folder
  `growth-finite-world`, fetched and checked by `fetch_data.py`.
