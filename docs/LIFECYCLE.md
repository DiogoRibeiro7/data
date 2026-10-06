# Canonical dataset lifecycle

Canonical metadata schema version 2 makes lifecycle and version identity explicit
for every dataset under `datasets/`.

The lifecycle model preserves immutable historical snapshots while making the
preferred replacement path discoverable.

## Identity model

Each canonical metadata record has three distinct identifiers:

- `id` — immutable identifier for one canonical snapshot and its directory;
- `family` — stable identifier shared by versions of the same logical dataset;
- `version` — version identifier unique within that family.

A dataset ID never changes after publication. A newer version is represented by
a new canonical dataset ID.

## Lifecycle states

### `active`

The dataset is a current canonical version.

An active dataset may be the first version in its family
(`supersedes: null`) or a newer version that supersedes one immediate
predecessor.

### `superseded`

The dataset remains canonical, immutable, citable, and checksum-verifiable, but
a newer canonical version is preferred.

The preferred successor is **not** written into the old record. It is derived
from another dataset whose `lifecycle.supersedes` points to the old dataset.

### `deprecated`

The dataset remains reproducible but should not be selected for new consumption.

Deprecation does not necessarily imply that a replacement exists. When a
replacement does exist, the replacement edge is still represented by
`supersedes`.

## Replacement edge

The only authored replacement edge is:

`lifecycle.supersedes`

It names the **immediate** predecessor dataset ID.

Example:

```yaml
id: example-data-2026
family: example-data
version: "2026"
lifecycle:
  state: active
  supersedes: example-data-2025
  transitioned_at: 2026-10-06
  compatibility: "Columns are unchanged."
  notes: "Annual refresh."
```

The old dataset does **not** carry a manually maintained `superseded_by`
field. Reverse lookup is derived from the lifecycle graph. This avoids two
reciprocal fields drifting apart.

## Transition metadata

Optional lifecycle context:

- `transitioned_at` — ISO date of the lifecycle transition;
- `compatibility` — schema/API/data compatibility or migration note;
- `notes` — free-form lifecycle rationale.

These fields describe registry lifecycle, not upstream release provenance.
Upstream version and retrieval identity remain under `source`.

## Initial canonical versions

Datasets that existed before lifecycle schema v2 are migrated as:

- explicit family;
- explicit version;
- `state: active`;
- `supersedes: null`.

This migration changes metadata semantics only. It does not rewrite canonical
data bytes or historical Git releases.

## Current schema policy

Current canonical metadata must use schema version **2**.

`schemas/canonical-metadata-v1.schema.json` remains committed so historical
registry snapshots can still be interpreted, but schema v1 is not accepted for
new/current canonical records on `main`.

## Semantic validation

The JSON Schema enforces structure and allowed lifecycle values.

Phase 8 semantic validation additionally enforces graph-level invariants such
as:

- replacement references resolve;
- predecessor and successor share a family;
- version identifiers are unique within a family;
- no self-reference or cycle exists;
- no ambiguous immediate replacement exists;
- lifecycle state and replacement structure agree.

Those graph invariants are implemented separately from the schema because they
require knowledge of the full canonical registry.

## Consumer semantics

A consumer may remain pinned to a superseded dataset for reproducibility.

The registry will distinguish:

- consumer already on the preferred version;
- consumer requiring migration;
- consumer intentionally retained on a historical version with rationale.

No lifecycle transition silently rewrites a consumer's pinned commit, path, or
SHA-256.
