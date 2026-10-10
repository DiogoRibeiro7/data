# Snapshot-to-snapshot diffs

`scripts/diff_snapshots.py` compares two local immutable
`snapshot-manifest.json` files and produces deterministic JSON and Markdown
change summaries.

No network access is required.

## Usage

```bash
python scripts/diff_snapshots.py \
  --base previous/snapshot-manifest.json \
  --target current/snapshot-manifest.json \
  --json-output snapshot-diff.json \
  --markdown-output snapshot-diff.md
```

The two manifests must belong to the same registry repository.

## Diff surface

The diff classifies:

- canonical datasets added and removed;
- canonical dataset metadata changes;
- canonical files added/removed;
- canonical file SHA-256 changes;
- consumer relationships added/removed/changed;
- lifecycle changes and preferred replacements;
- provenance/licensing debt items added/removed/changed;
- metadata schema version/digest changes;
- snapshot manifest version transitions;
- registry client/package/API changes;
- static-distribution version and artifact changes.

Every output records exact base/target:

- snapshot tag;
- commit SHA;
- manifest version;
- repository.

## Historical manifests

Snapshot manifest **v7** adds normalized consumer relationship identities and
provenance-debt item identities specifically so those two areas can be diffed
exactly.

Older manifests remain supported. When either side lacks those v7 identity
lists, the tool:

- compares the aggregate counts that are available;
- sets `exact_relationship_diff_available: false` for consumers;
- sets `exact_item_diff_available: false` for provenance debt;
- does **not** invent item-level history.

This distinction is intentional: a diff must never claim precision that the
historical release did not record.

## Empty diffs

Two semantically identical manifests produce:

```json
{
  "empty": true
}
```

Tag/commit identity alone is not treated as a semantic registry change. The
base/target identities are still recorded in the diff.

## Determinism

JSON keys and collection identities are deterministically ordered. Given the
same two manifest bytes, JSON and Markdown outputs are byte-for-byte
reproducible.

The diff engine operates only on immutable manifest contents. It does not read
floating branch state or query GitHub.
