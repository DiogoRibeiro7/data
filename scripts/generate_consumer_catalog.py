#!/usr/bin/env python3
"""Generate or verify deterministic canonical-consumer catalog artifacts."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_record(path: Path) -> dict[str, Any]:
    """Load one consumer relationship mapping."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: consumer record root must be a mapping")
    return raw


def relationship_entry(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return the stable catalog representation of one relationship."""

    entry: dict[str, Any] = {
        "consumer_id": metadata["consumer_id"],
        "consumer_repository": metadata["consumer_repository"],
        "dataset_id": metadata["dataset_id"],
        "status": metadata["status"],
        "registry_repository": metadata["registry_repository"],
        "registry_commit": metadata["registry_commit"],
        "path": metadata["path"],
        "sha256": metadata["sha256"],
    }

    for key in ("output", "consumer_commit", "evidence_url"):
        value = metadata.get(key)
        if isinstance(value, str) and value:
            entry[key] = value

    migration = metadata.get("migration")
    if isinstance(migration, dict):
        entry["migration"] = migration

    return entry


def build_catalog(consumers_root: Path) -> dict[str, Any]:
    """Build the deterministic relationship catalog."""

    relationships: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    if consumers_root.is_dir():
        for consumer_dir in sorted(path for path in consumers_root.iterdir() if path.is_dir()):
            for record_path in sorted(consumer_dir.glob("*.yaml")):
                metadata = load_record(record_path)
                relationship = (
                    str(metadata.get("consumer_id", "")),
                    str(metadata.get("dataset_id", "")),
                )
                if relationship in seen:
                    raise ValueError(
                        f"{record_path}: duplicate consumer/dataset relationship "
                        f"{relationship[0]} -> {relationship[1]}"
                    )
                seen.add(relationship)
                relationships.append(relationship_entry(metadata))

    relationships.sort(key=lambda item: (item["consumer_id"], item["dataset_id"]))
    return {"schema_version": 1, "relationships": relationships}


def build_dependency_graph(catalog: dict[str, Any]) -> dict[str, Any]:
    """Build consumer-to-dataset and dataset-to-consumer reverse views."""

    consumer_view: dict[str, dict[str, Any]] = {}
    dataset_view: dict[str, dict[str, Any]] = {}

    for item in catalog["relationships"]:
        consumer_id = item["consumer_id"]
        dataset_id = item["dataset_id"]

        consumer = consumer_view.get(consumer_id)
        if consumer is None:
            consumer = {
                "repository": item["consumer_repository"],
                "datasets": [],
            }
            consumer_view[consumer_id] = consumer
        elif consumer["repository"] != item["consumer_repository"]:
            raise ValueError(
                f"consumer {consumer_id}: conflicting consumer_repository values"
            )
        consumer_dataset = {
            "dataset_id": dataset_id,
            "status": item["status"],
            "registry_commit": item["registry_commit"],
            "path": item["path"],
            "sha256": item["sha256"],
        }
        if isinstance(item.get("migration"), dict):
            consumer_dataset["migration"] = item["migration"]
        consumer["datasets"].append(consumer_dataset)

        dataset = dataset_view.setdefault(dataset_id, {"consumers": []})
        dataset_consumer = {
            "consumer_id": consumer_id,
            "consumer_repository": item["consumer_repository"],
            "status": item["status"],
            "registry_commit": item["registry_commit"],
            "path": item["path"],
            "sha256": item["sha256"],
        }
        if isinstance(item.get("migration"), dict):
            dataset_consumer["migration"] = item["migration"]
        dataset["consumers"].append(dataset_consumer)

    for consumer in consumer_view.values():
        consumer["datasets"].sort(key=lambda item: item["dataset_id"])
    for dataset in dataset_view.values():
        dataset["consumers"].sort(key=lambda item: item["consumer_id"])

    return {
        "schema_version": 1,
        "consumers": dict(sorted(consumer_view.items())),
        "datasets": dict(sorted(dataset_view.items())),
    }


def _markdown_cell(value: object) -> str:
    """Escape plain text embedded in a Markdown table cell."""

    text = str(value).replace("\\", "\\\\")
    return text.replace("|", "\\|").replace("\n", "<br>")


def _markdown_code_cell(value: object) -> str:
    """Render code-like table content without breaking pipe-delimited rows."""

    text = str(value)
    if not any(char in text for char in ("|", "\\", "\n", "`", "<", ">", "&")):
        return f"`{text}`"
    escaped = html.escape(text, quote=False).replace("|", "&#124;").replace("\n", "<br>")
    return f"<code>{escaped}</code>"


def render_markdown(catalog: dict[str, Any]) -> str:
    """Render the human-readable consumer catalog."""

    relationships = catalog["relationships"]
    lines = [
        "# Canonical consumer catalog",
        "",
        "This file is generated from `consumers/<consumer-id>/<dataset-id>.yaml` records.",
        "Do not edit it by hand.",
        "",
    ]

    if not relationships:
        lines.extend(["No canonical consumer relationships are registered yet.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "| Consumer | Dataset | Status | Migration | Registry commit | Canonical path | SHA-256 | Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for item in relationships:
        record_path = f"{item['consumer_id']}/{item['dataset_id']}.yaml"
        evidence_url = item.get("evidence_url")
        evidence = f"[evidence]({evidence_url})" if evidence_url else "—"
        migration = item.get("migration")
        migration_status = (
            migration.get("status")
            if isinstance(migration, dict)
            else "—"
        )
        lines.append(
            f"| [{_markdown_cell(item['consumer_repository'])}]({record_path}) | "
            f"{_markdown_code_cell(item['dataset_id'])} | {_markdown_cell(item['status'])} | "
            f"{_markdown_cell(migration_status)} | "
            f"{_markdown_code_cell(item['registry_commit'])} | "
            f"{_markdown_code_cell(item['path'])} | "
            f"{_markdown_code_cell(item['sha256'])} | {evidence} |"
        )

    lines.append("")
    return "\n".join(lines)


def expected_outputs(root: Path) -> tuple[str, str, str]:
    """Return JSON catalog, Markdown catalog, and dependency graph text."""

    catalog = build_catalog(root / "consumers")
    graph = build_dependency_graph(catalog)
    return (
        json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        render_markdown(catalog),
        json.dumps(graph, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )


def run(root: Path, *, write: bool) -> list[str]:
    """Write generated artifacts or return freshness errors."""

    catalog_json, catalog_markdown, graph_json = expected_outputs(root)
    outputs = [
        (root / "consumers" / "catalog.json", catalog_json),
        (root / "consumers" / "CATALOG.md", catalog_markdown),
        (root / "consumers" / "dependency-graph.json", graph_json),
    ]

    if write:
        (root / "consumers").mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: generated consumer artifact is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path}: consumer artifact is stale; run with --write")
    return errors


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
        "--write",
        action="store_true",
        help="Regenerate consumer catalog artifacts.",
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
        print("Consumer catalog artifacts updated.")
    else:
        print("Consumer catalog artifacts are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
