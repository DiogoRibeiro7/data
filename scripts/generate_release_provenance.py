#!/usr/bin/env python3
"""Generate deterministic provenance metadata for immutable snapshot releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPOSITORY = "DiogoRibeiro7/data"
SCHEMA_VERSION = 1
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SNAPSHOT_TAG_RE = re.compile(
    r"^snapshot-\d{4}\.\d{2}\.\d{2}(?:\.[1-9]\d*)?$"
)
RELEASE_WORKFLOW = ".github/workflows/snapshot-release.yml"
PUBLISHER_WORKFLOW = (
    "DiogoRibeiro7/git-actions-collection/.github/workflows/"
    "snapshot-release.yml@6c68c76f3cec5b61552d24aa724fbd3398c33dbd"
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def validate_identity(tag: str, commit: str) -> None:
    """Validate immutable snapshot identity syntax."""

    if SNAPSHOT_TAG_RE.fullmatch(tag) is None:
        raise ValueError(
            "tag must match snapshot-YYYY.MM.DD or snapshot-YYYY.MM.DD.N"
        )
    if COMMIT_RE.fullmatch(commit) is None:
        raise ValueError("commit must be a full 40-character lowercase Git SHA")


def build_provenance(
    release_dir: Path,
    *,
    tag: str,
    commit: str,
) -> dict[str, Any]:
    """Build deterministic release provenance from prepared release material."""

    validate_identity(tag, commit)
    manifest_path = release_dir / "snapshot-manifest.json"
    summary_path = release_dir / "snapshot-summary.md"

    if not manifest_path.is_file():
        raise ValueError(f"missing release artifact: {manifest_path}")
    if not summary_path.is_file():
        raise ValueError(f"missing release artifact: {summary_path}")

    manifest = load_json(manifest_path)
    if manifest.get("repository") != REPOSITORY:
        raise ValueError("snapshot manifest repository does not match provenance")
    if manifest.get("tag") != tag:
        raise ValueError("snapshot manifest tag does not match provenance")
    if manifest.get("commit") != commit:
        raise ValueError("snapshot manifest commit does not match provenance")

    client = manifest.get("registry_client")
    distribution = manifest.get("static_distribution")
    if not isinstance(client, dict):
        raise ValueError("snapshot manifest has no registry_client object")
    if not isinstance(distribution, dict):
        raise ValueError("snapshot manifest has no static_distribution object")

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": REPOSITORY,
        "snapshot": {
            "tag": tag,
            "commit": commit,
            "manifest_version": manifest.get("manifest_version"),
        },
        "artifacts": [
            {
                "name": "snapshot-manifest.json",
                "sha256": sha256_file(manifest_path),
            },
            {
                "name": "snapshot-summary.md",
                "sha256": sha256_file(summary_path),
            },
        ],
        "workflow": {
            "repository_workflow": RELEASE_WORKFLOW,
            "publisher_workflow": PUBLISHER_WORKFLOW,
        },
        "versions": {
            "registry_client": {
                "name": client.get("name"),
                "version": client.get("version"),
                "public_api_version": client.get("public_api_version"),
            },
            "static_distribution_version": distribution.get(
                "distribution_version"
            ),
        },
        "release_assertions": [
            {
                "id": "unit-tests",
                "command": "python -m unittest discover -s tests -v",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "repository-validation",
                "command": "python scripts/validate_repository.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "external-catalog-freshness",
                "command": "python scripts/generate_external_catalog.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "consumer-catalog-freshness",
                "command": "python scripts/generate_consumer_catalog.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "registry-quality-freshness",
                "command": "python scripts/registry_quality.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "provenance-debt-freshness",
                "command": "python scripts/generate_provenance_debt.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "lifecycle-report-freshness",
                "command": "python scripts/generate_lifecycle_report.py",
                "result": "required-before-provenance-generation",
            },
            {
                "id": "static-distribution-freshness",
                "command": "python scripts/generate_static_distribution.py",
                "result": "required-before-provenance-generation",
            },
        ],
    }


def write_provenance(
    release_dir: Path,
    *,
    tag: str,
    commit: str,
) -> Path:
    """Write deterministic provenance JSON into the release directory."""

    provenance = build_provenance(release_dir, tag=tag, commit=commit)
    output = release_dir / "release-provenance.json"
    output.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        output = write_provenance(
            args.release_dir,
            tag=args.tag,
            commit=args.commit,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Release provenance: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
