#!/usr/bin/env python3
"""Generate or verify deterministic registry quality and coverage reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from *path*."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_metrics(root: Path) -> dict[str, Any]:
    """Return canonical-registry coverage metrics."""
    datasets_root = root / "datasets"
    dataset_dirs = sorted(
        path
        for path in datasets_root.iterdir()
        if path.is_dir() and (path / "metadata.yaml").is_file()
    )

    file_count = 0
    verified_checksum_files = 0
    complete_license_datasets = 0

    for dataset_dir in dataset_dirs:
        metadata = _load_yaml(dataset_dir / "metadata.yaml")
        license_data = metadata.get("license")
        if (
            isinstance(license_data, dict)
            and isinstance(license_data.get("name"), str)
            and bool(license_data["name"].strip())
            and isinstance(license_data.get("url"), str)
            and bool(license_data["url"].strip())
            and license_data.get("redistribution") in {"allowed", "restricted", "unknown"}
        ):
            complete_license_datasets += 1

        files = metadata.get("files")
        if not isinstance(files, list):
            continue
        for item in files:
            if not isinstance(item, dict):
                continue
            rel = item.get("path")
            expected = item.get("sha256")
            if not isinstance(rel, str) or not isinstance(expected, str):
                continue
            file_count += 1
            path = dataset_dir / rel
            if path.is_file() and _sha256(path) == expected:
                verified_checksum_files += 1

    return {
        "dataset_count": len(dataset_dirs),
        "file_count": file_count,
        "verified_checksum_files": verified_checksum_files,
        "complete_license_datasets": complete_license_datasets,
    }


def _external_metrics(root: Path) -> dict[str, Any]:
    """Return external-source coverage metrics."""
    external_root = root / "external"
    source_dirs = sorted(
        path
        for path in external_root.iterdir()
        if path.is_dir() and (path / "metadata.yaml").is_file()
    )

    resolved = 0
    unresolved = 0
    pinned = 0
    source_usage_consumers: set[str] = set()
    source_usage_references = 0

    for source_dir in source_dirs:
        metadata = _load_yaml(source_dir / "metadata.yaml")
        redistribution = metadata.get("redistribution")
        if redistribution is None:
            usage = metadata.get("usage")
            if isinstance(usage, dict):
                redistribution = usage.get("redistribution")

        if not isinstance(redistribution, str) or not redistribution.strip():
            unresolved += 1
        elif redistribution == "unresolved":
            unresolved += 1
        else:
            resolved += 1

        if isinstance(metadata.get("source_commit"), str):
            pinned += 1

        raw_consumers = metadata.get("consumers")
        if isinstance(raw_consumers, list):
            for consumer in raw_consumers:
                if isinstance(consumer, str) and consumer:
                    source_usage_consumers.add(consumer)
                    source_usage_references += 1

    return {
        "source_count": len(source_dirs),
        "redistribution": {
            "resolved": resolved,
            "unresolved": unresolved,
        },
        "pinned_immutable_identity_sources": pinned,
        "source_usage": {
            "consumer_count": len(source_usage_consumers),
            "consumer_references": source_usage_references,
            "consumers": sorted(source_usage_consumers),
        },
    }



def _consumer_metrics(root: Path) -> dict[str, Any]:
    """Return first-class canonical consumer-adoption metrics."""

    consumers_root = root / "consumers"
    dataset_ids: set[str] = set()
    canonical_contracts: dict[tuple[str, str], str] = {}
    for dataset_dir in sorted(
        path
        for path in (root / "datasets").iterdir()
        if path.is_dir() and (path / "metadata.yaml").is_file()
    ):
        dataset_id = dataset_dir.name
        dataset_ids.add(dataset_id)
        metadata = _load_yaml(dataset_dir / "metadata.yaml")
        files = metadata.get("files")
        if not isinstance(files, list):
            continue
        for item in files:
            if not isinstance(item, dict):
                continue
            relative_path = item.get("path")
            checksum = item.get("sha256")
            if isinstance(relative_path, str) and isinstance(checksum, str):
                canonical_contracts[
                    (dataset_id, f"datasets/{dataset_id}/{relative_path}")
                ] = checksum

    active_relationships = 0
    deprecated_relationships = 0
    pinned_contracts = 0
    active_consumers: set[str] = set()
    active_repositories: set[str] = set()
    consumed_datasets: set[str] = set()

    if consumers_root.is_dir():
        for consumer_dir in sorted(
            path for path in consumers_root.iterdir() if path.is_dir()
        ):
            for record_path in sorted(consumer_dir.glob("*.yaml")):
                metadata = _load_yaml(record_path)
                status = metadata.get("status")
                if status == "deprecated":
                    deprecated_relationships += 1
                    continue
                if status != "active":
                    continue

                active_relationships += 1

                consumer_id = metadata.get("consumer_id")
                if isinstance(consumer_id, str) and consumer_id:
                    active_consumers.add(consumer_id)

                consumer_repository = metadata.get("consumer_repository")
                if isinstance(consumer_repository, str) and consumer_repository:
                    active_repositories.add(consumer_repository)

                dataset_id = metadata.get("dataset_id")
                if isinstance(dataset_id, str) and dataset_id in dataset_ids:
                    consumed_datasets.add(dataset_id)

                commit = metadata.get("registry_commit")
                path = metadata.get("path")
                checksum = metadata.get("sha256")
                if (
                    isinstance(commit, str)
                    and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit)
                    and isinstance(dataset_id, str)
                    and isinstance(path, str)
                    and isinstance(checksum, str)
                    and canonical_contracts.get((dataset_id, path)) == checksum
                ):
                    pinned_contracts += 1

    without_consumers = sorted(dataset_ids - consumed_datasets)
    with_consumers = sorted(consumed_datasets)

    return {
        "active_consumer_repository_count": len(active_repositories),
        "active_relationship_count": active_relationships,
        "deprecated_relationship_count": deprecated_relationships,
        "pinned_contract_count": pinned_contracts,
        "pinned_contract_coverage": (
            pinned_contracts / active_relationships if active_relationships else 0.0
        ),
        "canonical_datasets_with_consumers": len(with_consumers),
        "canonical_datasets_without_consumers": len(without_consumers),
        "canonical_dataset_adoption_coverage": (
            len(with_consumers) / len(dataset_ids) if dataset_ids else 0.0
        ),
        "active_consumers": sorted(active_consumers),
        "active_consumer_repositories": sorted(active_repositories),
        "datasets_with_consumers": with_consumers,
        "datasets_without_consumers": without_consumers,
    }

def _legacy_metrics(root: Path) -> dict[str, Any]:
    """Return legacy-quarantine coverage metrics."""
    legacy_root = root / "legacy"
    packages = sorted(
        path.name
        for path in legacy_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )
    return {
        "package_count": len(packages),
        "unresolved_package_count": len(packages),
        "packages": packages,
    }


def _catalog_status(root: Path) -> dict[str, bool]:
    """Return generated-catalog freshness based on repository source state."""
    scripts = root / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        import generate_consumer_catalog as consumer_catalog  # type: ignore
        import generate_external_catalog as external_catalog  # type: ignore
        import validate_repository as validator  # type: ignore
    finally:
        sys.path.pop(0)

    canonical_metadata: list[dict[str, Any]] = []
    for dataset_dir in sorted(
        path
        for path in (root / "datasets").iterdir()
        if path.is_dir() and (path / "metadata.yaml").is_file()
    ):
        canonical_metadata.append(_load_yaml(dataset_dir / "metadata.yaml"))

    canonical_expected = validator.expected_catalog(canonical_metadata)
    canonical_json = json.dumps(canonical_expected, indent=2, ensure_ascii=False) + "\n"
    canonical_md = validator.expected_markdown_catalog(canonical_expected)

    external_json, external_md = external_catalog.expected_outputs(root)
    consumer_json, consumer_md, consumer_graph = consumer_catalog.expected_outputs(root)

    def current(path: Path, expected: str) -> bool:
        return path.is_file() and path.read_text(encoding="utf-8") == expected

    return {
        "canonical_current": (
            current(root / "datasets" / "catalog.json", canonical_json)
            and current(root / "datasets" / "CATALOG.md", canonical_md)
        ),
        "external_current": (
            current(root / "external" / "catalog.json", external_json)
            and current(root / "external" / "CATALOG.md", external_md)
        ),
        "consumer_current": (
            current(root / "consumers" / "catalog.json", consumer_json)
            and current(root / "consumers" / "CATALOG.md", consumer_md)
            and current(
                root / "consumers" / "dependency-graph.json",
                consumer_graph,
            )
        ),
    }


def build_report(root: Path) -> dict[str, Any]:
    """Build the deterministic registry quality report."""
    return {
        "schema_version": 1,
        "canonical": _canonical_metrics(root),
        "external": _external_metrics(root),
        "consumers": _consumer_metrics(root),
        "legacy": _legacy_metrics(root),
        "catalogs": _catalog_status(root),
        "snapshots": {
            "available_from_repository_state": False,
            "count": None,
            "note": (
                "Published snapshot tags/releases are not counted because their presence "
                "depends on Git fetch depth and remote state rather than committed files."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a human-readable registry quality report."""
    canonical = report["canonical"]
    external = report["external"]
    consumers = report["consumers"]
    legacy = report["legacy"]
    catalogs = report["catalogs"]
    snapshots = report["snapshots"]

    lines = [
        "# Registry quality and coverage",
        "",
        "This report is generated deterministically from committed repository state.",
        "It makes no live network requests.",
        "",
        "## Canonical registry",
        "",
        f"- Canonical datasets: **{canonical['dataset_count']}**",
        f"- Canonical files: **{canonical['file_count']}**",
        f"- Files with verified SHA-256: **{canonical['verified_checksum_files']}**",
        (
            "- Canonical datasets with complete licence metadata: "
            f"**{canonical['complete_license_datasets']}**"
        ),
        "",
        "## External sources",
        "",
        f"- External source records: **{external['source_count']}**",
        (
            "- Redistribution resolved / unresolved: "
            f"**{external['redistribution']['resolved']} / "
            f"{external['redistribution']['unresolved']}**"
        ),
        (
            "- Sources pinned to an immutable Git commit: "
            f"**{external['pinned_immutable_identity_sources']}**"
        ),
        "",
        "External source usage annotations:",
        "",
        f"- Referenced consumer repositories: **{external['source_usage']['consumer_count']}**",
        f"- Source usage references: **{external['source_usage']['consumer_references']}**",
        "",
    ]
    if external["source_usage"]["consumers"]:
        lines.extend(
            f"- `{name}`" for name in external["source_usage"]["consumers"]
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Canonical consumer adoption",
            "",
            (
                "- Active consumer repositories: "
                f"**{consumers['active_consumer_repository_count']}**"
            ),
            (
                "- Active canonical relationships: "
                f"**{consumers['active_relationship_count']}**"
            ),
            (
                "- Deprecated relationships: "
                f"**{consumers['deprecated_relationship_count']}**"
            ),
            (
                "- Pinned contracts: "
                f"**{consumers['pinned_contract_count']} / "
                f"{consumers['active_relationship_count']}**"
            ),
            (
                "- Pinned contract coverage: "
                f"**{consumers['pinned_contract_coverage']:.0%}**"
            ),
            (
                "- Canonical datasets with >=1 active consumer: "
                f"**{consumers['canonical_datasets_with_consumers']}**"
            ),
            (
                "- Canonical datasets with zero active consumers: "
                f"**{consumers['canonical_datasets_without_consumers']}**"
            ),
            (
                "- Canonical dataset adoption coverage: "
                f"**{consumers['canonical_dataset_adoption_coverage']:.0%}**"
            ),
            "",
            "Active consumers:",
            "",
        ]
    )
    if consumers["active_consumers"]:
        lines.extend(f"- `{name}`" for name in consumers["active_consumers"])
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Legacy quarantine",
            "",
            f"- Remaining packages: **{legacy['package_count']}**",
            f"- Unresolved packages: **{legacy['unresolved_package_count']}**",
            "",
            "## Generated catalog freshness",
            "",
            f"- Canonical catalog current: **{str(catalogs['canonical_current']).lower()}**",
            f"- External catalog current: **{str(catalogs['external_current']).lower()}**",
            f"- Consumer catalog/graph current: **{str(catalogs['consumer_current']).lower()}**",
            "",
            "## Snapshot coverage",
            "",
            (
                "- Snapshot/release count available from committed repository state: "
                f"**{str(snapshots['available_from_repository_state']).lower()}**"
            ),
            f"- Note: {snapshots['note']}",
            "",
            "## Interpretation",
            "",
            (
                "An unresolved redistribution state is not treated as an invalid record. "
                "It means the registry intentionally lacks sufficient evidence to claim "
                "redistribution permission."
            ),
            (
                "Canonical consumer adoption is measured only from formal `consumers/` "
                "records. External-source consumer annotations remain separate source-usage "
                "hints and are not counted as canonical consumer contracts."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def expected_outputs(root: Path) -> tuple[str, str]:
    """Return deterministic JSON and Markdown report text."""
    report = build_report(root)
    return (
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        render_markdown(report),
    )


def run(root: Path, *, write: bool) -> list[str]:
    """Write reports or return freshness errors."""
    json_text, md_text = expected_outputs(root)
    reports = root / "reports"
    outputs = [
        (reports / "registry-quality.json", json_text),
        (reports / "registry-quality.md", md_text),
    ]

    if write:
        reports.mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: generated quality report is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path}: quality report is stale; run with --write")
    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate registry quality reports.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        errors = run(args.root.resolve(), write=args.write)
    except (OSError, ValueError, yaml.YAMLError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.write:
        print("Registry quality reports updated.")
    else:
        print("Registry quality reports are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
