# Registry quality and coverage

The registry publishes a deterministic quality and coverage report derived only
from committed repository state.

The report is intended to answer a simple question: **how much of the registry
is currently resolved, verifiable, and reusable?**

## Outputs

- [Human-readable report](generated/registry-quality.md)
- `reports/registry-quality.json` for machine-readable use

Generate the reports with:

```bash
python scripts/registry_quality.py --write
```

Verify that committed reports are current with:

```bash
python scripts/registry_quality.py
```

## Metrics

The report covers:

- canonical dataset and file counts;
- canonical SHA-256 verification coverage;
- canonical licence-metadata completeness;
- external-source count;
- resolved versus unresolved redistribution status;
- sources pinned to exact Git commits;
- known downstream consumers;
- unresolved legacy-quarantine packages;
- canonical and external generated-catalog freshness.

## Unresolved is not invalid

External records may deliberately use an unresolved redistribution state.

That means the repository has enough provenance to identify the source but not
enough evidence to claim redistribution rights. The quality report keeps this
separate from schema or integrity failures.

## Snapshot count

The report does not count GitHub releases or tags.

Those values depend on remote Git state and checkout depth, so including them
would make the generated report environment-dependent. Snapshot material
remains covered by the separate immutable-release workflow.
