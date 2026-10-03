#!/usr/bin/env python3
"""Validate the data repository and keep generated catalogs in sync."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

MAX_DIRECT_GIT_BYTES = 100 * 1024 * 1024
REVIEW_LARGE_FILE_BYTES = 25 * 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"

FORBIDDEN_NAMES = {".DS_Store"}
FORBIDDEN_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".tmp", ".swp"}


@dataclass(frozen=True)
class Problem:
    """A validation problem discovered in the repository."""

    severity: str
    message: str


def sha256_file(path: Path) -> str:
    """Return the SHA-256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_identity(path: Path) -> tuple[str, int]:
    """Return the stored Git blob SHA-1 and size for a tracked file.

    In a real Git checkout, legacy integrity must be checked against the
    repository object rather than the materialized worktree bytes because
    checkout filters such as line-ending normalization may change the latter.
    Temporary unit-test repositories without Git metadata fall back to
    computing a blob identity from the file bytes directly.
    """

    try:
        root_result = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        root = Path(root_result.stdout.strip())
        relative = path.resolve().relative_to(root.resolve())
        index_result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-s", "--", relative.as_posix()],
            check=True,
            capture_output=True,
            text=True,
        )
        line = index_result.stdout.strip()
        if line:
            fields = line.split()
            if len(fields) >= 2:
                blob_sha = fields[1]
                size_result = subprocess.run(
                    ["git", "-C", str(root), "cat-file", "-s", blob_sha],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return blob_sha, int(size_result.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        pass

    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    blob_sha = hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()
    return blob_sha, len(payload)


def load_yaml(path: Path, problems: list[Problem]) -> dict[str, Any] | None:
    """Load a YAML mapping and report parsing/type problems."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        problems.append(Problem("error", f"{path}: cannot parse YAML: {exc}"))
        return None

    if not isinstance(raw, dict):
        problems.append(Problem("error", f"{path}: metadata root must be a mapping"))
        return None
    return raw

def json_compatible(value: Any) -> Any:
    """Convert YAML-native values into JSON-compatible values for schema validation."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_compatible(item) for item in value]
    return value


def load_json_schema(name: str, problems: list[Problem]) -> dict[str, Any] | None:
    """Load one repository JSON Schema."""

    path = SCHEMA_DIR / name
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        problems.append(Problem("error", f"{path}: cannot load JSON Schema: {exc}"))
        return None
    if not isinstance(raw, dict):
        problems.append(Problem("error", f"{path}: JSON Schema root must be an object"))
        return None
    return raw


def validate_schema(
    metadata: dict[str, Any],
    schema_name: str,
    metadata_path: Path,
    problems: list[Problem],
) -> None:
    """Validate metadata against a versioned JSON Schema."""

    schema = load_json_schema(schema_name, problems)
    if schema is None:
        return

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(
        validator.iter_errors(json_compatible(metadata)),
        key=lambda item: list(item.absolute_path),
    ):
        location = ".".join(str(part) for part in error.absolute_path)
        suffix = f" at {location}" if location else ""
        problems.append(
            Problem("error", f"{metadata_path}: schema violation{suffix}: {error.message}")
        )



def require_mapping(
    metadata: dict[str, Any],
    key: str,
    path: Path,
    problems: list[Problem],
) -> dict[str, Any] | None:
    """Return a required mapping field, recording an error when invalid."""

    value = metadata.get(key)
    if not isinstance(value, dict):
        problems.append(Problem("error", f"{path}: '{key}' must be a mapping"))
        return None
    return value


def require_text(
    mapping: dict[str, Any],
    key: str,
    context: str,
    problems: list[Problem],
) -> str | None:
    """Validate a required non-empty text value."""

    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        problems.append(Problem("error", f"{context}: '{key}' must be non-empty text"))
        return None
    return value.strip()


def is_within(path: Path, parent: Path) -> bool:
    """Return whether path resolves inside parent."""

    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def repository_files(root: Path) -> list[Path]:
    """Return files that belong to the repository.

    In a Git checkout, validation is scoped to tracked files so runtime
    artifacts created by tests, such as Python bytecode caches, do not make
    a clean commit fail validation. Outside a Git checkout, all files are
    inspected; this keeps temporary unit-test repositories fully checked.
    """

    git_marker = root / ".git"
    if git_marker.exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z"],
                check=True,
                capture_output=True,
                text=False,
            )
        except (OSError, subprocess.CalledProcessError):
            pass
        else:
            return [
                root / item.decode("utf-8")
                for item in result.stdout.split(b"\\0")
                if item
            ]

    return [
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    ]


def validate_forbidden_files(root: Path, problems: list[Problem]) -> None:
    """Reject committed generated/cache files across the repository."""

    for path in repository_files(root):
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_DIRS for part in rel.parts):
            problems.append(Problem("error", f"{rel}: generated/cache file is forbidden"))
            continue
        if (
            path.name in FORBIDDEN_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or path.name.endswith("~")
        ):
            problems.append(Problem("error", f"{rel}: generated/cache file is forbidden"))


