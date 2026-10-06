#!/usr/bin/env python3
"""Generate deterministic immutable snapshot release material."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

REPOSITORY = "DiogoRibeiro7/data"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SNAPSHOT_TAG_RE = re.compile(
    r"^snapshot-(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})"
    r"(?:\.(?P<sequence>[1-9]\d*))?$"
)
SCHEMA_FILES = {
    "canonical": "schemas/canonical-metadata-v2.schema.json",
    "consumer": "schemas/consumer-metadata-v1.schema.json",
    "external": "schemas/external-metadata-v1.schema.json",
    "legacy": "schemas/legacy-metadata-v0.schema.json",
}


def sha256_file(path: Path) -> str:
    """Return the SHA-256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_snapshot_tag(tag: str) -> None:
    """Validate snapshot tag syntax and calendar date."""

    match = SNAPSHOT_TAG_RE.fullmatch(tag)
    if match is None:
        raise ValueError(
            "tag must match snapshot-YYYY.MM.DD or snapshot-YYYY.MM.DD.N"
        )
    try:
        date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError as exc:
        raise ValueError(f"snapshot tag contains an invalid date: {tag}") from exc


def validate_commit(commit: str) -> None:
    """Require an exact lowercase 40-character Git commit SHA."""

    if COMMIT_RE.fullmatch(commit) is None:
        raise ValueError("commit must be a full 40-character lowercase Git SHA")


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return raw


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return raw


def _json_safe_value(value: Any) -> Any:
    """Normalize YAML scalar types that JSON cannot encode directly."""

    if isinstance(value, date):
        return value.isoformat()
    return value


def schema_record(root: Path, layer: str, relative_path: str) -> dict[str, Any]:
    """Return one metadata schema record."""

    path = root / relative_path
    schema = load_json(path)
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise ValueError(f"{path}: schema has no properties object")
    version_spec = properties.get("schema_version")
    if not isinstance(version_spec, dict) or not isinstance(version_spec.get("const"), int):
        raise ValueError(f"{path}: schema_version.const must be an integer")
    return {
        "layer": layer,
        "path": relative_path,
        "schema_version": version_spec["const"],
        "sha256": sha256_file(path),
    }


def canonical_dataset_records(root: Path) -> list[dict[str, Any]]:
    """Return deterministic canonical dataset/file checksum records."""

    datasets_root = root / "datasets"
    records: list[dict[str, Any]] = []
    if not datasets_root.is_dir():
        return records

    for dataset_dir in sorted(path for path in datasets_root.iterdir() if path.is_dir()):
        metadata_path = dataset_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_yaml(metadata_path)
        dataset_id = metadata.get("id")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ValueError(f"{metadata_path}: missing dataset id")
        files = metadata.get("files")
        if not isinstance(files, list):
            raise ValueError(f"{metadata_path}: files must be a list")

        file_records: list[dict[str, Any]] = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError(f"{metadata_path}: file entry must be a mapping")
            relative_file = item.get("path")
            expected_sha = item.get("sha256")
            if not isinstance(relative_file, str) or not relative_file:
                raise ValueError(f"{metadata_path}: file path must be non-empty text")
            if not isinstance(expected_sha, str):
                raise ValueError(f"{metadata_path}: file sha256 must be text")
            actual_path = dataset_dir / relative_file
            actual_sha = sha256_file(actual_path)
            if actual_sha != expected_sha:
                raise ValueError(
                    f"{actual_path}: SHA-256 mismatch: expected {expected_sha}, got {actual_sha}"
                )
            file_records.append({
                "path": relative_file,
                "role": item.get("role"),
                "format": item.get("format"),
                "sha256": actual_sha,
            })

        file_records.sort(key=lambda item: item["path"])
        source = metadata.get("source")
        license_data = metadata.get("license")
        if not isinstance(source, dict):
            raise ValueError(f"{metadata_path}: source must be a mapping")
        if not isinstance(license_data, dict):
            raise ValueError(f"{metadata_path}: license must be a mapping")

        records.append({
            "id": dataset_id,
            "path": f"datasets/{dataset_id}",
            "source": {
                "publisher": source.get("publisher"),
                "url": source.get("url"),
                "retrieved_at": _json_safe_value(source.get("retrieved_at")),
                "snapshot": source.get("snapshot"),
            },
            "license": {
                "name": license_data.get("name"),
                "url": license_data.get("url"),
                "redistribution": license_data.get("redistribution"),
            },
            "files": file_records,
        })

    records.sort(key=lambda item: item["id"])
    return records


