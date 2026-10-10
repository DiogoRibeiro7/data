# Machine-readable registry changelog

The registry publishes an append-only machine-readable history of immutable
snapshot transitions.

The source-of-truth transition entries live under:

`changelog/entries/`

The generated aggregate is:

`reports/registry-changelog.json`

and is published through static distribution v1 at:

`/registry/v1/changelog.json`

Git snapshot tags/releases remain the authoritative release identities.

## Entry model

Each committed transition entry records:

- a unique transition ID;
- exact base snapshot tag + commit;
- exact target snapshot tag + commit;
- base/target manifest versions and manifest SHA-256 digests;
- snapshot-diff schema version;
- which change categories are exact versus aggregate-only;
- categorized semantic changes.

Entries are immutable historical facts. Once a transition is published, later
work appends a new transition file rather than rewriting the old one.

## Continuity

The generator requires one contiguous history:

`A → B`
`B → C`
`C → D`

Both the tag **and exact commit** at the end of one transition must match the
base identity of the next transition.

This prevents a changelog that silently skips or forks release history.

## Historical precision

The first committed transition is:

`snapshot-2026.10.07 → snapshot-2026.10.09`

Those releases used manifest v5 and v6. They did not yet embed normalized
consumer-relationship or provenance-debt item identities, so the changelog
records those two categories as aggregate-exact but item-level unavailable.

From manifest v7 onward, consumer relationships and provenance-debt items are
available for exact item-level diffs.

The changelog keeps this exactness metadata explicitly rather than pretending
older manifests contain information they did not record.

## Current first transition

The Phase 8 → Phase 9 transition records:

- no canonical dataset changes;
- no consumer relationship count change;
- no lifecycle transition;
- provenance/licensing debt **6 → 9**;
- actionable debt **0 → 3**;
- introduction of `diogo-data-registry 0.1.0` / API v1;
- introduction of static distribution v1.

The three additional debt items correspond to the Medium research source
records added between those immutable releases.

## Generation

Regenerate:

```bash
python scripts/generate_registry_changelog.py --write
python scripts/generate_static_distribution.py --write
```

Check freshness:

```bash
python scripts/generate_registry_changelog.py
python scripts/generate_static_distribution.py
```

Both are enforced in CI.

## Schema and compatibility

The changelog contract is versioned by:

`schemas/registry-changelog-v1.schema.json`

A breaking interpretation or required-field change requires a new changelog
schema version. Historical entries remain committed and interpretable.

The static distribution version is a separate compatibility domain; adding
`changelog.json` to v1 is additive and backwards compatible.
