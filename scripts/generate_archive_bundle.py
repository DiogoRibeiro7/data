#!/usr/bin/env python3
"""Generate deterministic archive metadata and an archive-ready snapshot bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml
import jsonschema

from data_registry import verify_release_bundle

REPOSITORY = "DiogoRibeiro7/data"
ARCHIVE_SCHEMA_VERSION = 1
SUPPORTED_PROFILES = {"release-metadata", "eligible-canonical-bytes"}


def sha256_file(path: Path) -> str:
    """Return a file SHA-256 digest."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""

    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return value


def copy_file(
    source: Path,
    destination: Path,
    *,
    bundle_root: Path,
) -> dict[str, Any]:
    """Copy one file and return its deterministic bundle-relative record."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return {
        "path": destination.relative_to(bundle_root).as_posix(),
        "sha256": sha256_file(destination),
        "size": destination.stat().st_size,
    }


def _creator_records(citation: dict[str, Any]) -> list[dict[str, Any]]:
    authors = citation.get("authors")
    if not isinstance(authors, list) or not authors:
        raise ValueError("CITATION.cff must define at least one author")

    records: list[dict[str, Any]] = []
    for author in authors:
        if not isinstance(author, dict):
            raise ValueError("CITATION.cff author entries must be mappings")
        given = author.get("given-names")
        family = author.get("family-names")
        if not isinstance(given, str) or not isinstance(family, str):
            raise ValueError("CITATION.cff authors require given-names and family-names")
        record: dict[str, Any] = {"name": f"{family}, {given}"}
        orcid = author.get("orcid")
        if isinstance(orcid, str) and orcid:
            record["orcid"] = orcid
        records.append(record)
    return records


def _identifier_records(
    root: Path,
    *,
    tag: str,
    commit: str,
) -> list[dict[str, Any]]:
    path = root / "archive" / "identifiers.json"
    if not path.is_file():
        return []

    payload = load_json(path)
    _validate_schema(root, "schemas/archive-identifiers-v1.schema.json", payload)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError(f"{path}: entries must be a list")

    seen: set[tuple[str, str, str, str]] = set()
    matches: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError(f"{path}: identifier entries must be objects")
        row_key = (
            str(item.get("tag")),
            str(item.get("commit")),
            str(item.get("provider")),
            str(item.get("identifier")),
        )
        if row_key in seen:
            raise ValueError(f"{path}: duplicate archive identifier entry {row_key!r}")
        seen.add(row_key)

        if item.get("tag") == tag and item.get("commit") == commit:
            identifier = item.get("identifier")
            provider = item.get("provider")
            if not isinstance(identifier, str) or not identifier:
                raise ValueError(f"{path}: identifier must be non-empty text")
            if not isinstance(provider, str) or not provider:
                raise ValueError(f"{path}: provider must be non-empty text")
            matches.append(
                {
                    "provider": provider,
                    "identifier": identifier,
                    "relation": item.get("relation", "isIdenticalTo"),
                }
            )
    matches.sort(key=lambda item: (item["provider"], item["identifier"]))
    return matches


def _canonical_archive_records(
    root: Path,
    eligibility: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return upstream licence/citation records for canonical datasets."""

    canonical = eligibility.get("canonical")
    if not isinstance(canonical, list):
        raise ValueError("preservation eligibility canonical list is missing")

    records: list[dict[str, Any]] = []
    for item in canonical:
        if not isinstance(item, dict):
            raise ValueError("preservation eligibility canonical entries must be objects")
        dataset_id = item.get("id")
        metadata_path = item.get("metadata_path")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ValueError("canonical eligibility id must be non-empty text")
        if not isinstance(metadata_path, str) or not metadata_path:
            raise ValueError("canonical eligibility metadata_path must be non-empty text")

        metadata = load_yaml(root / metadata_path)
        license_data = metadata.get("license")
        citation = metadata.get("citation")
        if not isinstance(license_data, dict):
            raise ValueError(f"{metadata_path}: license must be a mapping")
        if citation is not None and not isinstance(citation, dict):
            raise ValueError(f"{metadata_path}: citation must be a mapping or null")

        records.append(
            {
                "id": dataset_id,
                "title": metadata.get("title"),
                "byte_archive_eligibility": item.get("byte_archive_eligibility"),
                "license": {
                    "name": license_data.get("name"),
                    "url": license_data.get("url"),
                    "redistribution": license_data.get("redistribution"),
                },
                "citation": (
                    {
                        "text": citation.get("text"),
                        "url": citation.get("url"),
                    }
                    if isinstance(citation, dict)
                    else None
                ),
            }
        )
    records.sort(key=lambda item: item["id"])
    return records


def _validate_schema(root: Path, relative_schema: str, payload: dict[str, Any]) -> None:
    """Validate one generated archive payload against a committed JSON Schema."""

    schema = load_json(root / relative_schema)
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(payload)


