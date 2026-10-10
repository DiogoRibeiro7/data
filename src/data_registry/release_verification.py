"""Offline verification for immutable registry release bundles."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PREDICATE = (
    "https://github.com/DiogoRibeiro7/data/attestations/snapshot-provenance/v1"
)


class ReleaseVerificationError(RuntimeError):
    """Release bundle verification failure."""


@dataclass(frozen=True)
class ReleaseVerificationResult:
    """Successful offline release verification result."""

    tag: str
    commit: str
    manifest_version: int
    manifest_sha256: str
    summary_sha256: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseVerificationError(f"{path}: cannot read JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ReleaseVerificationError(f"{path}: JSON root must be an object")
    return raw


def verify_release_bundle(
    bundle: Path | str,
    *,
    expected_tag: str | None = None,
    expected_commit: str | None = None,
) -> ReleaseVerificationResult:
    """Verify one downloaded snapshot release bundle without network access."""

    root = Path(bundle).resolve()
    manifest_path = root / "snapshot-manifest.json"
    summary_path = root / "snapshot-summary.md"
    provenance_path = root / "snapshot-provenance.json"

    for path in (manifest_path, summary_path, provenance_path):
        if not path.is_file():
            raise ReleaseVerificationError(f"missing release asset: {path.name}")

    manifest = _json(manifest_path)
    provenance = _json(provenance_path)

    if provenance.get("schema_version") != 1:
        raise ReleaseVerificationError("unsupported provenance schema version")
    if provenance.get("predicate_type") != EXPECTED_PREDICATE:
        raise ReleaseVerificationError("unexpected provenance predicate type")

    snapshot = provenance.get("snapshot")
    artifacts = provenance.get("artifacts")
    interfaces = provenance.get("interfaces")
    if not isinstance(snapshot, dict) or not isinstance(artifacts, dict):
        raise ReleaseVerificationError("provenance snapshot/artifacts are malformed")
    if not isinstance(interfaces, dict):
        raise ReleaseVerificationError("provenance interfaces are malformed")

    manifest_artifact = artifacts.get("manifest")
    summary_artifact = artifacts.get("summary")
    if not isinstance(manifest_artifact, dict) or not isinstance(summary_artifact, dict):
        raise ReleaseVerificationError("provenance artifact records are malformed")

    manifest_sha = _sha256(manifest_path)
    summary_sha = _sha256(summary_path)
    if manifest_artifact.get("path") != "snapshot-manifest.json":
        raise ReleaseVerificationError("unexpected manifest artifact path")
    if summary_artifact.get("path") != "snapshot-summary.md":
        raise ReleaseVerificationError("unexpected summary artifact path")
    if manifest_artifact.get("sha256") != manifest_sha:
        raise ReleaseVerificationError("snapshot-manifest.json digest mismatch")
    if summary_artifact.get("sha256") != summary_sha:
        raise ReleaseVerificationError("snapshot-summary.md digest mismatch")

    tag = snapshot.get("tag")
    commit = snapshot.get("commit")
    if not isinstance(tag, str) or not tag:
        raise ReleaseVerificationError("provenance snapshot tag is missing")
    if not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None:
        raise ReleaseVerificationError("provenance snapshot commit is invalid")

    manifest_tag = manifest.get("tag")
    manifest_commit = manifest.get("commit")
    if manifest_tag != tag:
        raise ReleaseVerificationError("manifest/provenance tag mismatch")
    if manifest_commit != commit:
        raise ReleaseVerificationError("manifest/provenance commit mismatch")

    if expected_tag is not None and tag != expected_tag:
        raise ReleaseVerificationError(
            f"release tag mismatch: expected {expected_tag}, got {tag}"
        )
    if expected_commit is not None:
        if COMMIT_RE.fullmatch(expected_commit) is None:
            raise ReleaseVerificationError("expected commit must be a full lowercase SHA")
        if commit != expected_commit:
            raise ReleaseVerificationError(
                f"release commit mismatch: expected {expected_commit}, got {commit}"
            )

    manifest_version = manifest.get("manifest_version")
    if not isinstance(manifest_version, int):
        raise ReleaseVerificationError("manifest version is missing")
    if interfaces.get("snapshot_manifest_version") != manifest_version:
        raise ReleaseVerificationError("provenance/manifest version mismatch")

    if manifest.get("repository") != provenance.get("repository"):
        raise ReleaseVerificationError("manifest/provenance repository mismatch")

    static_distribution = manifest.get("static_distribution")
    if not isinstance(static_distribution, dict):
        raise ReleaseVerificationError("manifest static distribution is missing")
    if (
        static_distribution.get("distribution_version")
        != interfaces.get("static_distribution_version")
    ):
        raise ReleaseVerificationError(
            "provenance/static-distribution version mismatch"
        )

    assertions = provenance.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        raise ReleaseVerificationError("provenance assertions are missing")
    if any(
        not isinstance(item, dict) or item.get("result") != "pass"
        for item in assertions
    ):
        raise ReleaseVerificationError("provenance contains a non-passing assertion")

    return ReleaseVerificationResult(
        tag=tag,
        commit=commit,
        manifest_version=manifest_version,
        manifest_sha256=manifest_sha,
        summary_sha256=summary_sha,
    )


__all__ = [
    "ReleaseVerificationError",
    "ReleaseVerificationResult",
    "verify_release_bundle",
]
