"""Strict typed models for public registry records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, ClassVar


class RegistryModelError(ValueError):
    """A public registry record does not match its supported contract."""


def _freeze(value: Any) -> Any:
    """Recursively freeze mappings/lists while preserving scalar values."""

    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    """Return a plain mapping/list structure suitable for serialization."""

    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _mapping(value: Any, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RegistryModelError(f"{field} must be an object")
    return value


def _schema_v1(value: Mapping[str, Any], *, record: str) -> None:
    if value.get("schema_version") != 1:
        raise RegistryModelError(f"{record}.schema_version must be 1")


def _text(
    value: Mapping[str, Any],
    key: str,
    *,
    record: str,
    allow_empty: bool = False,
) -> str:
    item = value.get(key)
    if not isinstance(item, str) or (not allow_empty and not item):
        raise RegistryModelError(f"{record}.{key} must be non-empty text")
    return item


def _optional_text(value: Mapping[str, Any], key: str, *, record: str) -> str | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, str) or not item:
        raise RegistryModelError(f"{record}.{key} must be non-empty text or null")
    return item


def _enum(
    value: Mapping[str, Any],
    key: str,
    choices: set[str],
    *,
    record: str,
) -> str:
    item = _text(value, key, record=record)
    if item not in choices:
        rendered = ", ".join(sorted(choices))
        raise RegistryModelError(f"{record}.{key} must be one of: {rendered}")
    return item


def _string_tuple(value: Any, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise RegistryModelError(f"{field} must be a list of non-empty strings")
    return tuple(value)


@dataclass(frozen=True)
class CanonicalDataset:
    """Typed projection of canonical dataset metadata schema v1."""

    SCHEMA_VERSION: ClassVar[int] = 1

    id: str
    title: str
    description: str
    domain: tuple[str, ...]
    publisher: str
    source_snapshot: str
    redistribution: str
    lifecycle_status: str
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CanonicalDataset":
        record = "canonical"
        raw = _mapping(raw, field=record)
        _schema_v1(raw, record=record)
        source = _mapping(raw.get("source"), field="canonical.source")
        license_data = _mapping(raw.get("license"), field="canonical.license")
        files = raw.get("files")
        if not isinstance(files, (list, tuple)) or not files:
            raise RegistryModelError("canonical.files must be a non-empty list")
        for index, item in enumerate(files):
            file_record = _mapping(item, field=f"canonical.files[{index}]")
            _text(file_record, "path", record=f"canonical.files[{index}]")
            _enum(
                file_record,
                "role",
                {"raw", "derived"},
                record=f"canonical.files[{index}]",
            )
            _text(file_record, "format", record=f"canonical.files[{index}]")
            checksum = _text(
                file_record,
                "sha256",
                record=f"canonical.files[{index}]",
            )
            if len(checksum) != 64:
                raise RegistryModelError(
                    f"canonical.files[{index}].sha256 must contain 64 characters"
                )

        lifecycle = raw.get("lifecycle")
        lifecycle_status = "active"
        if lifecycle is not None:
            lifecycle_map = _mapping(lifecycle, field="canonical.lifecycle")
            lifecycle_status = _enum(
                lifecycle_map,
                "status",
                {"active", "deprecated", "superseded"},
                record="canonical.lifecycle",
            )

        return cls(
            id=_text(raw, "id", record=record),
            title=_text(raw, "title", record=record),
            description=_text(raw, "description", record=record),
            domain=_string_tuple(raw.get("domain"), field="canonical.domain"),
            publisher=_text(source, "publisher", record="canonical.source"),
            source_snapshot=_text(source, "snapshot", record="canonical.source"),
            redistribution=_enum(
                license_data,
                "redistribution",
                {"allowed", "restricted", "unknown"},
                record="canonical.license",
            ),
            lifecycle_status=lifecycle_status,
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)


@dataclass(frozen=True)
class ExternalRecord:
    """Typed projection of external-source metadata schema v1."""

    SCHEMA_VERSION: ClassVar[int] = 1

    id: str
    title: str
    publisher: str
    source_url: str
    redistribution: str | None
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ExternalRecord":
        record = "external"
        raw = _mapping(raw, field=record)
        _schema_v1(raw, record=record)
        if raw.get("status") != "external-reference":
            raise RegistryModelError(
                "external.status must be 'external-reference'"
            )
        if "storage" not in raw and "usage" not in raw:
            raise RegistryModelError("external requires storage or usage metadata")

        redistribution = raw.get("redistribution")
        if redistribution is None:
            usage = raw.get("usage")
            if isinstance(usage, Mapping):
                redistribution = usage.get("redistribution")
        if redistribution is not None and not isinstance(redistribution, str):
            raise RegistryModelError("external redistribution must be text or null")

        return cls(
            id=_text(raw, "id", record=record),
            title=_text(raw, "title", record=record),
            publisher=_text(raw, "publisher", record=record),
            source_url=_text(raw, "source_url", record=record),
            redistribution=redistribution,
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)


@dataclass(frozen=True)
class ConsumerRelationship:
    """Typed projection of canonical consumer relationship metadata v1."""

    SCHEMA_VERSION: ClassVar[int] = 1

    status: str
    consumer_id: str
    consumer_repository: str
    dataset_id: str
    registry_commit: str
    path: str
    sha256: str
    migration_status: str | None
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ConsumerRelationship":
        record = "consumer"
        raw = _mapping(raw, field=record)
        _schema_v1(raw, record=record)
        status = _enum(raw, "status", {"active", "deprecated"}, record=record)
        if raw.get("registry_layer") != "canonical":
            raise RegistryModelError("consumer.registry_layer must be 'canonical'")
        if raw.get("registry_repository") != "DiogoRibeiro7/data":
            raise RegistryModelError(
                "consumer.registry_repository must be 'DiogoRibeiro7/data'"
            )

        commit = _text(raw, "registry_commit", record=record)
        if len(commit) != 40:
            raise RegistryModelError(
                "consumer.registry_commit must contain 40 characters"
            )
        sha256 = _text(raw, "sha256", record=record)
        if len(sha256) != 64:
            raise RegistryModelError("consumer.sha256 must contain 64 characters")

        migration_status: str | None = None
        migration = raw.get("migration")
        if migration is not None:
            migration_map = _mapping(migration, field="consumer.migration")
            migration_status = _enum(
                migration_map,
                "status",
                {"required", "planned", "migrated", "retained"},
                record="consumer.migration",
            )
            if migration_status in {"planned", "migrated"}:
                _text(
                    migration_map,
                    "target_dataset_id",
                    record="consumer.migration",
                )
            if migration_status == "retained":
                _text(migration_map, "rationale", record="consumer.migration")

        return cls(
            status=status,
            consumer_id=_text(raw, "consumer_id", record=record),
            consumer_repository=_text(
                raw,
                "consumer_repository",
                record=record,
            ),
            dataset_id=_text(raw, "dataset_id", record=record),
            registry_commit=commit,
            path=_text(raw, "path", record=record),
            sha256=sha256,
            migration_status=migration_status,
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)


@dataclass(frozen=True)
class LegacyRecord:
    """Typed projection of legacy quarantine metadata schema v0."""

    SCHEMA_VERSION: ClassVar[int] = 0

    id: str
    title: str
    publisher: str
    redistribution: str
    file_count: int
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "LegacyRecord":
        record = "legacy"
        raw = _mapping(raw, field=record)
        if raw.get("schema_version") != 0:
            raise RegistryModelError("legacy.schema_version must be 0")
        if raw.get("status") != "legacy-quarantine":
            raise RegistryModelError(
                "legacy.status must be 'legacy-quarantine'"
            )

        source = _mapping(raw.get("source"), field="legacy.source")
        license_data = _mapping(raw.get("license"), field="legacy.license")
        files = raw.get("files")
        if not isinstance(files, (list, tuple)) or not files:
            raise RegistryModelError("legacy.files must be a non-empty list")
        for index, item in enumerate(files):
            file_record = _mapping(item, field=f"legacy.files[{index}]")
            _text(
                file_record,
                "original_path",
                record=f"legacy.files[{index}]",
            )
            _text(file_record, "path", record=f"legacy.files[{index}]")
            size = file_record.get("size_bytes")
            if not isinstance(size, int) or size < 0:
                raise RegistryModelError(
                    f"legacy.files[{index}].size_bytes must be a non-negative integer"
                )
            blob = _text(
                file_record,
                "git_blob_sha",
                record=f"legacy.files[{index}]",
            )
            if len(blob) != 40:
                raise RegistryModelError(
                    f"legacy.files[{index}].git_blob_sha must contain 40 characters"
                )

        return cls(
            id=_text(raw, "id", record=record),
            title=_text(raw, "title", record=record),
            publisher=_text(
                source,
                "publisher",
                record="legacy.source",
            ),
            redistribution=_text(
                license_data,
                "redistribution",
                record="legacy.license",
            ),
            file_count=len(files),
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)


@dataclass(frozen=True)
class ProvenanceDebtItem:
    """Typed projection of one generated provenance-debt queue item."""

    id: str
    layer: str
    title: str
    path: str
    redistribution: str
    review_status: str | None
    terminal: bool | None
    blocker_category: str | None
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProvenanceDebtItem":
        record = "provenance_debt"
        raw = _mapping(raw, field=record)
        layer = _enum(raw, "layer", {"external", "legacy"}, record=record)

        review_status = raw.get("review_status")
        if review_status is not None and review_status not in {
            "actionable",
            "terminal",
        }:
            raise RegistryModelError(
                "provenance_debt.review_status must be actionable, terminal, or null"
            )

        terminal = raw.get("terminal")
        if terminal is not None and not isinstance(terminal, bool):
            raise RegistryModelError(
                "provenance_debt.terminal must be boolean or null"
            )

        blocker = raw.get("blocker_category")
        if blocker is not None and not isinstance(blocker, str):
            raise RegistryModelError(
                "provenance_debt.blocker_category must be text or null"
            )

        return cls(
            id=_text(raw, "id", record=record),
            layer=layer,
            title=_text(raw, "title", record=record),
            path=_text(raw, "path", record=record),
            redistribution=_text(raw, "redistribution", record=record),
            review_status=review_status,
            terminal=terminal,
            blocker_category=blocker,
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)


@dataclass(frozen=True)
class LifecycleDataset:
    """Typed projection of one generated lifecycle dataset record."""

    id: str
    title: str
    status: str
    replacement_chain: tuple[str, ...]
    direct_predecessors: tuple[str, ...]
    direct_replacement: str | None
    preferred_dataset_id: str | None
    active_consumer_count: int
    migration_needed_consumer_count: int
    _raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "LifecycleDataset":
        record = "lifecycle"
        raw = _mapping(raw, field=record)
        status = _enum(
            raw,
            "status",
            {"active", "deprecated", "superseded"},
            record=record,
        )
        active_count = raw.get("active_consumer_count")
        migration_count = raw.get("migration_needed_consumer_count")
        if not isinstance(active_count, int) or active_count < 0:
            raise RegistryModelError(
                "lifecycle.active_consumer_count must be a non-negative integer"
            )
        if not isinstance(migration_count, int) or migration_count < 0:
            raise RegistryModelError(
                "lifecycle.migration_needed_consumer_count must be a non-negative integer"
            )

        return cls(
            id=_text(raw, "id", record=record),
            title=_text(raw, "title", record=record),
            status=status,
            replacement_chain=_string_tuple(
                raw.get("replacement_chain"),
                field="lifecycle.replacement_chain",
            ),
            direct_predecessors=_string_tuple(
                raw.get("direct_predecessors"),
                field="lifecycle.direct_predecessors",
            ),
            direct_replacement=_optional_text(
                raw,
                "direct_replacement",
                record=record,
            ),
            preferred_dataset_id=_optional_text(
                raw,
                "preferred_dataset_id",
                record=record,
            ),
            active_consumer_count=active_count,
            migration_needed_consumer_count=migration_count,
            _raw=_freeze(raw),
        )

    def to_mapping(self) -> dict[str, Any]:
        return _thaw(self._raw)
