# IBM Telco Customer Churn sample

Source record for the IBM sample customer-churn dataset formerly stored under
`legacy/telco-customer-churn/`.

## Source

- Publisher: IBM
- Archived repository: https://github.com/IBM/telco-customer-churn-on-icp4d
- Pinned repository commit: `d5371f5d83a446ad5673cbcca3b814b926491f8a`
- Source path: `data/Telco-Customer-Churn.csv`

The legacy local file contained 7,043 customer rows and the same 21-column
schema as the IBM sample.

A byte comparison showed that the retained local file differed from IBM's
archived CSV only by line endings: after normalizing CRLF/CR to LF, the
contents are identical.

## Licensing decision — terminal unresolved

The exact pinned IBM repository contains an Apache-2.0 `LICENSE`, but the
repository README describes that licence as applying to the **code pattern** and
explicitly states that separately licensed third-party objects remain under
their respective providers' licences.

The repository includes `data/Telco-Customer-Churn.csv`, but no
dataset-specific licence or redistribution grant for that CSV was recovered.

IBM issue #22, opened specifically to ask whether the provided data is Apache
2.0 or otherwise freely licensed, remains unanswered.

Evidence:

- https://github.com/IBM/telco-customer-churn-on-icp4d/blob/d5371f5d83a446ad5673cbcca3b814b926491f8a/README.md
- https://github.com/IBM/telco-customer-churn-on-icp4d/blob/d5371f5d83a446ad5673cbcca3b814b926491f8a/LICENSE
- https://github.com/IBM/telco-customer-churn-on-icp4d/issues/22

The registry therefore keeps:

`redistribution: unresolved`

and classifies the blocker as **terminal
dataset-vs-repository-licence-scope**.

The record should only be reopened if IBM publishes new dataset-specific
licensing evidence.

No current consumer of the legacy filename was found, so the redundant local
serialization remains removed.
