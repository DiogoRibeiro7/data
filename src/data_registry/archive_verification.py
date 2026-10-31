"""Offline integrity and policy checks for downloaded archive-ready bundles."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from .release_verification import ReleaseVerificationError, verify_release_bundle

REPOSITORY = "DiogoRibeiro7/data"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARCHIVE_PROFILES = frozenset({"release-metadata", "eligible-canonical-bytes"})
ALLOWED_ROOTS = frozenset(
    {"archive", "release", "preservation", "reports", "distribution", "datasets", "CITATION.cff"}
)
REQUIRED_FILES = frozenset(
    {
        "archive/archive-metadata.json",
        "release/snapshot-manifest.json",
        "release/snapshot-summary.md",
        "release/snapshot-provenance.json",
        "CITATION.cff",
        "preservation/policy-v1.json",
        "reports/preservation-eligibility.json",
    }
)


class ArchiveVerificationError(RuntimeError):
    """An archive failed offline integrity or preservation-policy checks."""


@dataclass(frozen=True)
class ArchiveVerificationResult:
    """Verified archive identity and file-accounting summary."""

    tag: str
    commit: str
    profile: str
    file_count: int
    total_bytes: int
    manifest_sha256: str


def _sha256_file(path: Path) -> str:
    """Hash file bytes without loading large canonical datasets into memory."""

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ArchiveVerificationError(f"cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    """Load a JSON object with a verification-specific error on failure."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArchiveVerificationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArchiveVerificationError(f"{path}: JSON root must be an object")
    return value


def _relative_file_path(value: Any) -> PurePosixPath:
    """Require an exact, safe POSIX file path from the archive manifest."""

    if not isinstance(value, str) or not value or "\\" in value:
        raise ArchiveVerificationError(f"invalid archive file path: {value!r}")
    path = PurePosixPath(value)
    if (
        not path.parts
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != value
        or path.parts[0] not in ALLOWED_ROOTS
        or (path.parts[0] == "CITATION.cff" and len(path.parts) != 1)
        or (path.parts[0] == "datasets" and len(path.parts) < 3)
    ):
        raise ArchiveVerificationError(f"invalid archive file path: {value!r}")
    return path


