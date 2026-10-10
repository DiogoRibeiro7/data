# Archival preservation policy

This policy governs what registry material may be preserved outside GitHub in
long-term archival services such as Zenodo.

The governing machine-readable contract is
`preservation/policy-v1.json`. The generated current-state decision report is
`reports/preservation-eligibility.json`.

## Identity

The primary technical identity of a registry snapshot remains:

1. immutable snapshot tag;
2. exact Git commit.

A DOI or archive record is an additional durable citation identifier. It does
not replace the Git identity and does not permit changing an already published
snapshot.

## Eligibility matrix

| Content | Archive treatment |
| --- | --- |
| Registry-maintained tooling | Allowed under `LICENSE-CODE` (MIT) |
| Registry-authored metadata, policies, catalogs, manifests and summaries | Allowed |
| Static machine-readable distribution | Allowed |
| Canonical dataset bytes with `license.redistribution: allowed` | Eligible, with upstream attribution/licence preserved |
| Canonical bytes without explicit redistribution permission | Metadata-only |
| External-source records | Metadata-only by default |
| External-source bytes | Never archived by default |
| Legacy quarantine metadata | Allowed as metadata |
| Legacy quarantine bytes | Never archived until separately promoted to canonical |

The policy is deliberately asymmetric: documenting a third-party source never
creates permission to archive its bytes.

## Archive profiles

### Release metadata

The safest default archive profile contains only registry-authored material:

- snapshot manifest;
- snapshot summary;
- versioned static distribution;
- citation/archive metadata;
- preservation policy;
- preservation eligibility report.

This profile never includes canonical dataset bytes.

### Eligible canonical bytes

A broader profile may additionally include canonical dataset bytes only when
the committed canonical metadata explicitly records redistribution as
`allowed`.

Each included dataset must travel with:

- upstream publisher;
- exact source/snapshot identity;
- licence/terms name and URL;
- citation where available;
- file SHA-256 checksums.

A mixed archive bundle cannot apply one blanket licence that overrides the
upstream licences of individual datasets.

## Hard exclusions

Never place the following in an archival bundle merely because they exist in
repository history:

- private or personal data;
- confidential or regulated data;
- redistribution-restricted bytes;
- bytes with unresolved redistribution rights;
- external-layer source bytes;
- legacy-quarantine bytes.

If legal/redistribution evidence changes later, eligibility is recomputed from
the new committed registry state; historical snapshots remain unchanged.

## Corrections and supersession

Published archive records are not rewritten to hide an earlier state.

If an archived release later has an integrity, provenance, privacy, or
licensing problem:

1. preserve the historical Git tag/commit identity;
2. mark the archive record as superseded/withdrawn where the service permits;
3. publish a corrected new snapshot/archive record;
4. link the replacement to the earlier identifier;
5. document what changed.

## Current eligibility

The deterministic report currently classifies:

- **4 / 4 canonical datasets** as byte-archive eligible;
- **16 external sources** as metadata-only;
- **2 legacy packages** as metadata-only.

This is a mechanical policy decision from committed metadata, not a new legal
grant. Upstream terms remain controlling.