def catalog_record(root: Path, relative_path: str) -> dict[str, Any]:
    """Return a catalog digest record."""

    path = root / relative_path
    catalog = load_json(path)
    schema_version = catalog.get("schema_version")
    if not isinstance(schema_version, int):
        raise ValueError(f"{path}: catalog schema_version must be an integer")
    return {
        "path": relative_path,
        "schema_version": schema_version,
        "sha256": sha256_file(path),
    }



def provenance_debt_record(root: Path) -> dict[str, Any]:
    """Return the provenance-debt report digest and summary metrics."""

    relative_path = "reports/provenance-debt.json"
    path = root / relative_path
    report = load_json(path)
    summary = report.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(f"{path}: provenance debt report has no summary object")

    required_counts = (
        "total_debt",
        "external_count",
        "legacy_count",
        "structured_count",
        "unstructured_count",
        "actionable_count",
        "terminal_count",
    )
    for key in required_counts:
        if not isinstance(summary.get(key), int):
            raise ValueError(f"{path}: summary.{key} must be an integer")

    categories = summary.get("by_blocker_category")
    if not isinstance(categories, dict):
        raise ValueError(f"{path}: summary.by_blocker_category must be an object")

    return {
        "path": relative_path,
        "schema_version": report.get("schema_version"),
        "sha256": sha256_file(path),
        "age_reference_date": report.get("age_reference_date"),
        "total_debt": summary["total_debt"],
        "external_count": summary["external_count"],
        "legacy_count": summary["legacy_count"],
        "structured_count": summary["structured_count"],
        "unstructured_count": summary["unstructured_count"],
        "actionable_count": summary["actionable_count"],
        "terminal_count": summary["terminal_count"],
        "by_blocker_category": dict(sorted(categories.items())),
    }


def canonical_expansion_record(root: Path) -> dict[str, Any]:
    """Return canonical-expansion policy and quality state."""

    quality_relative = "reports/registry-quality.json"
    policy_relative = "reports/canonical-adoption-policy.json"
    quality_path = root / quality_relative
    policy_path = root / policy_relative

    quality = load_json(quality_path)
    expansion = quality.get("canonical_expansion")
    consumers = quality.get("consumers")
    if not isinstance(expansion, dict):
        raise ValueError(f"{quality_path}: canonical_expansion must be an object")
    if not isinstance(consumers, dict):
        raise ValueError(f"{quality_path}: consumers must be an object")

    required_ints = (
        "baseline_dataset_count",
        "current_dataset_count",
    )
    for key in required_ints:
        if not isinstance(expansion.get(key), int):
            raise ValueError(f"{quality_path}: canonical_expansion.{key} must be an integer")

    required_lists = (
        "datasets_added_since_baseline",
        "datasets_removed_since_baseline",
        "added_datasets_with_consumers",
        "added_datasets_exempted",
        "uncovered_datasets",
    )
    for key in required_lists:
        value = expansion.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{quality_path}: canonical_expansion.{key} must be a string list")

    baseline_snapshot = expansion.get("baseline_snapshot")
    exemptions = expansion.get("exemptions")
    if not isinstance(baseline_snapshot, str) or not baseline_snapshot:
        raise ValueError(
            f"{quality_path}: canonical_expansion.baseline_snapshot must be non-empty text"
        )
    if not isinstance(exemptions, dict):
        raise ValueError(f"{quality_path}: canonical_expansion.exemptions must be an object")

    policy = load_json(policy_path)
    return {
        "quality_report_path": quality_relative,
        "quality_report_sha256": sha256_file(quality_path),
        "adoption_policy_path": policy_relative,
        "adoption_policy_sha256": sha256_file(policy_path),
        "adoption_policy_schema": policy.get("schema_version"),
        "baseline_snapshot": baseline_snapshot,
        "baseline_dataset_count": expansion["baseline_dataset_count"],
        "current_dataset_count": expansion["current_dataset_count"],
        "datasets_added_since_baseline": sorted(expansion["datasets_added_since_baseline"]),
        "datasets_removed_since_baseline": sorted(expansion["datasets_removed_since_baseline"]),
        "added_datasets_with_consumers": sorted(expansion["added_datasets_with_consumers"]),
        "added_datasets_exempted": sorted(expansion["added_datasets_exempted"]),
        "uncovered_datasets": sorted(expansion["uncovered_datasets"]),
        "exemptions": dict(sorted(exemptions.items())),
        "active_relationship_count": consumers.get("active_relationship_count"),
        "pinned_contract_count": consumers.get("pinned_contract_count"),
        "pinned_contract_coverage": consumers.get("pinned_contract_coverage"),
        "canonical_dataset_adoption_coverage": consumers.get(
            "canonical_dataset_adoption_coverage"
        ),
    }


