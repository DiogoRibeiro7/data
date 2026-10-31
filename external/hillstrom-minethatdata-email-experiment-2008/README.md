# Hillstrom MineThatData email experiment (2008)

Kevin Hillstrom published the [MineThatData E-Mail Analytics and Data Mining
Challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html)
on **20 March 2008**. The original author describes **64,000 customers**
with purchases in the preceding 12 months. A randomized email experiment
assigned roughly one-third to each arm:

| `segment` | Assigned communication |
| --- | --- |
| `Mens E-Mail` | Men's merchandise campaign |
| `Womens E-Mail` | Women's merchandise campaign |
| `No E-Mail` | Holdout control |

Customer features are `recency`, `history_segment`, `history`, `mens`,
`womens`, `zip_code`, `newbie` and `channel`. Outcomes during a **two-week**
follow-up are `visit`, `conversion` and `spend`. This is a historical
randomized marketing dataset, not a representative sample of all shoppers.

## Downstream contract

[`causal-uplift-marketing-campaign`](https://github.com/DiogoRibeiro7/causal-uplift-marketing-campaign)
documents and loads the same data from the Kaggle mirror
[`bofulee/kevin-hillstrom-minethatdata-e-mailanalytics`](https://www.kaggle.com/datasets/bofulee/kevin-hillstrom-minethatdata-e-mailanalytics).
Its loader expects the original filename:

`Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv`

The adapter can:

- Pool both email arms against control (`treated_arm="any"`): all 64,000
  customers, but **two distinct creative treatments** are combined.
- Compare only men's email with control or only women's email with control:
  exclude the third arm for a more specific treatment contrast.
- Evaluate the `conversion` or `visit` binary outcome, with `spend` left
  as a different outcome rather than silently substituted for conversion.

The consumer generates `customer_id` as a **sequential row index**. It is
not a persistent customer identifier provided by Hillstrom. Research
must not treat it as a linkage key across independently sorted copies.
An actual acquisition should record the precise mirror version, raw CSV
SHA-256, row counts, treatment-arm proportions and validation results.

## Rights and provenance

The original challenge post encourages download and research analysis,
but an express licence permitting *redistribution of the original CSV*
has not been established. The Kaggle copy is a third-party mirror;
its availability alone does not establish the original owner's
republication permission. **Redistribution remains unresolved.**

The central registry stores only the original source link and the
downstream acquisition contract; it does not copy the experiment rows.
