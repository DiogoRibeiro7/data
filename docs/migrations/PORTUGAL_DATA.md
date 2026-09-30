# Migration audit: `Portugal-Data`

## Source repository

`DiogoRibeiro7/Portugal-Data`

The repository contains two files and one historical commit:

- `grouping.json`
- `worms_12jan.json`
- source commit `893f469cb4dd45fe02eb24424d0e3c261eacb802`

## Semantic audit

`worms_12jan.json` is a person-affiliation history dataset, not a general Portugal reference dataset. It contains 130 named individuals and structured records for government/municipal roles, party roles, and company/organisation positions.

`grouping.json` is a normalization map for 20 companies/groups and their related aliases.

## Dependency audit

Repository-wide code search found no consumer of either filename and no raw-data dependency on `Portugal-Data`.

The only account-level reference to the repository name was in `project-reminders/data/project_metadata.json`, where it is listed as repository metadata rather than consumed as a data dependency.

## Redistribution and provenance audit

No explicit licence or redistribution statement is present in `Portugal-Data`.

A public-web search produced a text source closely matching several records, but this is insufficient to establish authoritative provenance or redistribution permission for the structured files.

The dataset also contains named-person political/party affiliation information. Under the repository's own policy, that is sufficient reason not to duplicate the bytes automatically into the central public registry.

## Decision

Do **not** copy the two source files into `datasets/` or `legacy/`.

Instead:

1. register a metadata-only external reference at `external/portugal-political-business-links/`;
2. preserve the original source repository for historical traceability;
3. add a deprecation notice to the old repository;
4. do not archive the source repository until the deprecation change is merged;
5. reconsider canonical promotion only after provenance, redistribution, and handling questions are resolved.

This decision supersedes the original assumption in issue #4 that every source repository should result in a canonical copied dataset.
