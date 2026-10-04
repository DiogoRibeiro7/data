# Consumer contract health and drift checks

Canonical consumer records are immutable dependency claims, but downstream
repositories and evidence links can still change over time.

The repository therefore provides a networked health checker:

```bash
python scripts/check_consumer_contracts.py \
  --json-report consumer-health/report.json \
  --markdown-report consumer-health/report.md
```

The checker runs only for **active** consumer relationships. Deprecated records
are historical traceability records and are not polled.

## What is checked

For each active consumer relationship, when present:

- downstream GitHub repository reachability;
- pinned downstream `consumer_commit` reachability;
- migration/evidence URL reachability;
- exact canonical registry commit + file path reachability.

The last check uses the immutable registry commit and canonical path from the
consumer record. Baseline repository validation separately verifies that the
recorded path and SHA-256 agree with committed canonical metadata.

The current consumer schema does not record a downstream manifest/source-code
path, so this checker does not scrape arbitrary downstream files looking for
the commit or checksum text. When a future schema records such a path, the
health checker can verify it directly without heuristics.

## Outcome classes

### Healthy

The declared repository, commit, evidence, or immutable registry target resolves
normally.

### Transient warning

A condition may be temporary and does not justify changing the contract.

Examples:

- DNS or connection failure;
- timeout;
- HTTP 429;
- HTTP 5xx;
- another unexpected non-permanent HTTP response.

Warnings remain visible but do not fail the scheduled workflow.

### Actionable drift

A declared immutable/reachability target no longer resolves, or required
relationship metadata is missing.

Examples:

- HTTP 404 or 410 for the downstream repository, pinned commit, evidence URL,
  or immutable registry target;
- an active consumer record lacks its repository identity.

Drift is a signal for human review. The checker never modifies consumer
metadata or downstream repositories.

## GitHub Actions

The `Consumer contract health` workflow supports:

- manual runs through `workflow_dispatch`;
- a conservative monthly schedule.

Every run:

1. checks active consumer relationships;
2. writes `report.json` and `report.md`;
3. appends the Markdown report to the Actions summary;
4. uploads both files as a workflow artifact;
5. fails only when actionable drift is present.

## Offline validation boundary

Normal pull-request validation remains offline.

Consumer schema, canonical dataset/path/checksum consistency, generated catalog
freshness, and duplicate relationship checks are handled by the regular
repository validator and generator tests.

Network requests are limited to the scheduled/manual external-source and consumer-contract health workflows; pull-request validation stays offline.
