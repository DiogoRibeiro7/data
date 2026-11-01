"""Offline verification of canonical handoff plans and received object bytes.

The source manifest is a transfer contract, not a signed origin attestation.
Verification therefore requires a commit supplied independently by the caller.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, SchemaError, ValidationError

from .fetch import DatasetReference

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_RESOURCE = "schemas/ingestion-handoff-v1.schema.json"


class HandoffVerificationError(RuntimeError):
    """A serialized handoff or received canonical file failed verification."""


@dataclass(frozen=True, slots=True)
class HandoffVerificationResult:
    """Summary of verified bytes associated with one immutable handoff."""

    dataset_id: str
    repository: str
    commit: str
    verified_objects: int
    total_bytes: int
    manifest_sha256: str


def _load_json(path: Path) -> dict[str, Any]:
    """Load a manifest JSON object with a verification-specific failure."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffVerificationError(f"cannot read handoff manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise HandoffVerificationError("handoff manifest must be a JSON object")
    return value


def _sha256_file(path: Path) -> str:
    """Hash an object incrementally so large datasets need not fit in RAM."""

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise HandoffVerificationError(f"cannot read {path}: {exc}") from exc
    return digest.hexdigest()


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
) -> HandoffVerificationResult:
    """Verify received objects under their manifest storage keys, offline.

    The caller must provide a trusted expected commit. Passing this check
    proves local byte integrity and internal reference consistency, not that
    the manifest or publisher is independently authentic.

    Unrelated objects under ``storage_root`` are intentionally ignored: a
    consumer may store multiple datasets and immutable vintages together.
    """

    if not isinstance(expected_commit, str) or COMMIT_RE.fullmatch(expected_commit) is None:
        raise HandoffVerificationError("expected commit must be a full lowercase SHA")

    manifest_path = Path(manifest)
    payload = _load_json(manifest_path)
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

    root = Path(storage_root).resolve()
    if not root.is_dir():
        raise HandoffVerificationError("received object storage root is missing")

    source_paths: set[str] = set()
    storage_keys: set[str] = set()
    total_bytes = 0
    objects = payload["objects"]
    for item in objects:
        source_path = item["source_path"]
        storage_key = item["storage_key"]
        sha256 = item["sha256"]
        role = item["role"]

        source = _safe_relative_path(source_path, label="source path")
        key = _safe_relative_path(storage_key, label="storage key")
        if source.parts[:2] != ("datasets", dataset_id) or source.parts[2] != role:
            raise HandoffVerificationError(f"{source_path}: invalid canonical source identity")

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

        actual_bytes = destination.stat().st_size
        declared_bytes = item["size_bytes"]
        if declared_bytes is not None and actual_bytes != declared_bytes:
            raise HandoffVerificationError(f"{storage_key}: received object byte size mismatch")
        if _sha256_file(destination) != sha256:
            raise HandoffVerificationError(f"{storage_key}: received object SHA-256 mismatch")
        total_bytes += actual_bytes

    return HandoffVerificationResult(
        dataset_id=dataset_id,
        repository=repository,
        commit=commit,
        verified_objects=len(objects),
        total_bytes=total_bytes,
        manifest_sha256=_sha256_file(manifest_path),
    )


__all__ = [
    "HandoffVerificationError",
    "HandoffVerificationResult",
    "verify_handoff_manifest",
]