def validate_markdown_links(root: Path, datasets_root: Path, problems: list[Problem]) -> None:
    """Validate relative links in Markdown files under datasets/."""

    if not datasets_root.exists():
        return

    for markdown in datasets_root.rglob("*.md"):
        try:
            content = markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.append(Problem("error", f"{markdown}: cannot read Markdown: {exc}"))
            continue

        for target in MARKDOWN_LINK_RE.findall(content):
            target = target.strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            clean_target = target.split("#", 1)[0].split("?", 1)[0]
            if not clean_target:
                continue
            candidate = (markdown.parent / clean_target).resolve()
            if not is_within(candidate, root):
                problems.append(Problem("error", f"{markdown}: link escapes repository: {target}"))
            elif not candidate.exists():
                problems.append(Problem("error", f"{markdown}: broken relative link: {target}"))


def validate_legacy(root: Path, problems: list[Problem]) -> list[Path]:
    """Validate quarantine structure and Git-blob integrity for legacy data."""

    legacy_root = root / "legacy"
    data_files: list[Path] = []
    if not legacy_root.exists():
        return data_files

    for group in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        metadata_path = group / "metadata.yaml"
        readme_path = group / "README.md"
        raw_root = group / "raw"

        if not metadata_path.is_file():
            problems.append(Problem("error", f"{group}: missing metadata.yaml"))
            continue
        if not readme_path.is_file():
            problems.append(Problem("error", f"{group}: missing README.md"))
        if not raw_root.is_dir():
            problems.append(Problem("error", f"{group}: missing raw/ directory"))
            continue

        metadata = load_yaml(metadata_path, problems)
        if metadata is None:
            continue

        validate_schema(metadata, "legacy-metadata-v0.schema.json", metadata_path, problems)

        if metadata.get("schema_version") != 0:
            problems.append(Problem("error", f"{metadata_path}: legacy schema_version must be 0"))
        if metadata.get("status") != "legacy-quarantine":
            problems.append(Problem("error", f"{metadata_path}: status must be legacy-quarantine"))
        if metadata.get("id") != group.name:
            problems.append(
                Problem("error", f"{metadata_path}: id must match directory '{group.name}'")
            )

        source = require_mapping(metadata, "source", metadata_path, problems)
        if source is not None and ("publisher" not in source or "url" not in source):
            problems.append(
                Problem("error", f"{metadata_path}: source must contain publisher and url")
            )

        license_data = require_mapping(metadata, "license", metadata_path, problems)
        if license_data is not None and (
            "name" not in license_data or "redistribution" not in license_data
        ):
            problems.append(
                Problem(
                    "error",
                    f"{metadata_path}: license must contain name and redistribution",
                )
            )

        declared_raw: set[Path] = set()
        file_entries = metadata.get("files")
        if not isinstance(file_entries, list) or not file_entries:
            problems.append(Problem("error", f"{metadata_path}: files must be a non-empty list"))
            continue

        for index, entry in enumerate(file_entries):
            context = f"{metadata_path}: files[{index}]"
            if not isinstance(entry, dict):
                problems.append(Problem("error", f"{context} must be a mapping"))
                continue
            rel_value = entry.get("path")
            if not isinstance(rel_value, str) or not rel_value:
                problems.append(Problem("error", f"{context}: path must be non-empty text"))
                continue
            candidate = (group / rel_value).resolve()
            if not is_within(candidate, group):
                problems.append(Problem("error", f"{context}: path escapes legacy group"))
                continue
            rel_candidate = candidate.relative_to(group.resolve())
            if not str(rel_candidate).startswith("raw/"):
                problems.append(Problem("error", f"{context}: legacy data must live under raw/"))
            if not candidate.is_file():
                problems.append(Problem("error", f"{context}: referenced file does not exist"))
                continue

            data_files.append(candidate)
            declared_raw.add(candidate)

            worktree_size = candidate.stat().st_size
            if worktree_size > MAX_DIRECT_GIT_BYTES:
                problems.append(
                    Problem("error", f"{context}: legacy file exceeds 100 MiB direct-Git limit")
                )
            elif worktree_size >= REVIEW_LARGE_FILE_BYTES:
                problems.append(
                    Problem(
                        "warning",
                        f"{context}: legacy file is >=25 MiB and needs storage review before promotion",
                    )
                )

            blob_sha, blob_size = git_blob_identity(candidate)

            expected_size = entry.get("size_bytes")
            if isinstance(expected_size, int) and blob_size != expected_size:
                problems.append(
                    Problem("error", f"{context}: size_bytes does not match stored Git blob")
                )

            expected_git_sha = entry.get("git_blob_sha")
            if isinstance(expected_git_sha, str) and blob_sha != expected_git_sha:
                problems.append(
                    Problem("error", f"{context}: git_blob_sha does not match stored Git blob")
                )

        actual_raw = {path.resolve() for path in raw_root.rglob("*") if path.is_file()}
        for path in sorted(actual_raw - declared_raw):
            problems.append(
                Problem(
                    "error",
                    f"{path.relative_to(root)}: legacy raw file is missing from metadata.yaml",
                )
            )

    return data_files


