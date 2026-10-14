# External-source state contract

This page defines the normative cross-interface contract for external-source
resolution and availability state.

The same committed source state is projected through raw metadata, generated
catalogs, the static distribution, the typed Python API, the CLI, and immutable
snapshot manifests. These interfaces must agree semantically.

## Source of truth

The authoritative source is:

```text
external/<source-id>/metadata.yaml
```

Generated catalogs, client models, CLI summaries, static distribution files,
and snapshot projections must never introduce state that is absent from the
committed source record.

Two optional metadata blocks define external state:

- `resolution` — provenance/licensing review state;
- `availability` — reviewed upstream availability/disappearance state.

The top-level `redistribution` field remains the operative redistribution
policy. Resolution state explains why a policy question remains unresolved; it
does not override that policy.

## Resolution state

A `resolution` block may contain:

- `review_status`: `actionable` or `terminal`;
- `terminal`: boolean matching `review_status`;
- `blocker_category`;
- review/evidence fields retained in raw metadata.

Projection rules:

| Raw metadata | Catalog/API projection |
| --- | --- |
| no `resolution` block | resolution fields absent in catalog and `None` in typed API |
| `review_status: actionable` | `resolution_status = actionable`, `terminal = false` |
| `review_status: terminal` | `resolution_status = terminal`, `terminal = true` |
| `blocker_category` present | projected unchanged |
| evidence/reviewer prose | remains in raw metadata; not part of compact catalog state |

A terminal state means the current evidence review is complete unless genuinely
new evidence appears. It does not mean the source is invalid.

## Availability state

An optional `availability` block records reviewed upstream state.

Supported states:

- `live`;
- `transient-outage`;
- `moved`;
- `permanently-unavailable`;
- `legal-withdrawal`.

Projection rules:

| Raw metadata | Catalog/API projection |
| --- | --- |
| no `availability` block | availability fields absent in catalog and `None` in typed API |
| `state` present | projected as `availability_state` |
| `replacement_url` present | projected unchanged |
| review/evidence fields | retained in raw metadata; compact projections may omit them |

Absence of an availability block means **no reviewed exceptional availability
state has been committed**. Callers must not infer that a live network check was
performed.

## Interface mapping

### Raw metadata

`external/<id>/metadata.yaml` is authoritative.

It contains the full evidence record and may include fields intentionally not
projected into compact interfaces.

### Generated external catalog

`external/catalog.json` is a deterministic normalized projection governed by:

```text
schemas/external-catalog-v1.schema.json
```

For state-bearing records it may expose:

```json
{
  "resolution": {
    "review_status": "terminal",
    "terminal": true,
    "blocker_category": "redistribution-rights"
  },
  "availability": {
    "state": "moved",
    "replacement_url": "https://example.org/new",
    "last_reviewed": "2026-10-14"
  }
}
```

Optional state blocks are omitted when not present in authoritative metadata.

### Static distribution

`distribution/v1/external.json` must be byte-for-byte identical to
`external/catalog.json`.

Therefore external state published through the static distribution is exactly
the generated catalog state. There is no independent transformation layer.

Additive optional state fields remain compatible with distribution v1.
A new distribution version is required only for a breaking path, structure, or
interpretation change.

### Python API

`ExternalRecord` exposes:

- `resolution_status: str | None`;
- `terminal: bool | None`;
- `blocker_category: str | None`;
- `availability_state: str | None`;
- `replacement_url: str | None`.

`None` means the corresponding optional committed state was not present. It
must not be interpreted as an implicit policy or live-network result.

`RegistryClient.external_records(...)` filters only committed state and performs
no network access.

Adding these optional fields and filtering helpers is compatible with public API
version 1 because existing method signatures and meanings remain unchanged.

### CLI

JSON list/search summaries expose the same compact fields as the typed client.

External-state filters:

```bash
data-registry list --layer external --resolution-status terminal
data-registry list --layer external --availability-state moved
data-registry search medium --layer external --resolution-status terminal
```

The filters operate only on committed state and require `--layer external`.

Human-readable list/search output may remain compact; JSON output is the stable
machine-readable projection.

### Snapshot manifests and diffs

Snapshot manifest v9 embeds normalized external state:

- resolution status;
- terminal flag;
- blocker category;
- availability state;
- replacement URL.

This makes v9-to-v9 state transitions exactly reconstructible from immutable
release manifests.

Examples:

- `actionable → terminal`;
- `live → moved`;
- blocker-category changes;
- replacement-URL changes.

Historical manifests v1–v8 remain valid. When either side of a comparison lacks
v9 external-state records, the diff reports:

```text
exact_state_diff_available: false
```

The tool must not infer or reconstruct field-level history from current
repository state.

## Compatibility matrix

| Interface | Current contract | External-state compatibility rule |
| --- | --- | --- |
| Raw external metadata | schema v1 | optional `resolution` and `availability` blocks are backward-compatible |
| External catalog | schema v1 | optional projected state fields are additive |
| Static distribution | v1 | byte-identical catalog copy; optional fields do not require v2 |
| Python API | v1 | new optional model fields/helpers may be additive |
| CLI | API v1 package surface | new optional filters/output fields are additive |
| Snapshot manifest | v9 current | v9 adds exact normalized external state; v1–v8 stay immutable |
| Snapshot diff | schema v1 | exact state transitions only when both manifests contain v9 state |

## Consumer expectations

Consumers should:

1. treat raw metadata as authoritative when full evidence is required;
2. use catalog/distribution state for compact machine-readable discovery;
3. treat missing optional state as absence of a committed reviewed state;
4. never infer redistribution permission from resolution or availability state;
5. never infer current network reachability from absence of an availability block;
6. tolerate additive optional fields within catalog/distribution/API v1;
7. use manifest v9+ when exact historical external-state transitions matter.

Consumers must not:

- treat `terminal` as equivalent to `redistribution: prohibited`;
- treat `None` availability as a confirmed live source;
- reconstruct historical external state from present-day metadata;
- assume a replacement URL grants redistribution rights.

## Migration expectations

No migration is required for consumers that:

- ignore unknown optional JSON fields;
- already read the external catalog as a JSON object;
- use existing API-v1 methods without external-state filtering.

Consumers that validate JSON with their own closed schema should update it to
permit the optional `resolution` and `availability` catalog blocks.

Consumers requiring exact historical external-state transitions should use
snapshot manifest v9 or later. Older immutable snapshots are not upgraded or
rewritten.

## Validation

The repository enforces the contract through tests that verify:

- catalog projection from external metadata;
- catalog JSON Schema validation;
- byte-for-byte static-distribution parity;
- typed API projection and filtering;
- CLI filtering/error behavior;
- manifest v9 external-state projection;
- exact v9 snapshot-state transitions;
- conservative pre-v9 fallback.

The contract is deterministic and offline. Live source health checks are a
separate concern and do not participate in ordinary registry reads or snapshot
diffs.
