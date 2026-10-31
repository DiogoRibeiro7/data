# M5 Forecasting Accuracy: retail demand benchmark

The [M5 Forecasting Accuracy competition](https://www.kaggle.com/competitions/m5-forecasting-accuracy)
used hierarchical daily Walmart unit-sales series for forecasting over a
28-day horizon. Its publisher is the M5 Competition hosted by the University
of Nicosia. The retail-data source provides item, department, category, store
and state identifiers, along with date, price and calendar information.

## Downstream consumer and file contract

[`perishable-inventory-decision-lab`](https://github.com/DiogoRibeiro7/perishable-inventory-decision-lab)
has an [M5 dataset card](https://github.com/DiogoRibeiro7/perishable-inventory-decision-lab/blob/main/docs/PUBLIC_RETAIL_DATASET_CARD.md)
and a [Python adapter](https://github.com/DiogoRibeiro7/perishable-inventory-decision-lab/blob/main/src/perishable_lab/data/public_retail.py).
The project deliberately downloads the data into a **local raw directory**.
These three files are required:

| Source file | Purpose | Boundary |
| --- | --- | --- |
| `calendar.csv` | Calendar dates, events and calendar covariates | Join only information available by each forecast origin. |
| `sales_train_validation.csv` | Daily item-store unit sales `d_1` through `d_1913` | Training source for rolling-origin evaluation. |
| `sell_prices.csv` | Item-store prices by Walmart week | Do not treat unavailable future prices as known. |

The competition also distributes `sales_train_evaluation.csv`, containing
additional observed sales through `d_1941`, and `sample_submission.csv`.
The consumer flags both files and post-training day columns as possible
**evaluation leakage**. Do not use them to fit or tune the validation
benchmark. Independently defined historical rolling-origin windows within
`d_1`–`d_1913` remain possible.

To acquire the three input CSV files, visit the
[official data page](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data),
sign in, accept the applicable competition rules and download the data
through Kaggle. Unpack the required files to a local directory such as
`data/raw/m5/` in the consumer repository. Its adapter supports optional
SHA-256 checks using `M5AdapterConfig.expected_checksums`.

The consumer documents this example command:

```bash
poetry run perishable-lab public-retail-benchmark data/raw/m5 --output-dir artifacts/public-retail-benchmark
```

## What the benchmark measures

The public sales observations can support out-of-sample **demand forecast**
evaluation using rolling-origin splits, quantile loss, coverage, interval
width and approximate CRPS. The consumer compares a seasonal baseline, an
intermittent-demand baseline and quantile gradient boosting.

The original M5 data **do not** provide observed shelf life, on-hand stock,
spoilage, waste, supplier lead times, shrinkage or procurement costs. The
consumer fills those interface fields synthetically. Therefore:

- Forecast metrics computed on the observed sales series are public-data
  benchmark results, subject to the sampling and horizon choices.
- Inventory policy, expiry and waste outcomes are **not** empirically
  validated merely because the sales inputs came from M5.
- Unit sales need not equal uncensored demand when stockouts are unobserved.
  Avoid claiming an observed no-sale day proves no customer demand.

The M5 competition's official evaluation uses a hierarchical weighted
RMSSE metric. The consumer's quantile-forecast metrics are a separate
benchmark, not an official M5 competition score.

## Rights, provenance and archival status

Kaggle lists the [data licence](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data)
as **"Subject to Competition Rules"** and requires users to accept the
rules to access the data. That access model does not establish an unrestricted
right to republish the CSV files in this registry. Permission for central
redistribution is **unresolved**; source files are intentionally absent.

Record the exact competition file versions, retrieval date and SHA-256
checksums inside the consumer's local research manifest. This external record
preserves the source and consumption contract, not the original observations
or any purported reproducibility of a download that was never executed here.
