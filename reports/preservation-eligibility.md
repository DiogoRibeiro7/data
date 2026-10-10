# Archival preservation eligibility

This report is generated deterministically from committed registry metadata
and the versioned preservation policy. It does not grant rights beyond
the recorded upstream licence/terms.

- Preservation policy: `preservation/policy-v1.json` (v1)
- Release metadata: **eligible**
- Static distribution: **eligible**
- Canonical datasets: **4**
- Canonical byte-archive eligible: **4**
- Canonical metadata-only: **0**
- External sources (metadata-only): **16**
- Legacy packages (metadata-only): **2**

## Canonical dataset bytes

| Dataset | Eligibility | Redistribution | Licence |
| --- | --- | --- | --- |
| `online-retail-ii` | eligible | allowed | CC BY 4.0 |
| `ons-gross-median-weekly-pay` | eligible | allowed | Open Government Licence v3.0 |
| `ucdp-ged-25-1` | eligible | allowed | CC BY 4.0 |
| `unhcr-refugee-population-2024` | eligible | allowed | CC BY 4.0 |

## External sources

External records are archive-eligible as metadata only. Their upstream
bytes are not copied into an archive unless they are separately promoted
to the canonical layer under explicit redistribution permission.

## Legacy quarantine

Legacy records are archive-eligible as metadata only. Quarantined bytes
are not included in preservation bundles unless a later canonical
promotion establishes exact identity and redistribution permission.

## Corrections and identifiers

- Git snapshot tag + exact commit remain the primary technical identity.
- DOI/archive identifiers are additive citation identifiers.
- Published snapshot tags and archive records are not rewritten in place.
- Corrections create a new record that links/supersedes the earlier one.
- A mixed archive bundle never overrides per-dataset upstream terms.
