# Consumer migration audit

## Result

No consuming repository currently depends on a canonical dataset from `DiogoRibeiro7/data`.

The canonical catalog contains zero datasets. Account-wide searches for exact raw-content or repository-path references found no consumer dependency. Broader repository-name searches returned prefix matches such as `DataExcept` and `DataConsistencyChecker`; these are not consumers.

## Action taken

Because there is nothing to migrate yet, issue #7 establishes the consumer contract instead of modifying unrelated projects:

- exact Git commit pinning;
- canonical repository path;
- expected SHA-256;
- deterministic atomic fetch helper;
- local-fixture and offline policy;
- removal checklist for future duplicated copies.

## Deferred work

When a dataset is first promoted under `datasets/<slug>/`, create a consumer-specific migration issue or pull request that:

1. identifies every current copy;
2. pins the canonical commit and checksum;
3. updates code, notebooks and documentation;
4. preserves small local test fixtures;
5. verifies the consuming repository before deleting redundant data.