def _verify_canonical_datasets(
    bundle: Path,
    manifest_digests: dict[str, str],
    profile: str,
) -> None:
    """Recheck preserved dataset inclusion, licences, and declared checksums."""

    paths = set(manifest_digests)
    archived_ids = {
        PurePosixPath(path).parts[1]
        for path in paths
        if path.startswith("datasets/") and len(PurePosixPath(path).parts) >= 3
    }
    if profile == "release-metadata":
        if any(path.startswith("datasets/") for path in paths):
            raise ArchiveVerificationError(
                "metadata-only archive contains canonical dataset bytes"
            )
        return

    eligibility = _json(bundle / "reports" / "preservation-eligibility.json")
    canonical = eligibility.get("canonical")
    if not isinstance(canonical, list):
        raise ArchiveVerificationError("preservation eligibility canonical list is missing")
    eligible_ids: set[str] = set()
    seen_ids: set[str] = set()
    for item in canonical:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ArchiveVerificationError("invalid canonical eligibility entry")
        dataset_id = item["id"]
        if dataset_id in seen_ids:
            raise ArchiveVerificationError("duplicate canonical eligibility entry")
        seen_ids.add(dataset_id)
        if item.get("byte_archive_eligibility") == "eligible":
            if item.get("redistribution") != "allowed":
                raise ArchiveVerificationError(
                    f"{dataset_id}: eligible dataset lacks redistribution rights"
                )
            if item.get("metadata_path") != f"datasets/{dataset_id}/metadata.yaml":
                raise ArchiveVerificationError(
                    f"{dataset_id}: invalid canonical eligibility metadata path"
                )
            eligible_ids.add(dataset_id)
    if archived_ids != eligible_ids:
        raise ArchiveVerificationError(
            "archived canonical datasets differ from preservation eligibility"
        )

    for dataset_id in sorted(archived_ids):
        metadata_name = f"datasets/{dataset_id}/metadata.yaml"
        if metadata_name not in paths:
            raise ArchiveVerificationError(f"missing canonical metadata: {metadata_name}")
        metadata_path = bundle / metadata_name
        try:
            metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ArchiveVerificationError(
                f"cannot read canonical metadata {metadata_name}: {exc}"
            ) from exc
        if not isinstance(metadata, dict) or metadata.get("id") != dataset_id:
            raise ArchiveVerificationError(f"{metadata_name}: dataset id mismatch")
        license_data = metadata.get("license")
        if (
            not isinstance(license_data, dict)
            or license_data.get("redistribution") != "allowed"
        ):
            raise ArchiveVerificationError(
                f"{metadata_name}: canonical dataset redistribution is not allowed"
            )
        file_entries = metadata.get("files")
        if not isinstance(file_entries, list) or not file_entries:
            raise ArchiveVerificationError(f"{metadata_name}: missing declared files")

        declared: dict[str, str] = {}
        for item in file_entries:
            if not isinstance(item, dict):
                raise ArchiveVerificationError(f"{metadata_name}: invalid file declaration")
            relative = item.get("path")
            checksum = item.get("sha256")
            if not isinstance(relative, str) or not isinstance(checksum, str):
                raise ArchiveVerificationError(f"{metadata_name}: invalid file declaration")
            candidate = _relative_file_path(f"datasets/{dataset_id}/{relative}")
            if len(candidate.parts) < 4 or candidate.parts[2] not in {"raw", "derived"}:
                raise ArchiveVerificationError(f"{metadata_name}: invalid dataset file path")
            full_path = candidate.as_posix()
            if full_path in declared or SHA256_RE.fullmatch(checksum) is None:
                raise ArchiveVerificationError(f"{metadata_name}: duplicate or invalid SHA-256")
            declared[full_path] = checksum

        archived_data = {
            path
            for path in paths
            if path.startswith(f"datasets/{dataset_id}/")
            and path not in {metadata_name, f"datasets/{dataset_id}/README.md"}
        }
        if archived_data != set(declared):
            raise ArchiveVerificationError(
                f"{metadata_name}: archived data files differ from declarations"
            )
        for path, checksum in declared.items():
            if manifest_digests[path] != checksum:
                raise ArchiveVerificationError(
                    f"{path}: archived SHA-256 differs from canonical metadata"
                )


