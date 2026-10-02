# External source health and drift checks

The registry contains external-source records for datasets whose authoritative bytes remain upstream.

Those records can become stale even when the repository itself does not change. Examples include:

- a source URL disappearing;
- a licence or terms page moving;
- a pinned GitHub commit no longer resolving;
- a DOI failing to resolve;
- a generated external catalog drifting away from metadata IDs.

The repository therefore provides a lightweight health checker:

```bash
python scripts/check_external_sources.py \
  --json-report external-health/report.json \
  --markdown-report external-health/report.md
```

## Outcome classes

The checker deliberately separates three classes.

### Healthy

A declared endpoint resolves normally and structural registry metadata is consistent.

### Transient warning

A condition may be temporary and does **not** by itself justify changing provenance or licensing metadata.

Examples:

- DNS/network failure;
- timeout;
- HTTP 429;
- HTTP 5xx;
- another unexpected HTTP response that is not a confirmed permanent disappearance.

Transient warnings are reported but do not fail the scheduled workflow.

### Actionable drift

A condition indicates that the stored registry claim needs human review.

Examples:

- HTTP 404 or 410 for a declared source/licence/DOI endpoint;
- a pinned GitHub commit no longer resolves;
- a metadata ID is missing from the external catalog;
- a catalog ID has no matching metadata directory;
- a metadata ID does not match its directory;
- a pinned commit is declared for a source that cannot be mapped to a GitHub repository.

The checker **never edits metadata**. A drift finding is a signal to investigate and open a normal reviewed change.

## GitHub Actions

The `External source health` workflow supports:

- manual runs through `workflow_dispatch`;
- a conservative monthly schedule on the first day of each month.

Every run:

1. checks all external records;
2. writes `report.json` and `report.md`;
3. appends the Markdown report to the Actions summary;
4. uploads both files as a workflow artifact;
5. fails only when actionable drift is present.

Transient network warnings remain visible but non-failing.

## What is checked

For each external record, when applicable:

- `source_url`;
- licence / terms URL;
- DOI resolution through `doi.org`;
- pinned GitHub `source_commit`;
- metadata/catalog ID and path consistency.

The regular repository validator remains responsible for schema validity and generated catalog freshness.

## Licence and provenance guardrails

This health check is intentionally conservative.

It does not:

- infer a licence from a provider default;
- replace dataset-specific terms;
- auto-update a publisher, source, licence, or redistribution field;
- treat a transient outage as evidence that metadata is wrong.

Any provenance or licensing correction must still be made through a reviewed pull request with authoritative evidence.
