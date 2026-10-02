# Citation guidance

This repository contains two distinct things:

1. **registry software/tooling and repository-maintained metadata/documentation**;
2. **datasets and external data sources with their own upstream licences and citation requirements**.

A citation of this repository never replaces a required citation or attribution for an upstream dataset.

## Cite the registry tooling

GitHub reads the root `CITATION.cff` file and exposes a **Cite this repository** control.

For general use of the registry tooling, cite the repository as a software/research-data-management resource and include the repository URL.

A minimal human-readable form is:

> Ribeiro, D. *Data Registry*. GitHub. https://github.com/DiogoRibeiro7/data

When a DOI becomes available through an archival service such as Zenodo, prefer the archived record for the released version.

## Cite a published registry snapshot

A reproducible citation to a published registry snapshot must identify **both**:

- the exact immutable snapshot tag, for example `snapshot-YYYY.MM.DD[.N]`;
- the exact 40-character Git commit SHA referenced by that tag.

For an actual release, resolve the commit with:

```bash
git rev-list -n 1 snapshot-YYYY.MM.DD
```

Then cite the snapshot in a form such as:

> Ribeiro, D. *Data Registry*, `snapshot-YYYY.MM.DD`, commit `<40-character-git-sha>`. GitHub.

Do not substitute a floating branch name such as `main` for the commit.

The snapshot release also attaches:

- `snapshot-manifest.json`;
- `snapshot-summary.md`.

Those files record the exact repository commit, catalog digests, schema versions, and canonical dataset file checksums.

## Cite a dataset from the registry

If you use a canonical dataset, cite the **upstream dataset/publisher** according to its own metadata and licence requirements.

Also record the registry snapshot used for reproducibility:

- registry tag;
- exact registry commit;
- canonical path;
- file SHA-256.

For example, a paper or analysis may include both:

1. the upstream dataset citation from `datasets/<dataset>/metadata.yaml`;
2. the registry snapshot identity that supplied the exact bytes.

The registry citation is supplementary reproducibility metadata. It is not a replacement for upstream attribution.

## External source records

Records under `external/` are provenance/discovery records.

They may point to datasets that:

- cannot be redistributed here;
- have provider-specific terms;
- have per-series or per-file licensing;
- require their own citations.

Cite the authoritative upstream source, not merely the external registry record.

## Legacy material

Files under `legacy/` are quarantined historical material.

Their presence does not imply verified provenance, citation completeness, or redistribution permission.

Do not treat a registry-level citation as permission to reuse or republish a legacy file.

## Machine-readable metadata

The repository provides:

- `CITATION.cff` using Citation File Format 1.2.0;
- `codemeta.json` using the CodeMeta 3.1 JSON-LD context.

These describe the **repository-maintained registry software/tooling**.

They intentionally do not claim that all datasets in this repository are MIT-licensed.

Dataset-specific rights and citations remain authoritative in:

- canonical `metadata.yaml`;
- external-source metadata;
- upstream provider records.

## Archival workflow

For a future Zenodo/DataCite archival release:

1. create the immutable registry snapshot first;
2. verify the snapshot tag and exact commit;
3. publish the GitHub release with its manifest/summary;
4. archive that release;
5. preserve the generated DOI in the release/citation metadata in a follow-up reviewed change;
6. never move or rewrite the published snapshot tag.

This keeps software citation, registry-version identity, and upstream dataset attribution separate and reproducible.