def validate_canonical_dataset(
    root: Path,
    dataset_dir: Path,
    problems: list[Problem],
) -> tuple[dict[str, Any] | None, list[Path]]:
    """Validate one canonical dataset and return metadata plus data paths."""

    data_files: list[Path] = []
    slug = dataset_dir.name
    metadata_path = dataset_dir / "metadata.yaml"
    readme_path = dataset_dir / "README.md"

    if not SLUG_RE.fullmatch(slug):
        problems.append(Problem("error", f"{dataset_dir}: invalid dataset slug"))
    if not metadata_path.is_file():
        problems.append(Problem("error", f"{dataset_dir}: missing metadata.yaml"))
        return None, data_files
    if not readme_path.is_file():
        problems.append(Problem("error", f"{dataset_dir}: missing README.md"))

    metadata = load_yaml(metadata_path, problems)
    if metadata is None:
        return None, data_files

    validate_schema(metadata, "canonical-metadata-v1.schema.json", metadata_path, problems)

    if metadata.get("schema_version") != 1:
        problems.append(Problem("error", f"{metadata_path}: schema_version must be 1"))
    if metadata.get("id") != slug:
        problems.append(Problem("error", f"{metadata_path}: id must match directory '{slug}'"))

    for key in ("title", "description"):
        require_text(metadata, key, str(metadata_path), problems)

    domain = metadata.get("domain")
    if not isinstance(domain, list) or not domain or not all(
        isinstance(item, str) and item.strip() for item in domain
    ):
        problems.append(
            Problem("error", f"{metadata_path}: domain must be a non-empty list of strings")
        )

    source = require_mapping(metadata, "source", metadata_path, problems)
    if source is not None:
        for key in ("publisher", "url", "snapshot"):
            require_text(source, key, f"{metadata_path}: source", problems)
        retrieved_at = source.get("retrieved_at")
        if not (
            isinstance(retrieved_at, date)
            or (isinstance(retrieved_at, str) and retrieved_at.strip())
        ):
            problems.append(
                Problem(
                    "error",
                    f"{metadata_path}: source.retrieved_at must be an ISO date or non-empty text",
                )
            )

    license_data = require_mapping(metadata, "license", metadata_path, problems)
    if license_data is not None:
        for key in ("name", "url", "redistribution"):
            require_text(license_data, key, f"{metadata_path}: license", problems)
        redistribution = license_data.get("redistribution")
        if redistribution not in {"allowed", "restricted", "unknown"}:
            problems.append(
                Problem(
                    "error",
                    f"{metadata_path}: license.redistribution must be allowed, restricted, or unknown",
                )
            )
        if redistribution != "allowed":
            problems.append(
                Problem(
                    "error",
                    f"{metadata_path}: canonical stored data requires redistribution=allowed",
                )
            )

    citation = metadata.get("citation")
    if citation is not None:
        if not isinstance(citation, dict):
            problems.append(Problem("error", f"{metadata_path}: citation must be a mapping or null"))
        elif not any(
            isinstance(citation.get(key), str) and citation.get(key, "").strip()
            for key in ("text", "url")
        ):
            problems.append(
                Problem("error", f"{metadata_path}: citation must provide text or url")
            )

    lineage = metadata.get("lineage")
    if not isinstance(lineage, list):
        problems.append(Problem("error", f"{metadata_path}: lineage must be a list"))
        lineage = []

    file_entries = metadata.get("files")
    if not isinstance(file_entries, list) or not file_entries:
        problems.append(Problem("error", f"{metadata_path}: files must be a non-empty list"))
        return metadata, data_files

    declared: set[Path] = set()
    derived_paths: set[str] = set()

    for index, entry in enumerate(file_entries):
        context = f"{metadata_path}: files[{index}]"
        if not isinstance(entry, dict):
            problems.append(Problem("error", f"{context} must be a mapping"))
            continue

        rel_value = entry.get("path")
        role = entry.get("role")
        file_format = entry.get("format")
        expected_sha = entry.get("sha256")

        if not isinstance(rel_value, str) or not rel_value:
            problems.append(Problem("error", f"{context}: path must be non-empty text"))
            continue
        if role not in {"raw", "derived"}:
            problems.append(Problem("error", f"{context}: role must be raw or derived"))
        if not isinstance(file_format, str) or not file_format.strip():
            problems.append(Problem("error", f"{context}: format must be non-empty text"))
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            problems.append(Problem("error", f"{context}: sha256 must be 64 lowercase hex chars"))

        candidate = (dataset_dir / rel_value).resolve()
        if not is_within(candidate, dataset_dir):
            problems.append(Problem("error", f"{context}: path escapes dataset directory"))
            continue
        relative_candidate = candidate.relative_to(dataset_dir.resolve())
        expected_prefix = f"{role}/" if role in {"raw", "derived"} else None
        if expected_prefix is not None and not str(relative_candidate).startswith(expected_prefix):
            problems.append(
                Problem("error", f"{context}: role does not match raw/derived directory")
            )
        if not candidate.is_file():
            problems.append(Problem("error", f"{context}: referenced file does not exist"))
            continue

        declared.add(candidate)
        data_files.append(candidate)
        if role == "derived":
            derived_paths.add(rel_value)

        size = candidate.stat().st_size
        if size > MAX_DIRECT_GIT_BYTES:
            problems.append(
                Problem("error", f"{context}: file exceeds 100 MiB direct-Git limit")
            )
        elif size >= REVIEW_LARGE_FILE_BYTES and entry.get("large_file_reviewed") is not True:
            problems.append(
                Problem(
                    "error",
                    f"{context}: files >=25 MiB require large_file_reviewed: true",
                )
            )

        if isinstance(expected_sha, str) and SHA256_RE.fullmatch(expected_sha):
            if sha256_file(candidate) != expected_sha:
                problems.append(Problem("error", f"{context}: sha256 does not match file"))

    actual_data = {
        path.resolve()
        for folder in ("raw", "derived")
        if (dataset_dir / folder).exists()
        for path in (dataset_dir / folder).rglob("*")
        if path.is_file()
    }
    for path in sorted(actual_data - declared):
        problems.append(
            Problem(
                "error",
                f"{path.relative_to(root)}: canonical data file is missing from metadata.yaml",
            )
        )

    lineage_outputs = {
        item.get("output")
        for item in lineage
        if isinstance(item, dict) and isinstance(item.get("output"), str)
    }
    for derived in sorted(derived_paths - lineage_outputs):
        problems.append(
            Problem(
                "error",
                f"{metadata_path}: derived file '{derived}' is missing a lineage entry",
            )
        )

    return metadata, data_files