def consumer_graph_record(root: Path) -> dict[str, Any]:
    """Return the consumer dependency graph digest and relationship counts."""

    relative_path = "consumers/dependency-graph.json"
    path = root / relative_path
    graph = load_json(path)
    consumers = graph.get("consumers")
    datasets = graph.get("datasets")
    if not isinstance(consumers, dict) or not isinstance(datasets, dict):
        raise ValueError(f"{path}: dependency graph must contain consumers and datasets")

    relationship_count = 0
    active_relationship_count = 0
    deprecated_relationship_count = 0
    repositories: set[str] = set()

    for consumer_id, payload in sorted(consumers.items()):
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: consumer {consumer_id!r} must be an object")
        repository = payload.get("repository")
        if isinstance(repository, str) and repository:
            repositories.add(repository)
        relationships = payload.get("datasets")
        if not isinstance(relationships, list):
            raise ValueError(f"{path}: consumer {consumer_id!r} datasets must be a list")
        for item in relationships:
            if not isinstance(item, dict):
                raise ValueError(
                    f"{path}: consumer {consumer_id!r} relationship must be an object"
                )
            relationship_count += 1
            status = item.get("status")
            if status == "active":
                active_relationship_count += 1
            elif status == "deprecated":
                deprecated_relationship_count += 1

    return {
        "path": relative_path,
        "schema_version": graph.get("schema_version"),
        "sha256": sha256_file(path),
        "consumer_count": len(consumers),
        "repository_count": len(repositories),
        "dataset_count": len(datasets),
        "relationship_count": relationship_count,
        "active_relationship_count": active_relationship_count,
        "deprecated_relationship_count": deprecated_relationship_count,
    }

def build_manifest(root: Path, *, tag: str, commit: str) -> dict[str, Any]:
    """Build the deterministic snapshot manifest."""

    validate_snapshot_tag(tag)
    validate_commit(commit)
    root = root.resolve()

    schemas = {
        layer: schema_record(root, layer, relative_path)
        for layer, relative_path in sorted(SCHEMA_FILES.items())
    }
    return {
        "manifest_version": 4,
        "repository": REPOSITORY,
        "tag": tag,
        "commit": commit,
        "catalogs": {
            "canonical": catalog_record(root, "datasets/catalog.json"),
            "consumer": catalog_record(root, "consumers/catalog.json"),
            "external": catalog_record(root, "external/catalog.json"),
        },
        "consumer_registry": consumer_graph_record(root),
        "canonical_expansion": canonical_expansion_record(root),
        "provenance_debt": provenance_debt_record(root),
        "metadata_schemas": schemas,
        "canonical_datasets": canonical_dataset_records(root),
    }


