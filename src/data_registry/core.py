"""Deterministic, offline registry read and lookup primitives."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import fetch as FETCH

LAYER_ORDER = {"canonical": 0, "external": 1, "legacy": 2}
LAYER_CHOICES = ("canonical", "external", "legacy")


class RegistryError(RuntimeError):
    """A user-facing registry operation error."""


@dataclass(frozen=True)
class RegistryEntry:
    """One normalized registry entry."""

    layer: str
    id: str
    title: str
    path: str
    metadata: dict[str, Any]

    @property
    def publisher(self) -> str:
        """Return a publisher/source label when available."""

        if self.layer == "canonical":
            source = self.metadata.get("source")
            if isinstance(source, dict):
                value = source.get("publisher")
                if isinstance(value, str):
                    return value
        if self.layer == "external":
            value = self.metadata.get("publisher")
            if isinstance(value, str):
                return value
        if self.layer == "legacy":
            source = self.metadata.get("source")
            if isinstance(source, dict):
                value = source.get("publisher")
                if isinstance(value, str):
                    return value
        return ""

    @property
    def description(self) -> str:
        """Return a searchable description when present."""

        value = self.metadata.get("description")
        return value if isinstance(value, str) else ""

    @property
    def domains(self) -> list[str]:
        """Return normalized canonical-domain tags."""

        value = self.metadata.get("domain")
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]


def json_compatible(value: Any) -> Any:
    """Convert YAML-native values into JSON-compatible values."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_compatible(item) for item in value]
    return value


def load_metadata(path: Path) -> dict[str, Any]:
    """Load one metadata file as a mapping."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RegistryError(f"{path}: cannot load metadata: {exc}") from exc
    if not isinstance(raw, dict):
        raise RegistryError(f"{path}: metadata root must be a mapping")
    return raw


def _entries_from_layer(root: Path, layer: str) -> list[RegistryEntry]:
    """Load entries from one registry layer."""

    directory_name = {
        "canonical": "datasets",
        "external": "external",
        "legacy": "legacy",
    }[layer]
    layer_root = root / directory_name
    if not layer_root.is_dir():
        return []

    entries: list[RegistryEntry] = []
    for item in sorted(path for path in layer_root.iterdir() if path.is_dir()):
        metadata_path = item / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_metadata(metadata_path)
        entry_id = metadata.get("id")
        title = metadata.get("title")
        if not isinstance(entry_id, str) or not entry_id:
            raise RegistryError(f"{metadata_path}: missing non-empty id")
        if not isinstance(title, str) or not title:
            title = entry_id
        entries.append(
            RegistryEntry(
                layer=layer,
                id=entry_id,
                title=title,
                path=str(item.relative_to(root)),
                metadata=metadata,
            )
        )
    return entries


def load_registry(root: Path) -> list[RegistryEntry]:
    """Load all registry layers deterministically."""

    root = root.resolve()
    entries: list[RegistryEntry] = []
    for layer in LAYER_CHOICES:
        entries.extend(_entries_from_layer(root, layer))
    entries.sort(key=lambda item: (LAYER_ORDER[item.layer], item.id))
    return entries


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    """Load one committed JSON report/graph with registry-style errors."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RegistryError(f"{path}: cannot load {label}: {exc}") from exc
    if not isinstance(raw, dict):
        raise RegistryError(f"{path}: {label} root must be an object")
    return raw


def load_consumer_graph(root: Path) -> dict[str, Any]:
    """Load the generated consumer dependency graph."""

    path = root / "consumers" / "dependency-graph.json"
    raw = _load_json_object(path, "consumer dependency graph")
    consumers = raw.get("consumers")
    datasets = raw.get("datasets")
    if not isinstance(consumers, dict) or not isinstance(datasets, dict):
        raise RegistryError(
            f"{path}: dependency graph must contain consumers and datasets"
        )
    return raw


