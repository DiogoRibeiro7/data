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
  --commit <exact-40-character-registry-commit> \
  --verify-local --verify-checkout --json
```

For an offline *metadata-only* plan, omit `--verify-local`. This permits
planning from a sparse checkout, but it does **not** assert that source bytes
were verified. No implicit network requests occur in either mode.

`--verify-local` alone proves local file SHA-256 checksums match the YAML
declarations; it does **not** prove the declared Git commit is the checkout
containing those files. Add `--verify-checkout` to require the repository root,
match `HEAD` to the supplied commit, and confirm that canonical metadata and
every source file have the exact bytes committed in that Git tree. This option
requires `--verify-local` and a Git checkout with the necessary local objects.
It never fetches missing Git objects, invokes a provider, or contacts a service.
This check proves correspondence with the **local** Git tree; it does not
establish that the publisher's Git commit or repository is authentic. Verify
origin separately through a trusted remote or attestation.

The typed Python API exposes the same operation:

```python
from pathlib import Path
from data_registry import RegistryClient

registry = RegistryClient(Path("."))
plan = registry.handoff(
    "ons-gross-median-weekly-pay",
    commit="<exact-40-character-registry-commit>",
    verify_local=True,
    verify_checkout=True,
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
- an optional `checkout_identity_verified` flag, true only when the commit,
  metadata, and source Git blobs were checked. The field is additive to v1;
  older v1 manifests without it remain valid.

The contract is described by
[`schemas/ingestion-handoff-v1.schema.json`](https://github.com/DiogoRibeiro7/data/blob/main/schemas/ingestion-handoff-v1.schema.json).
The schema is also bundled with the Python package.

## Verify received objects offline

After a consumer downloads the objects and places each file at its declared
relative `storage_key`, verify the received bytes without a provider account or
registry checkout:

```bash
data-registry verify-handoff \
  --manifest handoff.json \
  --storage-root /path/to/received-objects \
  --commit <trusted-40-character-registry-commit> \
  --repository DiogoRibeiro7/data \
  --dataset-id ons-gross-median-weekly-pay \
  --json
```

Supply `--commit` from a **trusted source independent of the JSON manifest**;
the manifest must not be allowed to authenticate itself. The repository and
dataset identity checks are optional but recommended. This command validates
the bundled v1 schema, immutable source URLs, source-to-storage-key mappings,
unique file declarations, safe local paths, SHA-256 checksums, and any declared
byte sizes. It returns verified object count, total bytes, and the manifest's
SHA-256. It reads only local files and never contacts a provider or network
service; unrelated files in the storage root are left untouched.

The corresponding typed Python API is also independent of a Git checkout:

```python
from pathlib import Path
from data_registry import verify_handoff_manifest

receipt = verify_handoff_manifest(
    Path("handoff.json"),
    Path("/path/to/received-objects"),
    expected_commit="<trusted-40-character-registry-commit>",
    expected_repository="DiogoRibeiro7/data",
    expected_dataset_id="ons-gross-median-weekly-pay",
)
print(receipt.verified_objects, receipt.total_bytes)
```

This is an **offline integrity-verification result**, not a signed attestation
of publisher origin or a record of completed warehouse ingestion. Source
authenticity and any durable execution record remain the consumer's
responsibility.

### Anchor the handoff to a trusted Git checkout

With the basic command, a manifest containing altered but internally
consistent object hashes could still pass: an expected commit **string** does
not prove those hashes belong to the commit. Where a complete trusted local
checkout is available, add `--trusted-checkout`:

```bash
data-registry verify-handoff \
  --manifest handoff.json \
  --storage-root /path/to/received-objects \
  --commit <trusted-40-character-registry-commit> \
  --repository DiogoRibeiro7/data \
  --trusted-checkout /path/to/pinned-registry-checkout \
  --json
```

This stronger mode requires an independently specified `--repository`.
It regenerates the complete canonical plan from the checkout, confirms that
its `HEAD`, metadata, and **every source file** match the pinned Git tree,
and compares all provenance fields, hashes, formats, keys, and the complete
source file set. Metadata-only and older v1 handoff plans remain valid.
The result reports `trusted_checkout_verified: true` only after these checks
and the received-byte checks pass.

The checkout must contain the required Git objects and canonical source
files. The command does not fetch missing Git objects or access the network.
Even this mode does not authenticate a Git remote's owner, signed release, or
the original publisher: the caller must independently trust the repository
and commit it supplies. Without `--trusted-checkout`, the result explicitly
reports `trusted_checkout_verified: false`.

## Consumer-side execution contract

An ingestion worker can use the plan to implement a storage-neutral workflow:

1. Verify that the checkout metadata matches the exact pinned Git commit,
   ideally by requiring `--verify-checkout`. Do not substitute a floating
   `main` reference.
2. Retrieve only the declared immutable source paths. Do not fetch external
   catalog records or legacy quarantine packages as though they were canonical.
3. Stream to temporary local storage and verify **SHA-256 before promotion**.
   A metadata-only plan is never proof of byte integrity.
4. Publish to the selected destination using the deterministic `storage_key`.
   The provider adapter is responsible for atomic/idempotent promotion.
   Run `verify-handoff` on locally received objects before promoting them.
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
