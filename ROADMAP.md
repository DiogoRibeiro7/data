# Roadmap

This roadmap defines the intended evolution of the data registry after the
Phase 5 consumer-registry milestone.

It is a planning document, not a promise that every future phase will be
implemented unchanged. Near-term phases are concrete; later phases describe
the capabilities the repository should grow toward.

## Current baseline

The Phase 7 baseline is the immutable release
`snapshot-2026.10.05` at commit
`91f0ff2d5580313137fba4908d4f793c4b577823`.

At that point the registry has:

- **2 canonical datasets** with verified checksums and explicit redistribution
  rights;
- **13 external source records**;
- **2 remaining legacy packages**;
- **2 active canonical consumer relationships**;
- **100% canonical dataset adoption coverage**;
- deterministic canonical, external, and consumer catalogs;
- a reverse consumer dependency graph;
- offline repository validation;
- scheduled external-source and consumer-contract health checks;
- immutable snapshot manifests that include the consumer registry.

The next phases should improve trust, lifecycle management, adoption, and
long-term preservation rather than simply increasing dataset count.

---

## Phase 6 — Provenance and licensing debt

**Status:** complete.

**Tracking issue:** #84

### Goal

Make unresolved provenance and redistribution questions a structured,
measurable registry lifecycle and reduce the current debt.

### Current debt

- 5 external records with unresolved redistribution state;
- 2 legacy packages still in quarantine.

### Planned work

- #85 — structured provenance-resolution evidence;
- #86 — deterministic provenance/licensing debt queue;
- #87 — UNHCR and IBM Telco re-audit;
- #88 — DGS and PORDATA redistribution re-audit;
- #89 — maize licence scope and final legacy-package decisions;
- #90 — provenance-debt CLI and quality metrics;
- #91 — Phase 6 immutable snapshot.

### Exit criteria

Phase 6 is complete when:

- unresolved records carry explicit blocker/evidence metadata;
- actionable and terminal debt are distinguishable;
- both remaining legacy packages have explicit terminal dispositions;
- the CLI and quality report expose provenance debt;
- the unresolved external backlog is materially reduced or terminally
  classified;
- a new immutable snapshot captures the resulting state.

---

## Phase 7 — Expand the canonical registry from real demand