def consumer_summaries(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Return stable summaries for all registered consumers."""

    consumers = graph["consumers"]
    result: list[dict[str, Any]] = []
    for consumer_id in sorted(consumers):
        payload = consumers[consumer_id]
        if not isinstance(payload, dict):
            raise RegistryError(
                f"consumer {consumer_id!r}: graph entry must be an object"
            )
        datasets = payload.get("datasets")
        if not isinstance(datasets, list):
            raise RegistryError(
                f"consumer {consumer_id!r}: datasets must be a list"
            )
        repository = payload.get("repository")
        normalized_datasets: list[str] = []
        for item in datasets:
            if not isinstance(item, dict):
                raise RegistryError(
                    f"consumer {consumer_id!r}: dataset entries must be objects"
                )
            dataset_id = item.get("dataset_id")
            if not isinstance(dataset_id, str) or not dataset_id:
                raise RegistryError(
                    f"consumer {consumer_id!r}: dataset entry is missing dataset_id"
                )
            normalized_datasets.append(dataset_id)
        result.append(
            {
                "consumer_id": consumer_id,
                "consumer_repository": repository,
                "dataset_count": len(normalized_datasets),
                "datasets": normalized_datasets,
            }
        )
    return result


def find_consumer(graph: dict[str, Any], consumer_id: str) -> dict[str, Any]:
    """Return one exact consumer dependency entry."""

    consumers = graph["consumers"]
    payload = consumers.get(consumer_id)
    if not isinstance(payload, dict):
        raise RegistryError(f"unknown consumer id {consumer_id!r}")
    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        raise RegistryError(f"consumer {consumer_id!r}: datasets must be a list")
    return {
        "consumer_id": consumer_id,
        "consumer_repository": payload.get("repository"),
        "datasets": datasets,
    }


def consumers_for_dataset(
    graph: dict[str, Any],
    dataset_id: str,
    *,
    known_dataset_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return consumers registered for one canonical dataset."""

    datasets = graph["datasets"]
    if (
        dataset_id not in datasets
        and known_dataset_ids is not None
        and dataset_id in known_dataset_ids
    ):
        return []
    payload = datasets.get(dataset_id)
    if not isinstance(payload, dict):
        raise RegistryError(f"unknown consumer dataset id {dataset_id!r}")
    consumers = payload.get("consumers")
    if not isinstance(consumers, list):
        raise RegistryError(f"dataset {dataset_id!r}: consumers must be a list")
    return consumers


def datasets_for_consumer(
    graph: dict[str, Any],
    consumer_id: str,
) -> list[dict[str, Any]]:
    """Return datasets registered for one consumer."""

    return list(find_consumer(graph, consumer_id)["datasets"])


def load_provenance_debt(root: Path) -> dict[str, Any]:
    """Load the committed deterministic provenance-debt report."""

    path = root / "reports" / "provenance-debt.json"
    raw = _load_json_object(path, "provenance debt report")
    items = raw.get("items")
    if not isinstance(items, list):
        raise RegistryError(
            f"{path}: provenance debt report must contain an items list"
        )
    return raw


def filter_debt_items(
    report: dict[str, Any],
    *,
    layer: str = "all",
    category: str | None = None,
    status: str = "all",
) -> list[dict[str, Any]]:
    """Filter provenance-debt items deterministically."""

    raw_items = report.get("items")
    if not isinstance(raw_items, list):
        raise RegistryError("provenance debt report must contain an items list")

    result: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            raise RegistryError("provenance debt items must be objects")
        if layer != "all" and item.get("layer") != layer:
            continue
        if category is not None and item.get("blocker_category") != category:
            continue
        if status != "all" and item.get("review_status") != status:
            continue
        result.append(item)
    return result


def find_debt_item(report: dict[str, Any], item_id: str) -> dict[str, Any]:
    """Return one exact provenance-debt item by ID."""

    matches = [
        item
        for item in filter_debt_items(report)
        if item.get("id") == item_id
    ]
    if not matches:
        raise RegistryError(f"unknown provenance debt id {item_id!r}")
    if len(matches) > 1:
        raise RegistryError(f"provenance debt id {item_id!r} is not unique")
    return matches[0]


def load_lifecycle_report(root: Path) -> dict[str, Any]:
    """Load the committed deterministic lifecycle report."""

    path = root / "reports" / "lifecycle.json"
    raw = _load_json_object(path, "lifecycle report")
    datasets = raw.get("datasets")
    if not isinstance(datasets, list):
        raise RegistryError(
            f"{path}: lifecycle report must contain a datasets list"
        )
    return raw


def find_lifecycle_dataset(
    report: dict[str, Any],
    dataset_id: str,
) -> dict[str, Any]:
    """Return one canonical lifecycle dataset entry."""

    datasets = report.get("datasets")
    if not isinstance(datasets, list):
        raise RegistryError("lifecycle report must contain a datasets list")

    matches = [
        item
        for item in datasets
        if isinstance(item, dict) and item.get("id") == dataset_id
    ]
    if not matches:
        raise RegistryError(f"unknown lifecycle dataset id {dataset_id!r}")
    if len(matches) > 1:
        raise RegistryError(
            f"lifecycle dataset id {dataset_id!r} is not unique"
        )
    return matches[0]


def replacement_payload(
    report: dict[str, Any],
    dataset_id: str,
) -> dict[str, Any]:
    """Return deterministic preferred-replacement information."""

    item = find_lifecycle_dataset(report, dataset_id)
    chain = item.get("replacement_chain")
    if not isinstance(chain, list) or not all(
        isinstance(value, str) for value in chain
    ):
        raise RegistryError(
            f"lifecycle dataset {dataset_id!r}: "
            "replacement_chain must be a string list"
        )
    return {
        "dataset_id": dataset_id,
        "status": item.get("status"),
        "direct_replacement": item.get("direct_replacement"),
        "preferred_dataset_id": item.get("preferred_dataset_id"),
        "replacement_chain": chain,
        "deprecated_at": item.get("deprecated_at"),
        "migration_note": item.get("migration_note"),
    }


def supersedes_payload(
    report: dict[str, Any],
    dataset_id: str,
) -> dict[str, Any]:
    """Return direct and transitive datasets superseded by one dataset."""

    target = find_lifecycle_dataset(report, dataset_id)
    direct = target.get("direct_predecessors")
    if not isinstance(direct, list) or not all(
        isinstance(value, str) for value in direct
    ):
        raise RegistryError(
            f"lifecycle dataset {dataset_id!r}: "
            "direct_predecessors must be a string list"
        )

    datasets = report.get("datasets")
    if not isinstance(datasets, list):
        raise RegistryError("lifecycle report must contain a datasets list")

    transitive: list[str] = []
    for item in datasets:
        if not isinstance(item, dict):
            raise RegistryError("lifecycle dataset entries must be objects")
        item_id = item.get("id")
        chain = item.get("replacement_chain")
        if (
            isinstance(item_id, str)
            and isinstance(chain, list)
            and all(isinstance(value, str) for value in chain)
            and item_id != dataset_id
            and dataset_id in chain[1:]
        ):
            transitive.append(item_id)

    return {
        "dataset_id": dataset_id,
        "direct_predecessors": sorted(direct),
        "superseded_datasets": sorted(transitive),
    }


def filter_layer(
    entries: Iterable[RegistryEntry],
    layer: str,
) -> list[RegistryEntry]:
    """Filter entries by layer or return all."""

    if layer == "all":
        return list(entries)
    return [entry for entry in entries if entry.layer == layer]


def search_entries(
    entries: Iterable[RegistryEntry],
    query: str,
    *,
    layer: str = "all",
) -> list[RegistryEntry]:
    """Search IDs, titles, publishers, descriptions, and domains."""

    needle = query.casefold().strip()
    if not needle:
        return []
    matches: list[RegistryEntry] = []
    for entry in filter_layer(entries, layer):
        haystack = "\n".join(
            [
                entry.id,
                entry.title,
                entry.publisher,
                entry.description,
                *entry.domains,
            ]
        ).casefold()
        if needle in haystack:
            matches.append(entry)
    return matches


def find_entry(
    entries: Iterable[RegistryEntry],
    entry_id: str,
    *,
    layer: str | None = None,
) -> RegistryEntry:
    """Find one exact ID, requiring disambiguation across layers when necessary."""

    matches = [
        entry
        for entry in entries
        if entry.id == entry_id and (layer is None or entry.layer == layer)
    ]
    if not matches:
        suffix = f" in layer {layer}" if layer else ""
        raise RegistryError(f"unknown registry id {entry_id!r}{suffix}")
    if len(matches) > 1:
        layers = ", ".join(entry.layer for entry in matches)
        raise RegistryError(
            f"registry id {entry_id!r} is ambiguous across layers: "
            f"{layers}; use --layer"
        )
    return matches[0]


def entry_summary(entry: RegistryEntry) -> dict[str, Any]:
    """Return a stable compact representation for list/search output."""

    return {
        "layer": entry.layer,
        "id": entry.id,
        "title": entry.title,
        "publisher": entry.publisher or None,
        "domains": entry.domains,
        "path": entry.path,
    }


def show_payload(entry: RegistryEntry) -> dict[str, Any]:
    """Return detailed show output."""

    return {
        "layer": entry.layer,
        "path": entry.path,
        "metadata": json_compatible(entry.metadata),
    }


def canonical_file_metadata(
    entry: RegistryEntry,
    relative_path: str,
) -> dict[str, Any]:
    """Return metadata for one canonical file."""

    if entry.layer != "canonical":
        raise RegistryError("fetch is available only for canonical datasets")
    files = entry.metadata.get("files")
    if not isinstance(files, list):
        raise RegistryError(f"{entry.id}: canonical metadata has no files list")
    for item in files:
        if isinstance(item, dict) and item.get("path") == relative_path:
            return item
    raise RegistryError(
        f"{entry.id}: canonical file {relative_path!r} "
        "is not declared in metadata"
    )


def fetch_entry_file(
    entry: RegistryEntry,
    relative_path: str,
    *,
    commit: str,
    output: Path,
    repository: str = FETCH.DEFAULT_REPOSITORY,
    timeout: float = 60.0,
    force: bool = False,
    base_url: str = FETCH.DEFAULT_RAW_BASE_URL,
) -> tuple[Path, str, str]:
    """Fetch one canonical file using its metadata SHA-256."""

    file_metadata = canonical_file_metadata(entry, relative_path)
    checksum = file_metadata.get("sha256")
    if not isinstance(checksum, str):
        raise RegistryError(f"{entry.id}: {relative_path} has no SHA-256")
    repository_path = f"datasets/{entry.id}/{relative_path}"
    try:
        reference = FETCH.DatasetReference(
            repository=repository,
            commit=commit,
            path=repository_path,
            sha256=checksum,
        )
        result = FETCH.fetch_dataset_file(
            reference,
            output,
            base_url=base_url,
            timeout_seconds=timeout,
            force=force,
        )
    except (ValueError, TypeError, FileExistsError, RuntimeError) as exc:
        raise RegistryError(str(exc)) from exc
    return result, repository_path, checksum