def validate_external(root: Path, problems: list[Problem]) -> None:
    """Validate external source-record metadata."""

    external_root = root / "external"
    if not external_root.is_dir():
        return

    seen_ids: dict[str, Path] = {}
    for source_dir in sorted(path for path in external_root.iterdir() if path.is_dir()):
        metadata_path = source_dir / "metadata.yaml"
        readme_path = source_dir / "README.md"

        if not metadata_path.is_file():
            problems.append(Problem("error", f"{source_dir}: missing metadata.yaml"))
            continue
        if not readme_path.is_file():
            problems.append(Problem("error", f"{source_dir}: missing README.md"))

        metadata = load_yaml(metadata_path, problems)
        if metadata is None:
            continue

        validate_schema(metadata, "external-metadata-v1.schema.json", metadata_path, problems)

        if metadata.get("schema_version") != 1:
            problems.append(Problem("error", f"{metadata_path}: external schema_version must be 1"))
        if metadata.get("status") != "external-reference":
            problems.append(Problem("error", f"{metadata_path}: status must be external-reference"))
        if metadata.get("id") != source_dir.name:
            problems.append(
                Problem("error", f"{metadata_path}: id must match directory '{source_dir.name}'")
            )

        source_id = metadata.get("id")
        if isinstance(source_id, str):
            if source_id in seen_ids:
                problems.append(
                    Problem(
                        "error",
                        f"{metadata_path}: duplicate external id also used by {seen_ids[source_id]}",
                    )
                )
            else:
                seen_ids[source_id] = metadata_path




