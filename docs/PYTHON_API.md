# Python API

The installable client exposes a deterministic, typed Python API for registry reads.

```python
from pathlib import Path

from data_registry import RegistryClient

registry = RegistryClient(Path("/path/to/data"))
```

All read operations use committed files under the supplied registry root. They perform no implicit network access.

## Registry records

List every registry record in stable layer/ID order:

```python
records = registry.list()
```

Filter by layer:

```python
canonical = registry.list(layer="canonical")
external = registry.list(layer="external")
legacy = registry.list(layer="legacy")
```

Search IDs, titles, publishers, descriptions, and domain tags:

```python
matches = registry.search("refugee")
matches = registry.search("retail", layer="canonical")
```

Resolve one exact record:

```python
record = registry.get("online-retail-ii")
dataset = registry.canonical("online-retail-ii")
source = registry.external("medium-crawlfeeds-corpus")
legacy = registry.legacy("country-age-sex-2019")
```

Returned values are strict typed models: `CanonicalDataset`, `ExternalRecord`, and `LegacyRecord`.

Ambiguous IDs require an explicit layer. Unknown IDs raise `RegistryError`.

## Consumer relationships

```python
relationships = registry.consumers()
relationships = registry.consumer("displacement-risk-lab-dynamodb")
relationships = registry.consumers_for_dataset("unhcr-refugee-population-2024")
```

These methods return `ConsumerRelationship` instances in deterministic order.

## Provenance and licensing debt

```python
items = registry.provenance_debt()
items = registry.provenance_debt(layer="external")
items = registry.provenance_debt(status="terminal")
item = registry.provenance_debt_item("pordata-portugal-resident-population")
```

Returned values are `ProvenanceDebtItem` models.

Supported filters match the CLI: layer is `all`, `external`, or `legacy`; status is `all`, `actionable`, or `terminal`; blocker category is an exact text match when supplied.

## Lifecycle and replacement state

```python
state = registry.lifecycle("online-retail-ii")
preferred = registry.preferred_replacement("online-retail-ii")
history = registry.superseded_by("replacement-dataset-id")
```

Lifecycle methods return `LifecycleDataset` models.

`preferred_replacement()` returns the preferred terminal lifecycle record or `None` when no preferred dataset is recorded.

`superseded_by()` returns historical datasets whose replacement chain reaches the selected dataset.

## Error contract

Public read methods raise `RegistryError` for operational lookup errors such as unknown IDs, ambiguous IDs, invalid layer/filter values, and malformed generated report/graph files.

Typed model construction raises `RegistryModelError` when committed data does not match the supported record contract. The API does not silently coerce unsupported schema versions.

## Network behavior

Registry reads are offline by design. Network I/O occurs only through an explicit immutable fetch.

## Checksum-verified canonical fetch

`RegistryClient.fetch()` resolves the repository path and expected SHA-256 from
committed canonical metadata. Callers provide an exact 40-character commit:

```python
result = registry.fetch(
    "online-retail-ii",
    "raw/online_retail_II.xlsx",
    commit="<40-character-git-sha>",
    output="data/online_retail_II.xlsx",
)
```

The returned `FetchResult` records:

- canonical dataset ID;
- repository;
- exact commit;
- canonical repository path;
- expected/verified SHA-256;
- local output path.

Fetch semantics are strict:

- branch names and other floating refs are rejected;
- a checksum mismatch is fatal and the bad download is not accepted;
- writes are atomic;
- an existing local file with the expected checksum is reused without network access;
- an existing mismatched local file requires `force=True`;
- network access occurs only when the local verified copy cannot satisfy the request.

The installed CLI `data-registry fetch ...`, the compatibility script, and
`RegistryClient.fetch()` all use the same `data_registry.core.fetch_entry_file`
implementation.