def build_archive_metadata(
    root: Path,
    release_dir: Path,
    *,
    tag: str,
    commit: str,
    profile: str,
) -> dict[str, Any]:
    """Build deterministic archive metadata for one immutable snapshot."""

    if profile not in SUPPORTED_PROFILES:
        raise ValueError(f"unsupported archive profile: {profile}")

    verify_release_bundle(
        release_dir,
        expected_tag=tag,
        expected_commit=commit,
    )
    manifest = load_json(release_dir / "snapshot-manifest.json")
    provenance = load_json(release_dir / "snapshot-provenance.json")
    policy = load_json(root / "preservation" / "policy-v1.json")
    eligibility = load_json(root / "reports" / "preservation-eligibility.json")
    citation = load_yaml(root / "CITATION.cff")

    if manifest.get("repository") != REPOSITORY:
        raise ValueError("snapshot manifest repository mismatch")
    if manifest.get("tag") != tag or manifest.get("commit") != commit:
        raise ValueError("snapshot manifest identity mismatch")
    snapshot = provenance.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot provenance is missing snapshot identity")
    if snapshot.get("tag") != tag or snapshot.get("commit") != commit:
        raise ValueError("snapshot provenance identity mismatch")

    archive_profiles = policy.get("archive_profiles")
    if not isinstance(archive_profiles, dict) or profile not in archive_profiles:
        raise ValueError(f"preservation policy does not define profile {profile}")

    metadata = {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "repository": REPOSITORY,
        "snapshot": {
            "tag": tag,
            "commit": commit,
            "citation": f"{citation.get('title', 'Data Registry')}, {tag}, commit {commit}",
        },
        "title": f"{citation.get('title', 'Data Registry')} — {tag}",
        "description": citation.get("abstract"),
        "creators": _creator_records(citation),
        "keywords": sorted(
            item for item in citation.get("keywords", []) if isinstance(item, str)
        ),
        "archive_profile": profile,
        "licensing": {
            "registry_tooling": citation.get("license"),
            "upstream_dataset_terms_preserved": True,
            "archive_level_license_does_not_override_datasets": True,
        },
        "related_identifiers": [
            {
                "identifier": f"https://github.com/{REPOSITORY}/tree/{commit}",
                "relation": "isIdenticalTo",
            },
            {
                "identifier": f"https://github.com/{REPOSITORY}/releases/tag/{tag}",
                "relation": "isSupplementTo",
            },
        ],
        "assigned_archive_identifiers": _identifier_records(
            root, tag=tag, commit=commit
        ),
        "canonical_datasets": _canonical_archive_records(root, eligibility),
        "preservation": {
            "policy_version": policy.get("policy_version"),
            "eligibility_schema_version": eligibility.get("schema_version"),
            "canonical_byte_archive_eligible_count": (
                eligibility.get("summary", {}).get(
                    "canonical_byte_archive_eligible_count"
                )
                if isinstance(eligibility.get("summary"), dict)
                else None
            ),
        },
    }
    _validate_schema(root, "schemas/archive-metadata-v1.schema.json", metadata)
    return metadata


def build_bundle(
    root: Path,
    release_dir: Path,
    output_dir: Path,
    *,
    tag: str,
    commit: str,
    profile: str,
) -> tuple[Path, Path]:
    """Create deterministic archive metadata and copy only policy-eligible content."""

    metadata = build_archive_metadata(
        root,
        release_dir,
        tag=tag,
        commit=commit,
        profile=profile,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "archive-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    bundle_dir = output_dir / "archive-bundle"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    records: list[dict[str, Any]] = [
        copy_file(
            metadata_path,
            bundle_dir / "archive" / "archive-metadata.json",
            bundle_root=bundle_dir,
        )
    ]
    for name in (
        "snapshot-manifest.json",
        "snapshot-summary.md",
        "snapshot-provenance.json",
    ):
        records.append(
            copy_file(
                release_dir / name,
                bundle_dir / "release" / name,
                bundle_root=bundle_dir,
            )
        )

    for relative in (
        "CITATION.cff",
        "preservation/policy-v1.json",
        "reports/preservation-eligibility.json",
    ):
        records.append(
            copy_file(
                root / relative,
                bundle_dir / relative,
                bundle_root=bundle_dir,
            )
        )

    distribution = root / "distribution"
    for source in sorted(path for path in distribution.rglob("*") if path.is_file()):
        relative = source.relative_to(root)
        records.append(
            copy_file(source, bundle_dir / relative, bundle_root=bundle_dir)
        )

    if profile == "eligible-canonical-bytes":
        eligibility = load_json(root / "reports" / "preservation-eligibility.json")
        canonical = eligibility.get("canonical")
        if not isinstance(canonical, list):
            raise ValueError("preservation eligibility canonical list is missing")
        eligible_ids = {
            str(item["id"])
            for item in canonical
            if isinstance(item, dict)
            and item.get("byte_archive_eligibility") == "eligible"
        }
        for dataset_id in sorted(eligible_ids):
            dataset_root = root / "datasets" / dataset_id
            for source in sorted(
                path for path in dataset_root.rglob("*") if path.is_file()
            ):
                relative = source.relative_to(root)
                records.append(
                    copy_file(source, bundle_dir / relative, bundle_root=bundle_dir)
                )

    records.sort(key=lambda item: item["path"])
    manifest = {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "repository": REPOSITORY,
        "snapshot": {"tag": tag, "commit": commit},
        "archive_profile": profile,
        "files": records,
    }
    _validate_schema(
        root,
        "schemas/archive-bundle-manifest-v1.schema.json",
        manifest,
    )
    bundle_manifest_path = output_dir / "archive-bundle-manifest.json"
    bundle_manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata_path, bundle_manifest_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--profile",
        choices=sorted(SUPPORTED_PROFILES),
        default="release-metadata",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        metadata, bundle_manifest = build_bundle(
            args.root.resolve(),
            args.release_dir.resolve(),
            args.output_dir.resolve(),
            tag=args.tag,
            commit=args.commit,
            profile=args.profile,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Archive metadata: {metadata}")
    print(f"Archive bundle manifest: {bundle_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