def validate_consumer_template(root: Path, problems: list[Problem]) -> None:
    """Validate the committed consumer-record template structurally."""

    template_path = root / "templates" / "consumer-dataset.yaml"
    if not template_path.is_file():
        return

    metadata = load_yaml(template_path, problems)
    if metadata is None:
        return

    validate_schema(
        metadata,
        "consumer-metadata-v1.schema.json",
        template_path,
        problems,
    )


def validate_consumers(
    root: Path,
    canonical_metadata: dict[str, dict[str, Any]],
    problems: list[Problem],
) -> None:
    """Validate canonical consumer relationship records offline."""

    consumers_root = root / "consumers"
    if not consumers_root.is_dir():
        return

    seen_relationships: dict[tuple[str, str], Path] = {}

    for root_entry in sorted(consumers_root.iterdir()):
        if root_entry.is_file() and root_entry.suffix.lower() in {".yaml", ".yml"}:
            problems.append(
                Problem(
                    "error",
                    f"{root_entry}: consumer records must live under "
                    "consumers/<consumer-id>/<dataset-id>.yaml",
                )
            )

    for consumer_dir in sorted(path for path in consumers_root.iterdir() if path.is_dir()):
        consumer_id = consumer_dir.name
        if not SLUG_RE.fullmatch(consumer_id):
            problems.append(Problem("error", f"{consumer_dir}: invalid consumer slug"))
            continue

        for unexpected in sorted(
            path
            for path in consumer_dir.iterdir()
            if (
                path.is_file()
                and path.suffix.lower() in {".yaml", ".yml"}
                and path.suffix != ".yaml"
            )
        ):
            problems.append(
                Problem(
                    "error",
                    f"{unexpected}: consumer records must use the .yaml extension",
                )
            )

        for record_path in sorted(consumer_dir.glob("*.yaml")):
            metadata = load_yaml(record_path, problems)
            if metadata is None:
                continue

            validate_schema(
                metadata,
                "consumer-metadata-v1.schema.json",
                record_path,
                problems,
            )

            if metadata.get("schema_version") != 1:
                problems.append(
                    Problem("error", f"{record_path}: consumer schema_version must be 1")
                )

            if metadata.get("consumer_id") != consumer_id:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: consumer_id must match directory '{consumer_id}'",
                    )
                )

            dataset_id = metadata.get("dataset_id")
            if not isinstance(dataset_id, str) or not dataset_id:
                continue

            expected_filename = f"{dataset_id}.yaml"
            if record_path.name != expected_filename:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: filename must be '{expected_filename}'",
                    )
                )

            relationship = (consumer_id, dataset_id)
            previous = seen_relationships.get(relationship)
            if previous is not None:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: duplicate consumer/dataset relationship also "
                        f"declared by {previous}",
                    )
                )
            else:
                seen_relationships[relationship] = record_path

            expected_prefix = f"datasets/{dataset_id}/"
            declared_path = metadata.get("path")
            if not isinstance(declared_path, str) or not declared_path.startswith(expected_prefix):
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: path must belong to canonical dataset '{dataset_id}'",
                    )
                )
                continue

            if metadata.get("status") == "deprecated":
                continue

            dataset_metadata = canonical_metadata.get(dataset_id)
            if dataset_metadata is None:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: canonical dataset '{dataset_id}' does not exist",
                    )
                )
                continue

            relative_path = declared_path[len(expected_prefix):]
            files = dataset_metadata.get("files")
            canonical_file = None
            if isinstance(files, list):
                canonical_file = next(
                    (
                        item
                        for item in files
                        if isinstance(item, dict) and item.get("path") == relative_path
                    ),
                    None,
                )

            if canonical_file is None:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: path is not declared by canonical dataset metadata",
                    )
                )
                continue

            expected_sha = canonical_file.get("sha256")
            if metadata.get("sha256") != expected_sha:
                problems.append(
                    Problem(
                        "error",
                        f"{record_path}: sha256 does not match canonical dataset metadata",
                    )
                )