def render_summary(manifest: dict[str, Any]) -> str:
    """Render deterministic human-readable release material."""

    datasets = manifest["canonical_datasets"]
    consumers = manifest["consumer_registry"]
    expansion = manifest["canonical_expansion"]
    debt = manifest["provenance_debt"]
    file_count = sum(len(item["files"]) for item in datasets)
    lines = [
        f"# Registry snapshot {manifest['tag']}",
        "",
        f"- Repository: `{manifest['repository']}`",
        f"- Commit: `{manifest['commit']}`",
        f"- Canonical datasets: **{len(datasets)}**",
        f"- Canonical data files: **{file_count}**",
        f"- Active canonical consumer relationships: **{consumers['active_relationship_count']}**",
        f"- Canonical consumer repositories: **{consumers['repository_count']}**",
        f"- Canonical datasets added since {expansion['baseline_snapshot']}: **{len(expansion['datasets_added_since_baseline'])}**",
        f"- Uncovered canonical datasets: **{len(expansion['uncovered_datasets'])}**",
        f"- Provenance/licensing debt items: **{debt['total_debt']}**",
        f"- Terminal debt items: **{debt['terminal_count']}**",
        f"- Actionable debt items: **{debt['actionable_count']}**",
        "",
        "## Canonical expansion and adoption",
        "",
        f"- Baseline snapshot: **{expansion['baseline_snapshot']}**",
        f"- Baseline / current canonical datasets: **{expansion['baseline_dataset_count']} / {expansion['current_dataset_count']}**",
        f"- Quality report: `{expansion['quality_report_path']}`",
        f"- Quality report SHA-256: `{expansion['quality_report_sha256']}`",
        f"- Adoption policy: `{expansion['adoption_policy_path']}`",
        f"- Adoption policy SHA-256: `{expansion['adoption_policy_sha256']}`",
        f"- Active / pinned consumer contracts: **{expansion['active_relationship_count']} / {expansion['pinned_contract_count']}**",
        f"- Pinned contract coverage: **{expansion['pinned_contract_coverage']:.0%}**",
        f"- Canonical adoption coverage: **{expansion['canonical_dataset_adoption_coverage']:.0%}**",
        f"- Uncovered canonical datasets: **{len(expansion['uncovered_datasets'])}**",
        "",
        "Datasets added since baseline:",
        "",
    ]
    if expansion["datasets_added_since_baseline"]:
        lines.extend(
            f"- `{dataset_id}`"
            for dataset_id in expansion["datasets_added_since_baseline"]
        )
    else:
        lines.append("- None")

    lines.extend(["", "Adoption exemptions:", ""])
    if expansion["exemptions"]:
        lines.extend(
            f"- `{dataset_id}`: {rationale}"
            for dataset_id, rationale in expansion["exemptions"].items()
        )
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Provenance and licensing debt",
        "",
        f"- Report: `{debt['path']}`",
        f"- Report SHA-256: `{debt['sha256']}`",
        f"- Structured / unstructured: **{debt['structured_count']} / {debt['unstructured_count']}**",
        f"- External / legacy: **{debt['external_count']} / {debt['legacy_count']}**",
        f"- Age reference date: **{debt['age_reference_date'] or 'not available'}**",
        "",
        "Blocker categories:",
        "",
    ])
    if debt["by_blocker_category"]:
        lines.extend(
            f"- `{category}`: **{count}**"
            for category, count in debt["by_blocker_category"].items()
        )
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Catalog integrity",
        "",
        "| Catalog | Schema | SHA-256 |",
        "| --- | ---: | --- |",
    ])
    for name in ("canonical", "consumer", "external"):
        record = manifest["catalogs"][name]
        lines.append(
            f"| {name} | {record['schema_version']} | `{record['sha256']}` |"
        )

    lines.extend([
        "",
        "## Metadata schemas",
        "",
        "| Layer | Version | SHA-256 |",
        "| --- | ---: | --- |",
    ])
    for layer in ("canonical", "consumer", "external", "legacy"):
        record = manifest["metadata_schemas"][layer]
        lines.append(
            f"| {layer} | {record['schema_version']} | `{record['sha256']}` |"
        )

    lines.extend([
        "",
        "## Consumer registry",
        "",
        f"- Catalog: `{manifest['catalogs']['consumer']['path']}`",
        f"- Dependency graph: `{consumers['path']}`",
        f"- Dependency graph SHA-256: `{consumers['sha256']}`",
        f"- Consumer IDs: **{consumers['consumer_count']}**",
        f"- Distinct repositories: **{consumers['repository_count']}**",
        f"- Datasets represented in dependency graph: **{consumers['dataset_count']}**",
        f"- Active relationships: **{consumers['active_relationship_count']}**",
        f"- Deprecated relationships: **{consumers['deprecated_relationship_count']}**",
        "",
        "## Canonical datasets",
        "",
    ])
    if not datasets:
        lines.append("No canonical datasets are registered in this snapshot.")
    else:
        for dataset in datasets:
            lines.append(f"### `{dataset['id']}`")
            lines.append("")
            source = dataset["source"]
            license_data = dataset["license"]
            lines.append(f"- Publisher: {source['publisher']}")
            lines.append(f"- Source: {source['url']}")
            lines.append(f"- Snapshot identity: {source['snapshot']}")
            lines.append(f"- Retrieved: {source['retrieved_at']}")
            lines.append(
                f"- Licence: {license_data['name']} "
                f"({license_data['redistribution']}) — {license_data['url']}"
            )
            for item in dataset["files"]:
                lines.append(f"- `{item['path']}` — `{item['sha256']}`")
            lines.append("")

    lines.extend([
        "",
        "This summary is generated from `snapshot-manifest.json` and contains no runtime timestamp.",
        "The tag and exact commit above are the immutable release identity.",
        "",
    ])
    return "\n".join(lines)


def write_release_material(
    root: Path,
    *,
    tag: str,
    commit: str,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Write deterministic JSON and Markdown release material."""

    manifest = build_manifest(root, tag=tag, commit=commit)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "snapshot-manifest.json"
    summary_path = output_dir / "snapshot-summary.md"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(render_summary(manifest), encoding="utf-8")
    return manifest_path, summary_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        manifest_path, summary_path = write_release_material(
            args.root,
            tag=args.tag,
            commit=args.commit,
            output_dir=args.output_dir,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Snapshot manifest: {manifest_path}")
    print(f"Snapshot summary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
