"""Provider-neutral handoff manifests for canonical dataset ingestion.

The registry remains an immutable source of provenance and approved bytes. This
module produces an offline, deterministic transfer *plan*; execution, storage
credentials, and mutable analytical state belong to downstream consumers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final

from .core import RegistryError
from .fetch import DEFAULT_REPOSITORY, DatasetReference, sha256_file
from .models import CanonicalDataset

DATASET_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class HandoffObject:
    """One immutable source object and its provider-neutral destination key."""

    reference: DatasetReference
    role: str
    format: str
    storage_key: str
    size_bytes: int | None = None

    def to_mapping(self) -> dict[str, Any]:
        """Serialize this transfer entry without losing immutable identity."""

        return {
            "source_path": self.reference.path,
            "source_uri": self.reference.url(),
            "sha256": self.reference.sha256,
            "role": self.role,
            "format": self.format,
            "storage_key": self.storage_key,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True, slots=True)
class HandoffManifest:
    """Deterministic ingestion plan; no network or cloud provider is involved."""

    dataset_id: str
    title: str
    lifecycle_status: str
    repository: str
    commit: str
    source_publisher: str
    source_url: str
    source_snapshot: str
    retrieved_at: str
    license_name: str
    license_url: str
    citation_text: str
    objects: tuple[HandoffObject, ...]
    local_bytes_verified: bool

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-compatible versioned manifest for downstream ETL."""

        return {
            "manifest_version": 1,
            "dataset_id": self.dataset_id,
            "title": self.title,
            "lifecycle_status": self.lifecycle_status,
            "registry": {"repository": self.repository, "commit": self.commit},
            "source": {
                "publisher": self.source_publisher,
                "url": self.source_url,
                "snapshot": self.source_snapshot,
                "retrieved_at": self.retrieved_at,
            },
            "license": {
                "name": self.license_name,
                "url": self.license_url,
                "redistribution": "allowed",
            },
            "citation": self.citation_text,
            "local_bytes_verified": self.local_bytes_verified,
            "objects": [item.to_mapping() for item in self.objects],
        }


def _required_text(mapping: dict[str, Any], key: str, *, section: str) -> str:
    """Validate that the source metadata has the required textual identity."""

    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{section}.{key} must be non-empty text")
    return value


def build_handoff_manifest(
    dataset: CanonicalDataset,
    *,
    root: Path,
    commit: str,
    repository: str = DEFAULT_REPOSITORY,
    verify_local: bool = False,
) -> HandoffManifest:
    """Plan canonical ingestion using only approved, SHA-pinned registry files.

    If ``verify_local`` is enabled, source files are read and checked against
    their declared SHA-256 values. Otherwise this is a metadata-only plan: the
    downstream ingestion worker MUST verify downloaded bytes before publishing.
    This method never downloads, uploads, or writes any data.
    """

    if not isinstance(dataset, CanonicalDataset):
        raise TypeError("dataset must be CanonicalDataset")
    if not isinstance(root, Path):
        raise TypeError("root must be pathlib.Path")
    if not isinstance(verify_local, bool):
        raise TypeError("verify_local must be bool")
    if not DATASET_ID_RE.fullmatch(dataset.id):
        raise RegistryError("dataset id must be a normalized lowercase slug")
    if dataset.redistribution != "allowed":
        raise RegistryError(
            "canonical ingestion requires explicit redistribution permission"
        )

    metadata = dataset.to_mapping()
    source = metadata.get("source")
    license_data = metadata.get("license")
    citation = metadata.get("citation")
    files = metadata.get("files")
    if (
        not isinstance(source, dict)
        or not isinstance(license_data, dict)
        or not isinstance(citation, dict)
    ):
        raise RegistryError(
            "canonical metadata must declare source, license, and citation"
        )
    if not isinstance(files, list) or not files:
        raise RegistryError("canonical metadata must declare source files")

    # Source identity is retained for attribution and data-vintage tracing.
    source_url = _required_text(source, "url", section="source")
    license_name = _required_text(license_data, "name", section="license")
    license_url = _required_text(license_data, "url", section="license")
    citation_text = _required_text(citation, "text", section="citation")
    retrieved_at = source.get("retrieved_at")
    if isinstance(retrieved_at, (date, datetime)):
        retrieval_date = retrieved_at.isoformat()
    elif isinstance(retrieved_at, str) and retrieved_at.strip():
        retrieval_date = retrieved_at
    else:
        raise RegistryError("source.retrieved_at must be a date or non-empty string")

    resolved_root = root.resolve()
    canonical_root = (resolved_root / "datasets" / dataset.id).resolve()
    objects: list[HandoffObject] = []
    seen_paths: set[str] = set()
    for file_metadata in files:
        if not isinstance(file_metadata, dict):
            raise RegistryError("canonical file metadata must be an object")
        file_path = _required_text(file_metadata, "path", section="files")
        role = _required_text(file_metadata, "role", section="files")
        format_name = _required_text(file_metadata, "format", section="files")
        checksum = _required_text(file_metadata, "sha256", section="files")
        if role not in {"raw", "derived"} or not file_path.startswith(f"{role}/"):
            raise RegistryError("canonical file path must match its raw/derived role")

        repository_path = f"datasets/{dataset.id}/{file_path}"
        try:
            reference = DatasetReference(
                repository=repository,
                commit=commit,
                path=repository_path,
                sha256=checksum,
            )
        except (TypeError, ValueError) as exc:
            raise RegistryError(f"invalid immutable source reference: {exc}") from exc
        if reference.path in seen_paths:
            raise RegistryError(f"duplicate canonical source file: {reference.path}")
        seen_paths.add(reference.path)

        size_bytes: int | None = None
        if verify_local:
            local_path = (resolved_root / repository_path).resolve()
            if (
                not local_path.is_relative_to(canonical_root)
                or not local_path.is_file()
            ):
                raise RegistryError(
                    f"canonical source file missing or unsafe: {repository_path}"
                )
            if sha256_file(local_path) != reference.sha256:
                raise RegistryError(
                    f"canonical source checksum mismatch: {repository_path}"
                )
            size_bytes = local_path.stat().st_size

        # The key is an object-store-neutral, immutable relative path. It is
        # never treated as permission to upload without a consumer-side check.
        storage_key = f"canonical/{dataset.id}/{checksum}/{file_path}"
        objects.append(
            HandoffObject(
                reference=reference,
                role=role,
                format=format_name,
                storage_key=storage_key,
                size_bytes=size_bytes,
            )
        )

    objects.sort(key=lambda item: item.reference.path)
    return HandoffManifest(
        dataset_id=dataset.id,
        title=dataset.title,
        lifecycle_status=dataset.lifecycle_status,
        repository=repository,
        commit=commit,
        source_publisher=dataset.publisher,
        source_url=source_url,
        source_snapshot=dataset.source_snapshot,
        retrieved_at=retrieval_date,
        license_name=license_name,
        license_url=license_url,
        citation_text=citation_text,
        objects=tuple(objects),
        local_bytes_verified=verify_local,
    )
