# Online Retail II

Canonical snapshot of the UCI Machine Learning Repository **Online Retail II** dataset.

## Source

- Publisher: UCI Machine Learning Repository
- Creator: Daqing Chen
- UCI dataset ID: 502
- DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D)
- Source page: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Retrieved: 2026-10-01
- Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Coverage

The dataset contains **1,067,371 transactions** from a UK-based,
registered, non-store online retailer between **1 December 2009**
and **9 December 2011**.

UCI describes eight fields:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

Missing values are present in the source data.

## Canonical file

`raw/online_retail_II.xlsx` is the authoritative UCI workbook downloaded
from the dataset-502 download endpoint. It is stored without transformation.

The exact SHA-256 is recorded in `metadata.yaml`.

Because the workbook exceeds 25 MiB, its direct-Git storage was reviewed
explicitly under the repository large-file policy.

## Citation

> Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository.
> https://doi.org/10.24432/C5CG6D

This registry snapshot does not replace the upstream citation or attribution
requirement.
