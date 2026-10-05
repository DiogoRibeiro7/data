# Provenance and licensing resolution evidence

External and legacy records may carry an optional `resolution` block when a
provenance, snapshot, lineage, or redistribution question remains unresolved.

The block is deliberately structured so unresolved debt can be audited,
measured, and revisited without relying only on README prose.

## When to use it

Use `resolution` when a record has a known blocker such as:

- exact historical snapshot identity is not pinned;
- redistribution rights are not explicit;
- a repository-level licence may not cover dataset bytes;
- derived-file lineage is incomplete;
- the authoritative source family is uncertain;
- the exact historical export route cannot be reconstructed.

Resolved records do not need a `resolution` block.

## Shape

Example actionable record:

```yaml
resolution:
  review_status: actionable
  last_reviewed: 2026-10-05
  blocker_category: redistribution-rights
  blocker_summary: Dataset-specific redistribution terms are not explicit.
  evidence:
    - https://example.org/terms
  reviewer_note: Recheck the provider terms page before promotion.
  next_action: Review authoritative terms and update redistribution status.
  terminal: false
```

Example terminal record:

```yaml
resolution:
  review_status: terminal
  last_reviewed: 2026-10-05
  blocker_category: historical-export-route
  blocker_summary: Exact historical export cannot be reconstructed from available evidence.
  evidence:
    - https://example.org/archive
  next_action: Retain in quarantine unless new upstream evidence appears.
  terminal: true
```

## Fields

### `review_status`

Allowed values:

- `actionable` — further concrete research can reasonably change the outcome;
- `terminal` — the current evidence has been exhausted and the record should
  remain external/quarantined unless genuinely new evidence appears.

### `last_reviewed`

ISO calendar date of the most recent evidence review.

This is not the source publication date. It records when the registry last
evaluated the blocker.

### `blocker_category`

Allowed categories:

- `exact-snapshot-identity`;
- `redistribution-rights`;
- `dataset-vs-repository-licence-scope`;
- `derived-lineage`;
- `authoritative-source-identity`;
- `historical-export-route`.

Choose the narrowest category that explains why the record cannot move to a
more resolved state.

### `blocker_summary`

Short statement of the unresolved fact.

Describe the missing evidence, not merely the consequence. Prefer:

> Dataset-specific redistribution terms were not found.

over:

> Cannot promote.

### `evidence`

One or more authoritative or audit-relevant URLs supporting the current
decision.

Evidence may include:

- publisher terms;
- versioned repository files;
- archived documentation;
- dataset landing pages;
- prior audit documents.

Do not use a search-results page as evidence when a direct source is available.

### `reviewer_note`

Optional context that helps a future reviewer understand the previous audit.

### `next_action`

Concrete next step.

For actionable debt, describe the next research task.

For terminal debt, describe the condition that would justify reopening the
decision, for example:

> Retain in legacy quarantine unless the publisher exposes an archived export
> manifest or explicit redistribution terms.

### `terminal`

Must agree with `review_status`:

- `actionable` → `false`;
- `terminal` → `true`.

## Actionable versus terminal debt

Terminal does **not** mean the metadata is invalid or that the source is bad.

It means the current registry has reached a stable decision with the available
evidence and should not repeatedly spend effort on the same unresolved point.

A terminal record can be reopened when new evidence appears.

Actionable debt should have a real next step that could reasonably change the
decision.

## Relationship to redistribution state

The `resolution` block does not override `redistribution`.

For example:

```yaml
redistribution: unresolved
resolution:
  review_status: actionable
  ...
```

The redistribution field remains the operative source-policy state. The
resolution block explains why that state is unresolved and what should happen
next.

## Relationship to canonical promotion

Structured evidence does not relax canonical policy.

Canonical stored bytes still require explicit redistribution permission and the
full canonical provenance/integrity contract.

## Phase 6 migration

Issue #85 introduces this optional schema block.

Later Phase 6 issues backfill it onto unresolved external and legacy records,
generate a deterministic debt queue, and use the structured evidence in CLI and
quality reporting.
