"""Offline verification of canonical handoff plans and received object bytes.

The source manifest is a transfer contract, not a signed origin attestation.
Verification therefore requires a commit supplied independently by the caller.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, SchemaError, ValidationError

from .api import RegistryClient
from .core import RegistryError
from .fetch import DatasetReference

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_RESOURCE = "schemas/ingestion-handoff-v1.schema.json"


class HandoffVerificationError(RuntimeError):
    """A serialized handoff or received canonical file failed verification."""


@dataclass(frozen=True, slots=True)
class HandoffVerifiedFile:
    """Portable evidence for one locally verified canonical file."""

    source_path: str
    storage_key: str
    sha256: str
    size_bytes: int

    def to_mapping(self) -> dict[str, str | int]:
        """Emit the checked bytes and identity without local absolute paths."""

        return {
            "source_path": self.source_path,
            "storage_key": self.storage_key,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True, slots=True)
class HandoffVerificationResult:
    """Summary of verified bytes associated with one immutable handoff."""

    dataset_id: str
    repository: str
    commit: str
    verified_objects: int
    total_bytes: int
    manifest_sha256: str
    trusted_checkout_verified: bool = False
    files: tuple[HandoffVerifiedFile, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        """Emit the stable v1 evidence contract for downstream audit logs.

        This report attests only to a local verification run, not to ingestion,
        remote storage promotion, publisher origin, or a signed execution event.
        """

        if (
            not self.files
            or len(self.files) != self.verified_objects
            or sum(item.size_bytes for item in self.files) != self.total_bytes
        ):
            raise HandoffVerificationError(
                "verification evidence must contain every verified file and byte"
            )
        return {
            "verification_version": 1,
            "ok": True,
            "dataset_id": self.dataset_id,
            "repository": self.repository,
            "commit": self.commit,
            "verified_objects": self.verified_objects,
            "total_bytes": self.total_bytes,
            "manifest_sha256": self.manifest_sha256,
            "trusted_checkout_verified": self.trusted_checkout_verified,
            "files": [item.to_mapping() for item in self.files],
        }


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    """Parse and fingerprint the same serialized manifest bytes exactly once."""

    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffVerificationError(f"cannot read handoff manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise HandoffVerificationError("handoff manifest must be a JSON object")
    return value, hashlib.sha256(raw).hexdigest()


def _verify_trusted_checkout(
    payload: dict[str, Any],
    *,
    checkout: Path,
    dataset_id: str,
    repository: str,
    commit: str,
) -> None:
    """Anchor all declared provenance and objects to a local committed Git tree.

    The existing handoff builder verifies that checkout HEAD and every source
    blob, including metadata.yaml, match ``commit`` without fetching objects.
    Regenerating its contract prevents a self-consistent but forged handoff
    from adding, omitting, or replacing source declarations.
    """

    try:
        canonical = RegistryClient(checkout).handoff(
            dataset_id,
            commit=commit,
            repository=repository,
            verify_local=True,
            verify_checkout=True,
        ).to_mapping()
    except (RegistryError, OSError, ValueError) as exc:
        raise HandoffVerificationError(
            f"trusted checkout could not verify pinned source: {exc}"
        ) from exc

    # The source's own verification flags are not provenance, and metadata-only
    # handoffs legitimately omit size values. All other fields must agree.
    provenance_fields = (
        "manifest_version",
        "dataset_id",
        "title",
        "lifecycle_status",
        "registry",
        "source",
        "license",
        "citation",
    )
    for field in provenance_fields:
        if payload[field] != canonical[field]:
            raise HandoffVerificationError(
                f"trusted checkout disagrees with handoff field: {field}"
            )

    declared = {item["source_path"]: item for item in payload["objects"]}
    committed = {item["source_path"]: item for item in canonical["objects"]}
    if len(declared) != len(payload["objects"]) or declared.keys() != committed.keys():
        raise HandoffVerificationError(
            "trusted checkout disagrees with handoff source file set"
        )
    for source_path, item in declared.items():
        expected = committed[source_path]
        for field in ("source_uri", "sha256", "role", "format", "storage_key"):
            if item[field] != expected[field]:
                raise HandoffVerificationError(
                    f"trusted checkout disagrees with {source_path}: {field}"
                )
        if item["size_bytes"] is not None and item["size_bytes"] != expected["size_bytes"]:
            raise HandoffVerificationError(
                f"trusted checkout disagrees with {source_path}: size_bytes"
            )


def _fingerprint_file(path: Path) -> tuple[str, int]:
    """Hash and count the same byte stream, rejecting concurrent file changes."""

    digest = hashlib.sha256()
    bytes_read = 0
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                bytes_read += len(chunk)
            after = os.fstat(handle.fileno())
        current = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise HandoffVerificationError(f"cannot read {path}: {exc}") from exc

    # A pre-hash stat is not evidence of how many bytes were actually hashed.
    # Detect a concurrent resize, rewrite, or replacement of the verified path.
    if (
        before.st_size != bytes_read
        or after.st_size != bytes_read
        or before.st_mtime_ns != after.st_mtime_ns
        or before.st_ctime_ns != after.st_ctime_ns
        or current.st_dev != after.st_dev
        or current.st_ino != after.st_ino
        or current.st_size != bytes_read
        or current.st_mtime_ns != after.st_mtime_ns
        or current.st_ctime_ns != after.st_ctime_ns
    ):
        raise HandoffVerificationError(
            f"{path}: received object changed during verification"
        )
    return digest.hexdigest(), bytes_read


def _safe_relative_path(value: str, *, label: str) -> PurePosixPath:
    """Reject noncanonical paths before joining to a local storage root."""

    if not value or "\\" in value:
        raise HandoffVerificationError(f"invalid {label}: {value!r}")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != value
        or len(path.parts) < 4
    ):
        raise HandoffVerificationError(f"invalid {label}: {value!r}")
    return path


def verify_handoff_manifest(
    manifest: Path | str,
    storage_root: Path | str,
    *,
    expected_commit: str,
    expected_repository: str | None = None,
    expected_dataset_id: str | None = None,
    trusted_checkout: Path | str | None = None,
) -> HandoffVerificationResult:
    """Verify received objects under their manifest storage keys, offline.

    The caller must provide a trusted expected commit. Passing this check
    proves local byte integrity and internal reference consistency. When
    ``trusted_checkout`` is given, the manifest is additionally matched
    against the pinned Git tree and all checked-out canonical source bytes.
    The caller still must establish the Git repository/commit origin.

    Unrelated objects under ``storage_root`` are intentionally ignored: a
    consumer may store multiple datasets and immutable vintages together.
    """

    if not isinstance(expected_commit, str) or COMMIT_RE.fullmatch(expected_commit) is None:
        raise HandoffVerificationError("expected commit must be a full lowercase SHA")

    manifest_path = Path(manifest)
    payload, manifest_sha256 = _load_json(manifest_path)
    try:
        schema = json.loads(
            resources.files("data_registry")
            .joinpath(SCHEMA_RESOURCE)
            .read_text(encoding="utf-8")
        )
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError, ValidationError) as exc:
        raise HandoffVerificationError(f"invalid handoff v1 schema: {exc}") from exc

    identity = payload["registry"]
    dataset_id = payload["dataset_id"]
    repository, commit = identity["repository"], identity["commit"]
    if commit != expected_commit:
        raise HandoffVerificationError("handoff commit does not match expected commit")
    if expected_repository is not None and repository != expected_repository:
        raise HandoffVerificationError("handoff repository does not match expected repository")
    if expected_dataset_id is not None and dataset_id != expected_dataset_id:
        raise HandoffVerificationError("handoff dataset does not match expected dataset")

    if trusted_checkout is not None:
        if expected_repository is None:
            raise HandoffVerificationError(
                "trusted checkout requires an independently expected repository"
            )
        if not isinstance(trusted_checkout, (str, Path)):
            raise HandoffVerificationError("trusted checkout must be a local directory path")
        _verify_trusted_checkout(
            payload,
            checkout=Path(trusted_checkout),
            dataset_id=dataset_id,
            repository=repository,
            commit=commit,
        )

    root = Path(storage_root).resolve()
    if not root.is_dir():
        raise HandoffVerificationError("received object storage root is missing")

    source_paths: set[str] = set()
    storage_keys: set[str] = set()
    total_bytes = 0
    verified_files: list[HandoffVerifiedFile] = []
    objects = payload["objects"]
    for item in objects:
        source_path = item["source_path"]
        storage_key = item["storage_key"]
        sha256 = item["sha256"]
        role = item["role"]

        source = _safe_relative_path(source_path, label="source path")
        key = _safe_relative_path(storage_key, label="storage key")
        if source.parts[:2] != ("datasets", dataset_id) or source.parts[2] != role:
            raise HandoffVerificationError(
                f"{source_path}: invalid canonical source identity"
            )

        expected_key = f"canonical/{dataset_id}/{sha256}/" + "/".join(source.parts[2:])
        if key.as_posix() != expected_key:
            raise HandoffVerificationError(f"{storage_key}: storage key differs from source identity")

        try:
            reference = DatasetReference(
                repository=repository,
                commit=commit,
                path=source_path,
                sha256=sha256,
            )
        except (ValueError, TypeError) as exc:
            raise HandoffVerificationError(f"invalid immutable source reference: {exc}") from exc
        if item["source_uri"] != reference.url():
            raise HandoffVerificationError(f"{source_path}: immutable source URI mismatch")

        if source_path in source_paths or storage_key in storage_keys:
            raise HandoffVerificationError("duplicate handoff source path or storage key")
        source_paths.add(source_path)
        storage_keys.add(storage_key)

        destination = root.joinpath(*key.parts)
        if not destination.is_file() or destination.resolve() != destination:
            raise HandoffVerificationError(f"{storage_key}: received object missing or unsafe")

        actual_sha256, actual_bytes = _fingerprint_file(destination)
        declared_bytes = item["size_bytes"]
        if declared_bytes is not None and actual_bytes != declared_bytes:
            raise HandoffVerificationError(f"{storage_key}: received object byte size mismatch")
        if actual_sha256 != sha256:
            raise HandoffVerificationError(f"{storage_key}: received object SHA-256 mismatch")
        total_bytes += actual_bytes
        verified_files.append(
            HandoffVerifiedFile(
                source_path=source_path,
                storage_key=storage_key,
                sha256=sha256,
                size_bytes=actual_bytes,
            )
        )

    return HandoffVerificationResult(
        dataset_id=dataset_id,
        repository=repository,
        commit=commit,
        verified_objects=len(objects),
        total_bytes=total_bytes,
        manifest_sha256=manifest_sha256,
        trusted_checkout_verified=trusted_checkout is not None,
        files=tuple(sorted(verified_files, key=lambda item: item.source_path)),
    )


__all__ = [
    "HandoffVerificationError",
    "HandoffVerificationResult",
    "HandoffVerifiedFile",
    "verify_handoff_manifest",
]
