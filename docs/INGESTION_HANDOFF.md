# Provider-neutral ingestion handoff

The registry is the source of truth for **which exact dataset bytes may be
consumed**. A separate data-engineering platform may ingest, transform, and
serve those bytes using local disk, DVC, PostgreSQL, object storage, or another
provider chosen later. The registry does not operate that platform.

This boundary preserves the current data policy: no mutable warehouse tables,
application state, generated outputs, credentials, or unreviewed upstream data
are committed to this repository.

## Generate an ingestion plan

Check out an exact registry commit and create the handoff plan:

```bash
git checkout <exact-40-character-registry-commit>
data-registry --root . handoff ons-gross-median-weekly-pay \
  --commit <exact-40-character-registry-commit> --verify-local --json
```

For an offline *metadata-only* plan, omit `--verify-local`. This permits
planning from a sparse checkout, but it does **not** assert that source bytes
were verified. No implicit network requests occur in either mode.

The typed Python API exposes the same operation:

```python
from pathlib import Path
from data_registry import RegistryClient

registry = RegistryClient(Path("."))
plan = registry.handoff(
    "ons-gross-median-weekly-pay",
    commit="<exact-40-character-registry-commit>",
    verify_local=True,
)
payload = plan.to_mapping()
```

The manifest includes:

- schema version, canonical dataset ID, title, and lifecycle status;
- pinned GitHub repository and full Git commit;
- upstream publisher, source URL, snapshot, retrieval date, licence, citation;
- immutable source URL, source repository path, SHA-256, format, and role for
  each declared canonical object;
- a stable relative destination key of the form
  `canonical/<dataset-id>/<sha256>/<raw-or-derived>/<filename>`;
- an explicit flag showing whether local source bytes were SHA-256 verified.

The contract is described by
[`schemas/ingestion-handoff-v1.schema.json`](https://github.com/DiogoRibeiro7/data/blob/main/schemas/ingestion-handoff-v1.schema.json).
The schema is also bundled with the Python package.

## Consumer-side execution contract

An ingestion worker can use the plan to implement a storage-neutral workflow:

1. Verify that the checkout metadata matches the exact pinned Git commit. Do
   not substitute a floating `main` reference.
2. Retrieve only the declared immutable source paths. Do not fetch external
   catalog records or legacy quarantine packages as though they were canonical.
3. Stream to temporary local storage and verify **SHA-256 before promotion**.
   A metadata-only plan is never proof of byte integrity.
4. Publish to the selected destination using the deterministic `storage_key`.
   The provider adapter is responsible for atomic/idempotent promotion.
5. Persist an execution record outside this repository containing the handoff
   version, source commit/path/checksum, destination URI, run identifier, and
   verification outcome.
6. Keep downstream Bronze/Silver/Gold datasets and transformations outside
   this registry. Any derived artifact republished here must separately pass
   the canonical promotion and licensing rules.

Handoff manifests are plans, **not ingestion receipts**. They never create
tables, download datasets, upload objects, or claim that a storage provider is
configured. They do not authorize redistribution beyond the recorded licence
terms; downstream users remain responsible for attribution and permissible use.

## What stays undecided

No cloud account, bucket, database, billing method, or credential is required
to use this interface. A future consumer may implement a local filesystem or
DVC backend first, then select PostgreSQL/object-storage providers based on
actual workload and cost. Registry contracts do not change when that happens.

## Suggested Data Engineering showcase

Build the orchestration, transformations, observability, lineage, and API layer
in a **separate consumer repository**. Start with one approved canonical source
and small synthetic CI fixtures. Test checksum failures, retries, incremental
ingestion, replays, data-vintage preservation, and schema drift without adding
network access to the registry's standard validation workflow.

See [the consumer guide](CONSUMERS.md), [data policy](DATA_POLICY.md), and
[Python API](PYTHON_API.md) for the governing contracts.
