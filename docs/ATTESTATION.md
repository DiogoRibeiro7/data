# Snapshot release provenance

Every new immutable registry snapshot release includes a deterministic
`snapshot-provenance.json` record alongside the manifest and summary.

The provenance record binds the release identity to the exact release-material
bytes and to the committed producer configuration. It contains no runtime
timestamp, workflow run ID, actor name, or other environment-dependent value.

## Provenance contract

The schema is:

`schemas/snapshot-provenance-v1.schema.json`

Version 1 records:

- repository identity;
- exact snapshot tag and 40-character release commit;
- SHA-256 of `snapshot-manifest.json`;
- SHA-256 of `snapshot-summary.md`;
- SHA-256 of the committed snapshot generator;
- SHA-256 of the repository snapshot-release workflow;
- exact commit of the reusable publisher workflow;
- package/API/static-distribution/manifest versions;
- deterministic assertions that the snapshot generator itself verified.

The predicate type is:

`https://github.com/DiogoRibeiro7/data/attestations/snapshot-provenance/v1`

## Assertions

Assertions with `result: pass` describe checks that are a deterministic
precondition or direct consequence of successful snapshot generation, including:

- snapshot tag syntax/date validation;
- exact commit-SHA syntax validation;
- canonical-file checksum verification;
- readable metadata schemas and generated registry state;
- readable client/static-distribution state;
- successful deterministic summary rendering.

The record does **not** claim a GitHub Actions run ID, actor identity, wall-clock
time, or third-party signature. Those are deliberately excluded from this
deterministic payload.

Repository CI/release workflow checks are a separate execution record. The
committed workflow itself is bound by SHA-256 and the exact reusable publisher
commit is recorded.

## Independent verification

Given the three release assets:

```text
snapshot-manifest.json
snapshot-summary.md
snapshot-provenance.json
```

verify the two bound digests:

```bash
sha256sum snapshot-manifest.json snapshot-summary.md
```

Compare those values with:

- `artifacts.manifest.sha256`;
- `artifacts.summary.sha256`.

Then verify the snapshot identity in both the provenance record and manifest:

- tag;
- exact commit;
- manifest version.

For a full producer verification, check out the recorded release commit and
recompute SHA-256 for:

- `scripts/create_snapshot.py`;
- `.github/workflows/snapshot-release.yml`.

The workflow file must contain the same exact reusable publisher commit recorded
under `producer.reusable_publisher.ref`.

## Determinism

For the same repository bytes, snapshot tag, and commit, all three release
artifacts are byte-for-byte deterministic.

The provenance file intentionally has no back-reference from the snapshot
manifest. This avoids a digest cycle: provenance can bind the manifest and
summary without changing the historical snapshot-manifest compatibility
contract.

## Historical releases

Snapshots published before this provenance contract remain valid historical
release identities. They simply do not carry `snapshot-provenance.json`.

No historical release is rewritten to retrofit an attestation.

## Trust boundary

This deterministic provenance record is evidence about release construction and
artifact identity. It is not by itself a cryptographic signature of the Git tag
or publisher identity.

Independent/verifiable release identity is addressed separately by Phase 10
issue #179.
