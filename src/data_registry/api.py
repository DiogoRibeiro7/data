"""Stable programmatic API for deterministic registry reads."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import yaml

from .core import (
    LAYER_CHOICES,
    RegistryEntry,
    RegistryError,
    fetch_entry_file,
    filter_debt_items,
    find_debt_item,
    find_entry,
    find_lifecycle_dataset,
    load_lifecycle_report,
    load_provenance_debt,
    load_registry,
    search_entries,
    supersedes_payload,
)
from .models import (
    CanonicalDataset,
    ConsumerRelationship,
    ExternalRecord,
    LegacyRecord,
    LifecycleDataset,
    ProvenanceDebtItem,
    RegistryModelError,
)

RegistryRecord: TypeAlias = CanonicalDataset | ExternalRecord | LegacyRecord


@dataclass(frozen=True)
class FetchResult:
    """Verified immutable canonical fetch result."""

    dataset_id: str
    repository: str
    commit: str
    path: str
    sha256: str
    output: Path


@dataclass(frozen=True)
class RegistryClient:
    """Typed, deterministic, offline client for one registry checkout."""

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    def _entries(self) -> list[RegistryEntry]:
        return load_registry(self.root)

    @staticmethod
    def _typed_entry(entry: RegistryEntry) -> RegistryRecord:
        if entry.layer == "canonical":
            return CanonicalDataset.from_mapping(entry.metadata)
        if entry.layer == "external":
            return ExternalRecord.from_mapping(entry.metadata)
        if entry.layer == "legacy":
            return LegacyRecord.from_mapping(entry.metadata)
        raise RegistryError(f"unsupported registry layer: {entry.layer}")

    def list(self, *, layer: str = "all") -> tuple[RegistryRecord, ...]:
        """Return registry records in stable layer/ID order."""

        if layer != "all" and layer not in LAYER_CHOICES:
            raise RegistryError(f"unknown registry layer {layer!r}")
        entries = self._entries()
        if layer != "all":
            entries = [entry for entry in entries if entry.layer == layer]
        return tuple(self._typed_entry(entry) for entry in entries)

    def search(
        self,
        query: str,
        *,
        layer: str = "all",
    ) -> tuple[RegistryRecord, ...]:
        """Search registry records without network access."""

        if layer != "all" and layer not in LAYER_CHOICES:
            raise RegistryError(f"unknown registry layer {layer!r}")
        matches = search_entries(self._entries(), query, layer=layer)
        return tuple(self._typed_entry(entry) for entry in matches)

    def get(
        self,
        record_id: str,
        *,
        layer: str | None = None,
    ) -> RegistryRecord:
        """Return one exact typed registry record."""

        if layer is not None and layer not in LAYER_CHOICES:
            raise RegistryError(f"unknown registry layer {layer!r}")
        entry = find_entry(self._entries(), record_id, layer=layer)
        return self._typed_entry(entry)

    def canonical(self, dataset_id: str) -> CanonicalDataset:
        """Return one canonical dataset by exact ID."""

        record = self.get(dataset_id, layer="canonical")
        if not isinstance(record, CanonicalDataset):
            raise RegistryError(f"{dataset_id!r} is not canonical")
        return record

    def external(self, source_id: str) -> ExternalRecord:
        """Return one external source record by exact ID."""

        record = self.get(source_id, layer="external")
        if not isinstance(record, ExternalRecord):
            raise RegistryError(f"{source_id!r} is not external")
        return record

    def legacy(self, record_id: str) -> LegacyRecord:
        """Return one legacy quarantine record by exact ID."""

        record = self.get(record_id, layer="legacy")
        if not isinstance(record, LegacyRecord):
            raise RegistryError(f"{record_id!r} is not legacy")
        return record

    def _consumer_relationships(self) -> tuple[ConsumerRelationship, ...]:
        consumers_root = self.root / "consumers"
        if not consumers_root.is_dir():
            return ()

        relationships: list[ConsumerRelationship] = []
        for path in sorted(consumers_root.glob("*/*.yaml")):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                raise RegistryError(f"{path}: cannot load consumer metadata: {exc}") from exc
            if not isinstance(raw, dict):
                raise RegistryError(f"{path}: consumer metadata root must be an object")
            relationships.append(ConsumerRelationship.from_mapping(raw))

        relationships.sort(
            key=lambda item: (item.consumer_id, item.dataset_id)
        )
        return tuple(relationships)

    def consumers(self) -> tuple[ConsumerRelationship, ...]:
        """Return every consumer relationship deterministically."""

        return self._consumer_relationships()

    def consumer(self, consumer_id: str) -> tuple[ConsumerRelationship, ...]:
        """Return all relationships for one consumer."""

        matches = tuple(
            item
            for item in self._consumer_relationships()
            if item.consumer_id == consumer_id
        )
        if not matches:
            raise RegistryError(f"unknown consumer id {consumer_id!r}")
        return matches

    def consumers_for_dataset(
        self,
        dataset_id: str,
    ) -> tuple[ConsumerRelationship, ...]:
        """Return relationships referencing one canonical dataset."""

        self.canonical(dataset_id)
        return tuple(
            item
            for item in self._consumer_relationships()
            if item.dataset_id == dataset_id
        )

    def fetch(
        self,
        dataset_id: str,
        relative_path: str,
        *,
        commit: str,
        output: Path,
        repository: str = "DiogoRibeiro7/data",
        timeout: float = 60.0,
        force: bool = False,
        base_url: str = "https://raw.githubusercontent.com",
    ) -> FetchResult:
        """Fetch one canonical file using registry metadata identity.

        The caller supplies only the exact Git commit and canonical relative
        file path. SHA-256 is resolved from committed canonical metadata.
        """

        entry = find_entry(self._entries(), dataset_id, layer="canonical")
        try:
            result, repository_path, checksum = fetch_entry_file(
                entry,
                relative_path,
                commit=commit,
                output=output,
                repository=repository,
                timeout=timeout,
                force=force,
                base_url=base_url,
            )
        except RegistryError:
            raise
        return FetchResult(
            dataset_id=dataset_id,
            repository=repository,
            commit=commit,
            path=repository_path,
            sha256=checksum,
            output=result,
        )

    def provenance_debt(
        self,
        *,
        layer: str = "all",
        category: str | None = None,
        status: str = "all",
    ) -> tuple[ProvenanceDebtItem, ...]:
        """Return typed provenance/licensing debt items."""

        if layer not in {"all", "external", "legacy"}:
            raise RegistryError(f"unknown provenance debt layer {layer!r}")
        if status not in {"all", "actionable", "terminal"}:
            raise RegistryError(f"unknown provenance debt status {status!r}")

        report = load_provenance_debt(self.root)
        items = filter_debt_items(
            report,
            layer=layer,
            category=category,
            status=status,
        )
        typed = [ProvenanceDebtItem.from_mapping(item) for item in items]
        typed.sort(key=lambda item: (item.layer, item.id))
        return tuple(typed)

    def provenance_debt_item(self, item_id: str) -> ProvenanceDebtItem:
        """Return one exact provenance/licensing debt item."""

        raw = find_debt_item(load_provenance_debt(self.root), item_id)
        return ProvenanceDebtItem.from_mapping(raw)

    def lifecycle(self, dataset_id: str) -> LifecycleDataset:
        """Return lifecycle state for one canonical dataset."""

        raw = find_lifecycle_dataset(
            load_lifecycle_report(self.root),
            dataset_id,
        )
        return LifecycleDataset.from_mapping(raw)

    def preferred_replacement(
        self,
        dataset_id: str,
    ) -> LifecycleDataset | None:
        """Return the preferred terminal dataset, or None when unavailable."""

        lifecycle = self.lifecycle(dataset_id)
        preferred_id = lifecycle.preferred_dataset_id
        if preferred_id is None:
            return None
        return self.lifecycle(preferred_id)

    def superseded_by(
        self,
        dataset_id: str,
    ) -> tuple[LifecycleDataset, ...]:
        """Return historical datasets whose replacement chain reaches dataset_id."""

        report = load_lifecycle_report(self.root)
        payload = supersedes_payload(report, dataset_id)
        dataset_ids = payload["superseded_datasets"]
        if not isinstance(dataset_ids, list):
            raise RegistryError("superseded_datasets must be a list")
        return tuple(
            LifecycleDataset.from_mapping(
                find_lifecycle_dataset(report, item_id)
            )
            for item_id in dataset_ids
        )


__all__ = [
    "FetchResult",
    "RegistryClient",
    "RegistryModelError",
    "RegistryRecord",
]
