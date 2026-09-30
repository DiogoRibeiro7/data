# Licensing and data notice

This repository is a **multi-license data registry**. No single repository-wide licence applies to every file.

## Repository tooling

Code and small infrastructure files maintained specifically for this repository, including scripts and tests, are licensed under the MIT License in [LICENSE-CODE](LICENSE-CODE), unless a file states otherwise.

## Documentation and metadata

Repository-maintained policy, metadata, catalog, and migration documentation may describe third-party datasets and licences. That documentation does not change ownership or licensing of the underlying data.

## Canonical datasets

Every canonical dataset must declare its own licence or redistribution terms in its `metadata.yaml`.

A dataset's upstream terms take precedence over repository tooling licences.

## External sources

Entries under `external/` are provenance/source records. They may point to providers with their own licences, terms of use, attribution requirements, commercial-use restrictions, API policies, or citation requirements.

Do not infer permission to redistribute upstream bytes merely because an external source is documented here.

## Legacy data

Files under `legacy/` are retained for historical traceability and are not automatically relicensed.

Some legacy files have unresolved provenance or redistribution terms. Treat them as non-canonical and review their package metadata before reuse or redistribution.

## Attribution and citation

When using data:

1. follow the upstream licence and terms;
2. preserve required attribution;
3. cite the original publisher or paper where available;
4. record the exact snapshot/version used;
5. retain checksums for reproducible work.

If a dataset's rights are unclear, do not republish it as canonical data until the ambiguity is resolved.