def verify_archive_bundle(
    archive: Path | str,
    *,
    expected_tag: str | None = None,
    expected_commit: str | None = None,
    expected_profile: str | None = None,
) -> ArchiveVerificationResult:
    """Verify an extracted archive-ready directory completely offline.

    This establishes internal consistency, not publisher authenticity: a
    trusted artifact attestation is still needed to authenticate origin.
    """

    root = Path(archive).resolve()
    manifest_path = root / "archive-bundle-manifest.json"
    manifest = _json(manifest_path)
    if manifest.get("schema_version") != 1 or manifest.get("repository") != REPOSITORY:
        raise ArchiveVerificationError("invalid archive manifest version or repository")

    snapshot = manifest.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ArchiveVerificationError("archive snapshot identity is missing")
    tag, commit = snapshot.get("tag"), snapshot.get("commit")
    if not isinstance(tag, str) or not tag or not isinstance(commit, str):
        raise ArchiveVerificationError("archive snapshot identity is malformed")
    if COMMIT_RE.fullmatch(commit) is None:
        raise ArchiveVerificationError("archive commit must be a full lowercase SHA")
    if expected_tag is not None and tag != expected_tag:
        raise ArchiveVerificationError("archive tag does not match requested tag")
    if expected_commit is not None and commit != expected_commit:
        raise ArchiveVerificationError("archive commit does not match requested commit")

    profile = manifest.get("archive_profile")
    if profile not in ARCHIVE_PROFILES:
        raise ArchiveVerificationError("unsupported archive profile")
    if expected_profile is not None and profile != expected_profile:
        raise ArchiveVerificationError("archive profile does not match requested profile")

    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise ArchiveVerificationError("archive manifest has no file records")
    bundle = root / "archive-bundle"
    if not bundle.is_dir() or bundle.is_symlink():
        raise ArchiveVerificationError("archive-bundle directory is missing or unsafe")

    digests: dict[str, str] = {}
    total_bytes = 0
    for record in records:
        if not isinstance(record, dict):
            raise ArchiveVerificationError("archive file record must be an object")
        relative = _relative_file_path(record.get("path"))
        name = relative.as_posix()
        digest, size = record.get("sha256"), record.get("size")
        if name in digests:
            raise ArchiveVerificationError(f"duplicate archive file path: {name}")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise ArchiveVerificationError(f"{name}: invalid SHA-256 declaration")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ArchiveVerificationError(f"{name}: invalid byte size")

        source = bundle.joinpath(*relative.parts)
        if not source.is_file() or source.resolve() != bundle.joinpath(*relative.parts):
            raise ArchiveVerificationError(f"{name}: archive file missing or unsafe")
        if source.stat().st_size != size:
            raise ArchiveVerificationError(f"{name}: archive file size mismatch")
        if _sha256_file(source) != digest:
            raise ArchiveVerificationError(f"{name}: archive file SHA-256 mismatch")
        digests[name] = digest
        total_bytes += size

    actual: set[str] = set()
    for path in bundle.rglob("*"):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ArchiveVerificationError(f"unexpected filesystem entry: {path}")
        if path.is_file():
            actual.add(path.relative_to(bundle).as_posix())
    if actual != set(digests):
        raise ArchiveVerificationError(
            f"archive has undeclared or missing files: {sorted(actual ^ set(digests))}"
        )
    if not REQUIRED_FILES.issubset(digests):
        raise ArchiveVerificationError(
            f"archive is missing mandatory files: {sorted(REQUIRED_FILES - set(digests))}"
        )

    outer_metadata = root / "archive-metadata.json"
    if _sha256_file(outer_metadata) != digests["archive/archive-metadata.json"]:
        raise ArchiveVerificationError("standalone archive metadata does not match bundle")
    metadata = _json(bundle / "archive" / "archive-metadata.json")
    if (
        metadata.get("repository") != REPOSITORY
        or metadata.get("archive_profile") != profile
        or not isinstance(metadata.get("snapshot"), dict)
        or metadata["snapshot"].get("tag") != tag
        or metadata["snapshot"].get("commit") != commit
    ):
        raise ArchiveVerificationError("archive metadata identity/profile mismatch")

    try:
        verify_release_bundle(
            bundle / "release", expected_tag=tag, expected_commit=commit
        )
    except ReleaseVerificationError as exc:
        raise ArchiveVerificationError(f"embedded release failed verification: {exc}") from exc

    release_manifest = _json(bundle / "release" / "snapshot-manifest.json")
    distribution = release_manifest.get("static_distribution")
    version = distribution.get("distribution_version") if isinstance(distribution, dict) else None
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ArchiveVerificationError("embedded release has invalid distribution version")
    index_name = f"distribution/v{version}/index.json"
    if index_name not in digests:
        raise ArchiveVerificationError("snapshot distribution index is missing")
    index = _json(bundle / index_name)
    if index.get("repository") != REPOSITORY or index.get("distribution_version") != version:
        raise ArchiveVerificationError("distribution index identity mismatch")
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list):
        raise ArchiveVerificationError("distribution index artifacts are malformed")
    indexed_paths = {index_name}
    for item in artifacts:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ArchiveVerificationError("distribution index contains invalid artifact")
        filename = item["path"]
        if filename in {"", ".", ".."} or "/" in filename or "\\" in filename:
            raise ArchiveVerificationError("distribution index has unsafe artifact path")
        artifact_path = f"distribution/v{version}/{filename}"
        if artifact_path in indexed_paths:
            raise ArchiveVerificationError("distribution index has duplicate artifact")
        indexed_paths.add(artifact_path)
    actual_distribution = {name for name in digests if name.startswith("distribution/")}
    if actual_distribution != indexed_paths:
        raise ArchiveVerificationError("distribution artifacts differ from index")

    _verify_canonical_datasets(bundle, digests, profile)

    return ArchiveVerificationResult(
        tag=tag,
        commit=commit,
        profile=profile,
        file_count=len(digests),
        total_bytes=total_bytes,
        manifest_sha256=_sha256_file(manifest_path),
    )


__all__ = [
    "ArchiveVerificationError",
    "ArchiveVerificationResult",
    "verify_archive_bundle",
]
