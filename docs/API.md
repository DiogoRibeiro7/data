# Python API

The installable `diogo-data-registry` package exposes a typed, deterministic
Python API through `RegistryClient`.

Registry reads are offline. No method below performs implicit network access.

## Create a client

Point the client at a checked-out registry root:

```python
from data_registry import RegistryClient

registry = RegistryClient("/path/to/data")
```

`pathlib.Path` values are also accepted.

## Canonical, external, and legacy records

Exact typed lookup:

```python
dataset = registry.canonical("online-retail-ii")
print(dataset.title)
print(dataset.publisher)

source = registry.external("medium-crawlfeeds-corpus")
legacy = registry.legacy("country-age-sex-2019")
```

Generic exact lookup is available through `get()`. When the same ID exists in
multiple layers, omit the layer only if the ID is unambiguous:

```python
record = registry.get("online-retail-ii")
record = registry.get("online-retail-ii", layer="canonical")
```

Unknown or ambiguous IDs raise `RegistryError`.

## List and search

Results are tuples in deterministic registry order:

```python
all_records = registry.list()
canonical = registry.list(layer="canonical")
matches = registry.search("refugee")
matches = registry.search("population", layer="canonical")
```

Records are returned as typed models:

- `CanonicalDataset`
- `ExternalRecord`
- `LegacyRecord`

## Consumer relationships

Consumer APIs read committed relationship YAML records and return
`ConsumerRelationship` models:

```python
all_relationships = registry.consumers()

relationships = registry.consumer("displacement-risk-lab-dynamodb")

users = registry.consumers_for_dataset(
    "unhcr-refugee-population-2024"
)
```

A known canonical dataset with no registered consumers returns an empty tuple.
An unknown dataset or consumer raises `RegistryError`.

## Provenance and licensing debt

```python
items = registry.provenance_debt()
actionable = registry.provenance_debt(status="actionable")
legacy = registry.provenance_debt(layer="legacy")

item = registry.provenance_debt_item("medium-crawlfeeds-corpus")
```

Results are `ProvenanceDebtItem` models.

The supported filters match the CLI semantics:

- layer: `all`, `external`, `legacy`
- status: `all`, `actionable`, `terminal`
- optional blocker category

## Lifecycle and replacement lookup

```python
state = registry.lifecycle("online-retail-ii")

preferred = registry.preferred_replacement("online-retail-ii")

history = registry.superseded_by("some-current-dataset")
```

These APIs return `LifecycleDataset` models.

`preferred_replacement()` returns the preferred terminal lifecycle record
identified by the committed lifecycle report. For an active current dataset,
that is the dataset itself.

## Serialization

Typed records preserve the committed source mapping and can be converted back
without losing source-specific fields:

```python
payload = dataset.to_mapping()
```

The returned mapping is detached and mutable; modifying it does not mutate the
model.

## Errors

Public read APIs use:

```python
from data_registry import RegistryError, RegistryModelError
```

- `RegistryError` covers lookup, ambiguity, filter, and registry-read errors.
- `RegistryModelError` means committed/public data does not satisfy the
  supported typed contract.

The client does not silently coerce unsupported schema versions.

## Network boundary

The methods documented on this page perform no network access.

Checksum-verified immutable fetching is an explicit operation and is handled
separately by the fetch API/CLI.