def build_catalog_entry(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build a stable catalog entry from canonical metadata."""

    source = metadata["source"]
    license_data = metadata["license"]
    return {
        "id": metadata["id"],
        "title": metadata["title"],
        "description": metadata["description"],
        "domain": metadata["domain"],
        "snapshot": str(source["snapshot"]),
        "source": {"publisher": source["publisher"], "url": source["url"]},
        "license": {
            "name": license_data["name"],
            "url": license_data["url"],
            "redistribution": license_data["redistribution"],
        },
        "path": f"datasets/{metadata['id']}",
    }


def expected_catalog(metadata_items: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return the canonical machine-readable catalog."""

    entries = sorted(
        (build_catalog_entry(metadata) for metadata in metadata_items),
        key=lambda item: item["id"],
    )
    return {"schema_version": 1, "datasets": entries}


def expected_markdown_catalog(catalog: dict[str, Any]) -> str:
    """Render the human-readable catalog."""

    datasets = catalog["datasets"]
    lines = [
        "# Canonical dataset catalog",
        "",
        "This file is generated from canonical `metadata.yaml` records.",
        "Do not edit it by hand.",
        "",
    ]
    if not datasets:
        lines.extend(["No canonical datasets are registered yet.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "| Dataset | Domain | Snapshot | Source | License / terms |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in datasets:
        domain = ", ".join(item["domain"])
        source = item["source"]
        license_data = item["license"]
        lines.append(
            f"| [{item['title']}]({item['id']}/README.md) | {domain} | "
            f"{item['snapshot']} | [{source['publisher']}]({source['url']}) | "
            f"[{license_data['name']}]({license_data['url']}) |"
        )
    lines.append("")
    return "\n".join(lines)


def validate_catalogs(
    root: Path,
    catalog: dict[str, Any],
    problems: list[Problem],
    *,
    write: bool,
) -> None:
    """Write or validate generated catalog files."""

    datasets_root = root / "datasets"
    json_path = datasets_root / "catalog.json"
    md_path = datasets_root / "CATALOG.md"

    json_text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    md_text = expected_markdown_catalog(catalog)

    if write:
        datasets_root.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        return

    for path, expected in ((json_path, json_text), (md_path, md_text)):
        if not path.is_file():
            problems.append(Problem("error", f"{path}: generated catalog file is missing"))
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            problems.append(
                Problem(
                    "error",
                    f"{path}: catalog is stale; run validator with --write-catalog",
                )
            )


def validate_duplicate_bytes(data_files: Iterable[Path], root: Path, problems: list[Problem]) -> None:
    """Reject exact duplicate data bytes anywhere in canonical/legacy storage."""

    by_checksum: dict[str, list[Path]] = {}
    for path in sorted(set(path.resolve() for path in data_files)):
        by_checksum.setdefault(sha256_file(path), []).append(path)

    for checksum, paths in sorted(by_checksum.items()):
        if len(paths) > 1:
            rendered = ", ".join(str(path.relative_to(root.resolve())) for path in paths)
            problems.append(Problem("error", f"duplicate SHA-256 {checksum}: {rendered}"))


def validate_repository(root: Path, *, write_catalog: bool = False) -> list[Problem]:
    """Validate repository structure, metadata, integrity, and catalogs."""

    root = root.resolve()
    problems: list[Problem] = []
    datasets_root = root / "datasets"

    validate_forbidden_files(root, problems)

    metadata_items: list[dict[str, Any]] = []
    data_files = validate_legacy(root, problems)
    validate_external(root, problems)
    validate_consumer_template(root, problems)

    if datasets_root.is_dir():
        for dataset_dir in sorted(path for path in datasets_root.iterdir() if path.is_dir()):
            metadata, canonical_files = validate_canonical_dataset(root, dataset_dir, problems)
            data_files.extend(canonical_files)
            if metadata is not None:
                metadata_items.append(metadata)

    canonical_metadata = {
        str(metadata["id"]): metadata
        for metadata in metadata_items
        if isinstance(metadata.get("id"), str)
    }
    validate_consumers(root, canonical_metadata, problems)

    if not any(problem.severity == "error" for problem in problems):
        validate_catalogs(
            root,
            expected_catalog(metadata_items),
            problems,
            write=write_catalog,
        )

    validate_duplicate_bytes(data_files, root, problems)
    validate_markdown_links(root, datasets_root, problems)
    return problems


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parser.add_argument(
        "--write-catalog",
        action="store_true",
        help="Regenerate datasets/catalog.json and datasets/CATALOG.md.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    problems = validate_repository(args.root, write_catalog=args.write_catalog)

    errors = [problem for problem in problems if problem.severity == "error"]
    warnings = [problem for problem in problems if problem.severity == "warning"]

    for problem in problems:
        print(f"{problem.severity.upper()}: {problem.message}")

    if args.write_catalog and not errors:
        print("Catalog files updated.")

    print(f"Validation complete: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
