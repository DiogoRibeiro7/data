# Archive and DOI metadata

Milestone registry snapshots can be prepared for long-term archival services
such as Zenodo without changing the repository's licensing model.

The archive tooling is deliberately service-neutral. It generates deterministic
metadata and a policy-filtered bundle locally. Uploading that bundle to an
archive service is a separate publication action.

## Generate an archive-ready bundle

For the default metadata-only profile:

```bash
python scripts/generate_archive_bundle.py \
  --release-dir release-material \
  --output-dir archive-material \
  --tag snapshot-YYYY.MM.DD \
  --commit <40-character-release-commit> \
  --profile release-metadata
```

The output contains:

- `archive-metadata.json`;
- `archive-bundle-manifest.json`;
- `archive-bundle/` with the exact files eligible for that profile.

The bundle manifest records SHA-256 and byte size for every included file.

## Archive profiles

### `release-metadata`

This is the default and safest profile. It contains:

- snapshot manifest, summary, and provenance;
- repository citation metadata;
- preservation policy;
- preservation eligibility report;
- static distribution.

It contains **no canonical, external, or legacy dataset bytes**.

### `eligible-canonical-bytes`

This explicitly broader profile additionally includes only canonical datasets
whose committed preservation eligibility is `eligible`.

External-source and legacy-quarantine bytes are never included merely because
they exist in repository history.

## Deterministic metadata

`archive-metadata.json` records:

- exact snapshot tag and release commit;
- deterministic snapshot citation;
- creators from `CITATION.cff`;
- ORCID values when configured in `CITATION.cff`;
- description and keywords;
- archive profile;
- repository/tooling licence identity;
- explicit statement that upstream dataset terms remain controlling;
- Git commit and GitHub release identifiers;
- preservation-policy and eligibility versions;
- assigned archive/DOI identifiers when they have been recorded.

No archive-service timestamp, deposition ID, or DOI is invented before a
service assigns it.

## Recording a DOI or archive identifier

After an archive service assigns an identifier, add it to
`archive/identifiers.json` in a reviewed follow-up change.

Each entry is bound to the exact immutable snapshot:

```json
{
  "tag": "snapshot-YYYY.MM.DD",
  "commit": "<40-character-release-commit>",
  "provider": "zenodo",
  "identifier": "10.5281/zenodo.1234567",
  "relation": "isIdenticalTo"
}
```

Regenerating archive metadata for that exact snapshot then exposes the assigned
identifier. Identifiers for another commit or tag are never inherited.

A DOI is an additive citation identifier. It never replaces the snapshot tag
and commit, and an existing snapshot tag is never moved to match an archive.

## Publication procedure

1. ensure the target commit is green;
2. run the snapshot workflow in dry-run mode;
3. inspect and verify the deterministic release material;
4. generate the archive bundle with the intended profile;
5. inspect `archive-bundle-manifest.json`;
6. publish the immutable GitHub snapshot;
7. upload the inspected archive bundle to the preservation service;
8. after the service assigns an identifier, add it to
   `archive/identifiers.json` through review;
9. do not rewrite the historical snapshot or archive record.

Service credentials are intentionally not required by the repository tooling.
Archive publication can remain manual when no service integration is
configured.
