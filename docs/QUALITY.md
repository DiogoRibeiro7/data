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
- external-source usage annotations;
- active canonical consumer repositories and relationships;
- canonical dataset adoption coverage;
- pinned canonical consumer-contract coverage;
- deprecated consumer relationships;
- canonical expansion relative to the committed Phase 7 baseline;
- datasets added since the baseline with/without active consumers;
- explicit adoption exemptions with rationale;
- unresolved legacy-quarantine packages;
- canonical, external, and consumer generated-catalog freshness.

## Consumer coverage

Canonical consumer adoption is calculated only from formal
`consumers/<consumer-id>/<dataset-id>.yaml` records.

The report keeps these metrics separate from `consumers` annotations that may
still exist on external-source records. Those annotations describe source usage;
they are not reproducibility contracts for canonical registry files.

For active canonical relationships, the report measures:

- distinct downstream repositories from `consumer_repository`;
- relationship count;
- exact pin/checksum contract coverage;
- canonical datasets with at least one active consumer;
- canonical datasets with no active consumer;
- deprecated relationships retained for traceability.

## Provenance and licensing debt

The registry also publishes a deterministic unresolved-debt queue:

- [human-readable debt queue](generated/provenance-debt.md);
- `reports/provenance-debt.json` for machine-readable use.

Generate or verify it with:

```bash
python scripts/generate_provenance_debt.py --write
python scripts/generate_provenance_debt.py
```

The debt queue is derived only from committed external and legacy metadata. It
keeps unstructured unresolved records visible while Phase 6 migrates them to the
structured `resolution` model.

Age is deliberately content-based rather than wall-clock based: when structured
review dates exist, the latest committed `last_reviewed` date is the reference
point. This keeps the generated report byte-deterministic across machines and
reruns.

The main registry quality report now incorporates the debt queue and reports:

- actionable and terminal external debt;
- actionable and terminal legacy debt;
- counts by blocker category;
- oldest committed review date;
- oldest deterministic debt age.

The local registry CLI exposes the same committed debt state through `debt`
and `debt-show` queries.

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


## Canonical expansion safeguards

Phase 7 adds a committed adoption policy at
`reports/canonical-adoption-policy.json`.

The policy records:

- the immutable baseline snapshot used for deterministic expansion metrics;
- the canonical dataset IDs present at that baseline;
- optional adoption exemptions, each requiring a dataset ID and non-empty
  rationale.

The current baseline is `snapshot-2026.10.05`, which contained
`online-retail-ii` and `ucdp-ged-25-1`.

Quality generation now fails when:

1. an active consumer relationship does not match a canonical path and SHA-256;
2. a canonical dataset has no active consumer and no documented exemption.

The current Phase 7 state has two additions since the baseline:
`ons-gross-median-weekly-pay` and
`unhcr-refugee-population-2024`. Both have active consumers, so the exemption
list is empty.

This policy is committed repository state and therefore remains offline and
deterministic. It does not inspect GitHub releases or account-wide repositories
during ordinary validation.
