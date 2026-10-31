# Criteo Uplift Prediction Dataset

The [Criteo AI Lab Uplift Prediction Dataset](https://ailab.criteo.com/criteo-uplift-prediction-dataset/)
was published with *A Large Scale Benchmark for Uplift Modeling*
(Diemert, Betlei, Renaudin & Amini, AdKDD 2018). Its anonymized
experiments were designed for uplift and heterogeneous-treatment-effect
benchmarking.

## Identify the exact version

Do not confuse different published Criteo distributions:

| Source | Size reported by publisher | Version / evidence |
| --- | ---: | --- |
| [Original Criteo AI Lab page](https://ailab.criteo.com/criteo-uplift-prediction-dataset/) | 25,309,483 rows | 2018 research release, with a described 25M-row dataset |
| [First-party Criteo Hugging Face repository](https://huggingface.co/datasets/criteo/criteo-uplift) | 13,979,592 rows | Later `criteo-research-uplift-v2.1.csv.gz` distribution |

The source versions must **not** be treated as identical data exports.
Different subsamples can alter treatment rates and uplift estimates.
Record the final URL, exact archive filename, raw SHA-256, row count,
column set, and acquisition date before using a benchmark result.

Typical columns include anonymized numeric features `f0`–`f11`,
`treatment` (assignment), `exposure` (effective ad exposure), and the
binary `visit` and `conversion` outcomes. **Assignment is not the same
variable as actual exposure.** Criteo states that it nonuniformly
subsampled the data for privacy, so original experiment-wide causal
incrementality cannot be recovered naively from benchmark rates.

## Downstream acquisition

[`causal-uplift-marketing-campaign`](https://github.com/DiogoRibeiro7/causal-uplift-marketing-campaign)
offers an optional `--source criteo` direct-URL download. Its configured
default is `https://storage.googleapis.com/criteo-uplift-v2.1/criteo-uplift-v2.1.csv.gz`;
that exact endpoint and its correspondence to the v2.1 first-party
Hugging Face file have **not been independently verified**. The default
real-data path is Hillstrom, and CI uses synthetic data. This record
must not be used as evidence that a Criteo dataset was successfully fetched
or benchmarked in the project.

## Licence

Criteo's [original dataset terms](https://ailab.criteo.com/criteo-uplift-prediction-dataset/)
explicitly apply **Creative Commons Attribution–NonCommercial–ShareAlike
4.0**. Reuse requires attribution, restricts covered redistribution to
noncommercial purposes and applies a ShareAlike obligation to adaptations.
The publisher also asks users to cite the 2018 benchmark paper. The
research code's Apache software licence does **not** override dataset
restrictions.

This central registry keeps an external reference only, with no copied
Criteo observations or transformed source rows.
