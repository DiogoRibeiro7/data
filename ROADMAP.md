# Roadmap

This roadmap defines the intended evolution of the data registry after the
Phase 5 consumer-registry milestone.

It is a planning document, not a promise that every future phase will be
implemented unchanged. Near-term phases are concrete; later phases describe
the capabilities the repository should grow toward.

## Current baseline

The current baseline is the immutable Phase 9 release
`snapshot-2026.10.09` at commit
`caea1de8daec085b0af39525b9c5f8eb7ec5ce37`.

At that point the registry has:

- **4 canonical datasets** with verified checksums and explicit redistribution rights;
- **16 external source records**;
- **2 remaining legacy packages**;
- **4 active canonical consumer relationships** across **3 repositories**;
- **100% canonical dataset adoption coverage**;
- explicit lifecycle and consumer-migration semantics;
- deterministic canonical, external, consumer, provenance-debt, lifecycle, quality, and static-distribution artifacts;
- an installable `diogo-data-registry 0.1.0` client;
- public API version **1** and Python **3.12–3.14** support;
- checksum-verified immutable fetch through the packaged client;
- static machine-readable distribution **v1**;
- snapshot manifest **v6** capturing client and distribution identity;
- immutable snapshot and compatibility/versioning policies.

Phase 10 focuses on long-term preservation, citation, and independently verifiable release trust.

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

**Status:** complete.

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
- [x] snapshot release captures the expanded registry (`snapshot-2026.10.06`).

---

## Phase 8 — Dataset lifecycle, supersession, and version semantics

**Status:** complete.

**Tracking issue:** #126.

### Goal

Define what happens after a canonical dataset is no longer the preferred
version.

The registry already makes snapshots immutable. It still needs explicit
semantics for dataset replacement, deprecation, supersession, and consumer
migration.

### Planned capabilities

- #127 — canonical lifecycle metadata and supersession relationships;
- #128 — lifecycle graph validation and ambiguity prevention;
- #129 — deterministic lifecycle and deprecation reports;
- #130 — lifecycle and replacement lookup in the registry CLI;
- #131 — consumer migration semantics for superseded datasets;
- #132 — lifecycle state in snapshot manifests and summaries;
- #133 — Phase 8 immutable registry snapshot.

### Exit criteria

- canonical datasets can be superseded without deleting historical identity;
- consumers can discover the preferred replacement deterministically;
- deprecated datasets remain citable and reproducible;
- lifecycle state is represented in snapshot manifests.

---

## Phase 9 — Registry client and machine-readable distribution

**Status:** complete.

**Tracking issue:** #146.

### Goal

Turn the repository tooling into a small reusable registry client rather than
requiring consumers to copy command snippets or import scripts from the repo.

### Planned capabilities

- #147 — extract reusable registry core modules;
- #148 — add typed registry models;
- #149 — package the registry client and CLI entry point;
- #150 — add stable programmatic registry APIs;
- #151 — add checksum-verified fetch to the packaged client;
- #152 — publish machine-readable static registry distribution;
- #153 — define client/API/schema compatibility and versioning policy;
- #154 — publish the Phase 9 immutable registry snapshot.

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

**Status:** active.

**Tracking issue:** #165.

### Goal

Make registry releases suitable for long-term scientific and professional
citation beyond GitHub alone.

### Planned capabilities

- #175 — archival preservation policy and snapshot eligibility;
- #176 — deterministic snapshot-to-snapshot diff summaries;
- #177 — machine-readable registry changelog artifacts;
- #178 — deterministic release provenance and attestation metadata;
- #179 — independently verifiable release identity support;
- #180 — archival and DOI metadata for eligible milestone snapshots;
- #181 — external-source disappearance and preservation policy;
- #182 — Phase 10 immutable preservation snapshot.

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
