# INE Portugal: median new-lease rents, 2025

This canonical package preserves indicator **0014698**, period **S7A2025**:
annual median monthly rent per m² of gross private area for new family-dwelling
leases, methodology 2026, NUTS 2024. It contains original public statistical
responses and interpretation metadata; there are no household records or
transformed analytical outputs.

The scope and snapshot were reviewed in the merged
[platform source proposal](https://github.com/DiogoRibeiro7/data-platform-lab/pull/106).
The package supports municipal housing research and the planned platform
adapter. This registry owns immutable source bytes and provenance; the platform
owns curation and database publication.

## Snapshot and acquisition

| File in `raw/` | Bytes | Acquired | Role |
| --- | ---: | --- | --- |
| `ine_0014698_S7A2025_2026-10-30.json` | 91,363 | 2026-10-30 | Observations for 2025, all returned geographic levels |
| `ine_0014698_metadata_2026-11-16.json` | 150,884 | 2026-11-16 08:56:10 UTC | Indicator metadata, geography codebook and revision note |
| `ine_0014698_methodology_2026-11-16.html` | 8,819 | 2026-11-16 08:56:14 UTC | Indicator information page and concepts |

[metadata.yaml](metadata.yaml) records SHA-256 identities for all three files,
the exact request URLs, collection dates and citation. The dataset-level
`source.retrieved_at` describes the observations; companion collection dates
are separate. `.gitattributes` disables text normalization for these raw files.

The observation request was
[`pindica.jsp?op=2&varcd=0014698&Dim1=S7A2025&lang=PT`][observations].
The registry copied the exact existing [research Git blob][candidate] from
`social-security-housing-investment`, commit
`f84577d7cb5a5dd0338707faa32fe166881d9596`, path
`data/snapshots/rents/ine_0014698_S7A2025_2026-10-30.json`, blob ID
`500ab19d99028aa3484227a35ff3714b763afaa7`. Its hash and size match the
[committed research inventory][inventory]. No fresh observation request was
used to replace that historical snapshot.

The metadata was acquired through `ine_metadata()` with cache disabled,
30-second request timeout and at most two retries, using the existing
[`ineDataClient` source][client] at commit
`e60e69ea3a4f149b61b3b2b44c49e8c01be6095a` (package version 0.1.9).
The same client's curl transport retrieved the information page. Exact response
bodies were saved without re-serializing JSON or rewriting HTML. This describes
the November companion acquisition, not the original research collector.

Both JSON responses report source update **2026-09-29**. The November codebook
has the same 638 geography codes and labels as the October observations, and
declares period `S7A2025`, classification `05433`, annual frequency and EUR/m²
units. These checks establish compatibility for this package; they do not prove
historical metadata identity or an atomic upstream release. The endpoints are
mutable, and every future revision needs new reviewed bytes and hashes.

## Observation contract

The response is a singleton JSON array. Its `Dados["2025"]` contains 638
records keyed by `geocod`. Keep every code as a string, including letters,
leading zeroes and the full geographic prefix. Resolve geography levels from
the pinned metadata's `Dimensoes.Categoria_Dim`, not code length.

| Metadata level | Geography | Records | Numeric values | Null/not applicable |
| --- | --- | ---: | ---: | ---: |
| 1 | Portugal | 1 | 1 | 0 |
| 2 | NUTS I | 3 | 3 | 0 |
| 3 | NUTS II | 9 | 9 | 0 |
| 4 | NUTS III | 26 | 26 | 0 |
| 5 | Municipalities | 308 | 247 | 61 |
| 6 | Selected parishes | 291 | 201 | 90 |
| Total | All returned levels | 638 | 487 | 151 |

Each row carries a source label `geodsg` and display string `ind_string`.
Numeric `valor` fields are decimal strings; parse with decimal arithmetic,
preserving source precision (two decimal places) and scale (exponent zero).
Missing records omit `valor` and carry `sinal_conv: "-"` with the source
description meaning null/not applicable. Preserve that flag and description;
do not turn it into zero or assume confidentiality. Other vintages may introduce
different flags and require explicit review.

The natural observation key is `(indicator, period, geography classification,
geocod)` within one source snapshot. Metadata covers 2020–2025, but this package
contains observations for **2025 only**. Municipal consumers select level 5
and retain all 308 rows, including the 61 null values. The registry does not
materialize a municipal subset or a Gold table.

## Interpretation and source defects

Values describe nominal contracted new-lease rents. They are not asking prices,
all-tenancy rents, total dwelling rents, sale prices or inflation-adjusted
values. Regional medians cannot be reconstructed by averaging municipal medians.
Affordability analysis needs independently compatible income and area measures.
Do not splice methodology 2026 into older methodology series or join different
geographic editions without an explicit concordance.

The pinned metadata reports that 2020–2025 values were revised on 2026-09-29,
affecting some NUTS III areas. The archived information page has a known
inconsistency: its formula mentions sales while its title, indicator and
concepts concern rents. It also contains upstream encoding defects. Both remain
unchanged. Consumers can use the identified published rent observations, but
must not treat that formula as a verified computational definition or silently
correct the official source.

## Licence and attribution

INE's [published reuse notice][rights] permits reuse of its statistical
information under [CC BY 4.0][licence], with clear source attribution. This is
also recorded in the broader [INE external-source record][external]. The scope
here is directly published INE statistics and metadata, not PORDATA exports.

Suggested attribution:

> Fonte: Instituto Nacional de Estatística, I.P. – Portugal. Indicator 0014698,
> reference year 2025, methodology 2026, NUTS 2024. Observations collected
> 2026-10-30; companion metadata collected 2026-11-16. CC BY 4.0.

Link the licence and identify any downstream selection or transformation.
The registry code licence does not replace the source terms.

## Consumer and handoff

`DiogoRibeiro7/data-platform-lab` is the intended consumer. Its reviewed
[contract proposal][platform-contract] is pinned at
`cf1bd2f9de0ecdc95e6f1390c185f00b08df84db`; it is **not an implemented INE
adapter**. No active canonical consumer relationship is claimed. A documented
adoption exemption in [the quality policy][adoption-policy] covers the interval
between source promotion and the first downstream migration. Remove it when
the platform implements the adapter, pins the merged registry commit and all
source hashes, and registers the actual consumer implementation commit.

After this promotion is reviewed and merged, an operator can generate the
existing provider-neutral handoff from the exact trusted registry checkout:

```bash
data-registry --root . handoff ine-portugal-new-lease-rents \
  --commit "$REGISTRY_COMMIT" --verify-local --verify-checkout --json
```

`REGISTRY_COMMIT` must be the independently selected full commit checked out
locally, not a floating branch name or a value trusted solely from a manifest.
The plan includes all three raw artifacts and their hashes. Store the emitted
plan outside this registry; no self-referential commit or fabricated handoff
hash is committed here. See the [handoff contract][handoff] for offline
received-byte and trusted-checkout verification.

Source promotion and a successful handoff verification do not constitute
platform ingestion, database publication, acceptance evidence or release
activation. Other research repositories retain their existing snapshots until
their own separately reviewed migrations.

[observations]: https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0014698&Dim1=S7A2025&lang=PT
[candidate]: https://gitlab.com/DiogoRibeiro7/social-security-housing-investment/-/blob/f84577d7cb5a5dd0338707faa32fe166881d9596/data/snapshots/rents/ine_0014698_S7A2025_2026-10-30.json
[inventory]: https://gitlab.com/DiogoRibeiro7/social-security-housing-investment/-/blob/f84577d7cb5a5dd0338707faa32fe166881d9596/data/sources/rent_affordability_sources.json
[client]: https://gitlab.com/DiogoRibeiro7/ine-data-client/-/blob/e60e69ea3a4f149b61b3b2b44c49e8c01be6095a/R/metadata.R
[rights]: https://www.ine.pt/ine_novidades/semin/INEWS66/4/
[licence]: https://creativecommons.org/licenses/by/4.0/
[external]: ../../external/ine-portugal-housing-statistics/README.md
[platform-contract]: https://github.com/DiogoRibeiro7/data-platform-lab/blob/cf1bd2f9de0ecdc95e6f1390c185f00b08df84db/docs/ine-rents-registry-proposal.md
[adoption-policy]: ../../reports/canonical-adoption-policy.json
[handoff]: ../../docs/INGESTION_HANDOFF.md