**Status:** release-ready; immutable snapshot pending (#107).

**Tracking issue:** #101

### Goal

Grow the canonical layer only where a maintained downstream project has a real
need for an immutable, reusable dataset.

### Priorities

1. identify maintained repositories still downloading reusable public data
   directly;
2. prefer sources with explicit redistribution rights and stable snapshot
   identity;
3. promote datasets only when the canonical contract is fully satisfied;
4. migrate at least one real consumer for every new canonical dataset;
5. register the consumer relationship immediately;
6. include every expansion in an immutable registry snapshot.

### Likely work

- account-wide consumer discovery;
- candidate scoring by provenance, licence clarity, stability, size, and reuse;
- promotion of two or more additional datasets;
- downstream migrations to exact commit/path/SHA-256 contracts;
- removal of redundant downstream copies where safe;
- documentation and citation updates.

### Exit criteria

- [x] at least **4 canonical datasets** in total;
- [x] every newly promoted dataset has at least one real registered consumer;
- [x] no new unresolved redistribution debt is introduced by promotion;
- [x] canonical consumer coverage remains explicit and reproducible;
- [ ] snapshot release captures the expanded registry (#107).

---

## Phase 8 — Dataset lifecycle, supersession, and version semantics

**Status:** planned.

### Goal

Define what happens after a canonical dataset is no longer the preferred
version.

The registry already makes snapshots immutable. It still needs explicit
semantics for dataset replacement, deprecation, supersession, and consumer
migration.

### Planned capabilities

- canonical dataset lifecycle states;
- `supersedes` / `superseded_by` relationships;
- version lineage between canonical snapshots;
- deprecation metadata and dates;
- compatibility notes for schema-changing replacements;
- consumer migration status;
- CLI commands for lifecycle and replacement lookup;
- validation that prevents ambiguous active replacements;
- generated lifecycle/deprecation reports.

### Exit criteria

- canonical datasets can be superseded without deleting historical identity;
- consumers can discover the preferred replacement deterministically;
- deprecated datasets remain citable and reproducible;
- lifecycle state is represented in snapshot manifests.

---

## Phase 9 — Registry client and machine-readable distribution

**Status:** planned.

### Goal

Turn the repository tooling into a small reusable registry client rather than
requiring consumers to copy command snippets or import scripts from the repo.

### Planned capabilities

- package the registry reader/fetcher as a Python package;
- stable programmatic API for:
  - dataset lookup;
  - checksum-verified fetch;
  - consumer lookup;
  - provenance/debt lookup;
  - lifecycle lookup;
- typed models for canonical, external, consumer, and provenance records;
- machine-readable static registry endpoints suitable for automation;
- CLI installed as an entry point instead of invoked only through
  `python scripts/registry.py`;
- backward-compatibility policy for schema/API versions.

### Non-goal

This phase should **not** create a stateful web service or database unless a
real consumer requires one. The Git repository remains the source of truth.

### Exit criteria

- downstream projects can depend on a released client version;
- registry reads remain deterministic and offline-capable;
- fetching still requires exact immutable identity and checksum verification;
- repository scripts and packaged client share one implementation path.

---

## Phase 10 — Archival preservation, citation, and trust

**Status:** long-term.

### Goal

Make registry releases suitable for long-term scientific and professional
citation beyond GitHub alone.

### Planned capabilities

- archive selected immutable snapshots in a preservation service such as
  Zenodo;
- DOI-backed citation for milestone releases where appropriate;
- release provenance/attestation metadata;
- signed or otherwise verifiable release identities;
- snapshot-to-snapshot diff summaries;
- machine-readable changelog of:
  - added/removed canonical datasets;
  - consumer changes;
  - provenance/licensing resolutions;
  - lifecycle transitions;
- preservation policy for external records whose upstream source disappears.

### Exit criteria

- milestone snapshots have durable archival identifiers;
- a user can reconstruct what changed between releases;
- citations can distinguish registry tooling, registry snapshots, and upstream
  datasets cleanly;
- preservation does not weaken upstream licence obligations.

---

## Continuous work

The following are not separate phases. They apply throughout the roadmap.

### Validation and CI

- keep baseline validation deterministic and offline;
- test every new metadata contract;
- keep generated artifacts under freshness checks;
- do not add network calls to ordinary repository validation.

### Health monitoring

- keep external-source and consumer-contract health checks conservative;
- distinguish transient failures from actionable drift;
- avoid noisy high-frequency scheduled checks.

### Documentation

- update README, MkDocs, CLI reference, schemas, and policy docs when contracts
  change;
- prefer generated tables/reports over manually maintained inventories where
  possible.

### Consumer discipline

- never use floating `main` URLs for reproducible canonical consumption;
- pin exact commit, path, and SHA-256;
- keep synthetic fixtures distinct from canonical source data.

### Licensing and privacy

- never infer dataset redistribution rights from a code licence without
  evidence that the data is covered;
- do not commit private, personal, confidential, regulated, or
  redistribution-restricted data;
- preserve upstream attribution and citation requirements.

---

## What this repository should not become

The registry is intentionally **not**:

- a generic data dump;
- a personal data lake;
- a mirror of every public dataset used once;
- a replacement for authoritative upstream providers;
- a mutable "latest data" bucket;
- a place to store large data merely because Git can technically hold it.

The durable model is:

> identify reusable data, prove its provenance and redistribution basis, pin
> immutable bytes when justified, register real consumers, and preserve the
> resulting state through immutable snapshots.

---

## Roadmap maintenance

When a phase becomes active:

1. create a parent tracking issue;
2. create the complete first batch of child issues before implementation;
3. add dependencies and exit criteria;
4. update this roadmap if the phase scope changes materially;
5. close the phase only after its immutable snapshot is published.

Future phases should be split, reordered, or removed when repository evidence
shows a better path. The roadmap exists to make the work coherent, not to force
work that no longer has value.
