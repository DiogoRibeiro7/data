# IBM Telco Customer Churn sample

Source record for the IBM sample customer-churn dataset formerly stored under `legacy/telco-customer-churn/`.

## Source

- Publisher: IBM
- Archived repository: https://github.com/IBM/telco-customer-churn-on-icp4d
- Pinned repository commit: `d5371f5d83a446ad5673cbcca3b814b926491f8a`
- Source path: `data/Telco-Customer-Churn.csv`

The legacy local file contained 7,043 customer rows and the same 21-column schema as the IBM sample.

A byte comparison showed that the retained local file was not byte-identical to IBM's archived CSV only because of line endings: after normalizing CRLF/CR to LF, the contents are identical.

## Licensing note

The archived IBM code-pattern repository is Apache-2.0 licensed, but its README explicitly distinguishes separately licensed third-party objects. A dataset-specific redistribution grant for this sample was not established during the audit.

For that reason the external record leaves dataset redistribution status as unresolved and does not claim the repository's software licence applies automatically to the data.

No current consumer of the legacy filename was found, so the redundant local serialization was removed.
