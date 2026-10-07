#!/usr/bin/env python3
"""Generate or verify deterministic canonical lifecycle reports."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML mapping."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def _iso_date(value: object) -> str | None:
    """Normalize YAML-native date values."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and value:
        return value
    return None


def _lifecycle(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return normalized lifecycle metadata, defaulting to active."""

    raw = metadata.get("lifecycle")
    if not isinstance(raw, dict):
        return {
            "status": "active",
            "deprecated_at": None,
            "supersedes": [],
            "superseded_by": None,
            "migration_note": None,
        }

    supersedes = raw.get("supersedes")
    return {
        "status": raw.get("status", "active"),
        "deprecated_at": _iso_date(raw.get("deprecated_at")),
        "supersedes": (
            sorted(item for item in supersedes if isinstance(item, str))
            if isinstance(supersedes, list)
            else []
        ),
        "superseded_by": (
            raw.get("superseded_by")
            if isinstance(raw.get("superseded_by"), str)
            else None
        ),
        "migration_note": (
            raw.get("migration_note")
            if isinstance(raw.get("migration_note"), str)
            else None
        ),
    }


def load_canonical(root: Path) -> dict[str, dict[str, Any]]:
    """Load canonical metadata indexed by dataset ID."""

    datasets: dict[str, dict[str, Any]] = {}
    datasets_root = root / "datasets"
    if not datasets_root.is_dir():
        return datasets

    for dataset_dir in sorted(path for path in datasets_root.iterdir() if path.is_dir()):
        metadata_path = dataset_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_yaml(metadata_path)
        dataset_id = metadata.get("id")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ValueError(f"{metadata_path}: missing dataset id")
        datasets[dataset_id] = metadata

    return dict(sorted(datasets.items()))


def build_edges(
    datasets: dict[str, dict[str, Any]],
) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Build one deterministic replacement edge per superseded dataset."""

    candidates: dict[str, set[str]] = {dataset_id: set() for dataset_id in datasets}

    for dataset_id, metadata in datasets.items():
        lifecycle = _lifecycle(metadata)
        replacement = lifecycle["superseded_by"]
        if isinstance(replacement, str):
            if replacement not in datasets:
                raise ValueError(
                    f"{dataset_id}: superseded_by references unknown dataset {replacement!r}"
                )
            candidates[dataset_id].add(replacement)

        for older_id in lifecycle["supersedes"]:
            if older_id not in datasets:
                raise ValueError(
                    f"{dataset_id}: supersedes references unknown dataset {older_id!r}"
                )
            candidates[older_id].add(dataset_id)

    edges: dict[str, str] = {}
    reverse: dict[str, list[str]] = {dataset_id: [] for dataset_id in datasets}
    for dataset_id, targets in sorted(candidates.items()):
        if len(targets) > 1:
            rendered = ", ".join(sorted(targets))
            raise ValueError(f"{dataset_id}: ambiguous direct replacements: {rendered}")
        if targets:
            target = next(iter(targets))
            edges[dataset_id] = target
            reverse[target].append(dataset_id)

    for predecessors in reverse.values():
        predecessors.sort()
    return edges, reverse


def replacement_chain(
    dataset_id: str,
    edges: dict[str, str],
) -> list[str]:
    """Return the replacement chain starting at *dataset_id*."""

    chain = [dataset_id]
    seen = {dataset_id}
    current = dataset_id
    while current in edges:
        current = edges[current]
        if current in seen:
            raise ValueError(
                "lifecycle replacement cycle while rendering: "
                + " -> ".join(chain + [current])
            )
        seen.add(current)
        chain.append(current)
    return chain


def load_consumer_relationships(root: Path) -> list[dict[str, Any]]:
    """Return canonical consumer relationships deterministically."""

    path = root / "consumers" / "catalog.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    relationships = raw.get("relationships")
    if not isinstance(relationships, list):
        raise ValueError(f"{path}: relationships must be a list")

    result = [item for item in relationships if isinstance(item, dict)]
    result.sort(
        key=lambda item: (
            str(item.get("consumer_id", "")),
            str(item.get("dataset_id", "")),
        )
    )
    return result


def build_report(root: Path) -> dict[str, Any]:
    """Build deterministic lifecycle, replacement, and migration state."""

    datasets = load_canonical(root)
    edges, reverse = build_edges(datasets)
    consumers = load_consumer_relationships(root)
    active_consumers = [
        item for item in consumers if item.get("status") == "active"
    ]

    consumers_by_dataset: dict[str, list[dict[str, Any]]] = {
        dataset_id: [] for dataset_id in datasets
    }
    for relationship in active_consumers:
        dataset_id = relationship.get("dataset_id")
        if isinstance(dataset_id, str) and dataset_id in consumers_by_dataset:
            consumers_by_dataset[dataset_id].append(relationship)

    dataset_items: list[dict[str, Any]] = []
    migration_items: list[dict[str, Any]] = []

    for dataset_id, metadata in datasets.items():
        lifecycle = _lifecycle(metadata)
        chain = replacement_chain(dataset_id, edges)
        terminal = chain[-1]
        status = str(lifecycle["status"])
        preferred = terminal if status == "superseded" else (
            dataset_id if status == "active" else None
        )
        dataset_consumers = consumers_by_dataset[dataset_id]
        unresolved_migrations = 0
        for relationship in dataset_consumers:
            migration = relationship.get("migration")
            migration_status = (
                migration.get("status")
                if isinstance(migration, dict)
                else None
            )
            if status in {"superseded", "deprecated"}:
                if migration_status in {None, "required", "planned"}:
                    unresolved_migrations += 1

        dataset_items.append(
            {
                "id": dataset_id,
                "title": metadata.get("title", dataset_id),
                "status": status,
                "deprecated_at": lifecycle["deprecated_at"],
                "migration_note": lifecycle["migration_note"],
                "direct_replacement": edges.get(dataset_id),
                "direct_predecessors": reverse[dataset_id],
                "preferred_dataset_id": preferred,
                "replacement_chain": chain,
                "active_consumer_count": len(dataset_consumers),
                "migration_needed_consumer_count": unresolved_migrations,
            }
        )

        for relationship in dataset_consumers:
            migration = relationship.get("migration")
            declared_status = (
                migration.get("status")
                if isinstance(migration, dict)
                else None
            )
            rationale = (
                migration.get("rationale")
                if isinstance(migration, dict)
                else None
            )
            target_dataset_id = (
                migration.get("target_dataset_id")
                if isinstance(migration, dict)
                else None
            )

            if status == "active":
                effective_status = "current"
                preferred_id = dataset_id
            elif declared_status == "retained":
                effective_status = "retained"
                preferred_id = terminal if status == "superseded" else target_dataset_id
            elif declared_status == "planned":
                effective_status = "planned"
                preferred_id = target_dataset_id or terminal
            else:
                effective_status = "required"
                preferred_id = target_dataset_id or (
                    terminal if status == "superseded" else None
                )

            migration_items.append(
                {
                    "consumer_id": relationship.get("consumer_id"),
                    "consumer_repository": relationship.get("consumer_repository"),
                    "dataset_id": dataset_id,
                    "status": effective_status,
                    "preferred_dataset_id": preferred_id or dataset_id,
                    "rationale": rationale,
                }
            )

    for relationship in consumers:
        if relationship.get("status") != "deprecated":
            continue
        migration = relationship.get("migration")
        if not isinstance(migration, dict) or migration.get("status") != "migrated":
            continue
        migration_items.append(
            {
                "consumer_id": relationship.get("consumer_id"),
                "consumer_repository": relationship.get("consumer_repository"),
                "dataset_id": relationship.get("dataset_id"),
                "status": "migrated",
                "preferred_dataset_id": migration.get("target_dataset_id"),
                "rationale": migration.get("rationale"),
            }
        )

    dataset_items.sort(key=lambda item: str(item["id"]))
    migration_items.sort(
        key=lambda item: (
            str(item["consumer_id"]),
            str(item["dataset_id"]),
        )
    )

    status_counts = {
        state: sum(item["status"] == state for item in dataset_items)
        for state in ("active", "deprecated", "superseded")
    }
    migration_counts = {
        state: sum(item["status"] == state for item in migration_items)
        for state in ("current", "required", "planned", "retained", "migrated")
    }
    affected_active = (
        migration_counts["required"]
        + migration_counts["planned"]
        + migration_counts["retained"]
    )
    resolved_active = migration_counts["planned"] + migration_counts["retained"]
    migration_resolution_coverage = (
        resolved_active / affected_active if affected_active else 1.0
    )

    return {
        "schema_version": 1,
        "summary": {
            "canonical_dataset_count": len(dataset_items),
            "active_count": status_counts["active"],
            "deprecated_count": status_counts["deprecated"],
            "superseded_count": status_counts["superseded"],
            "replacement_edge_count": len(edges),
            "active_consumer_relationship_count": len(active_consumers),
            "current_consumer_relationship_count": migration_counts["current"],
            "migration_required_count": migration_counts["required"],
            "migration_planned_count": migration_counts["planned"],
            "migration_retained_count": migration_counts["retained"],
            "migrated_relationship_count": migration_counts["migrated"],
            "migration_needed_count": (
                migration_counts["required"] + migration_counts["planned"]
            ),
            "migration_resolution_coverage": migration_resolution_coverage,
        },
        "preferred_replacements": dict(sorted(edges.items())),
        "datasets": dataset_items,
        "consumer_migrations": migration_items,
    }


def _cell(value: object) -> str:
    """Escape a plain Markdown table cell."""

    if value is None:
        return "--"
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def render_markdown(report: dict[str, Any]) -> str:
    """Render the lifecycle report as Markdown."""

    summary = report["summary"]
    lines = [
        "# Canonical dataset lifecycle",
        "",
        "This report is generated deterministically from committed canonical metadata",
        "and the committed consumer catalog. Do not edit it by hand.",
        "",
        f"- Canonical datasets: **{summary['canonical_dataset_count']}**",
        f"- Active: **{summary['active_count']}**",
        f"- Deprecated: **{summary['deprecated_count']}**",
        f"- Superseded: **{summary['superseded_count']}**",
        f"- Replacement edges: **{summary['replacement_edge_count']}**",
        f"- Active consumer relationships: **{summary['active_consumer_relationship_count']}**",
        f"- Current consumer relationships: **{summary['current_consumer_relationship_count']}**",
        f"- Migration required: **{summary['migration_required_count']}**",
        f"- Migration planned: **{summary['migration_planned_count']}**",
        f"- Intentionally retained: **{summary['migration_retained_count']}**",
        f"- Historical migrated relationships: **{summary['migrated_relationship_count']}**",
        f"- Migration needed: **{summary['migration_needed_count']}**",
        f"- Migration resolution coverage: **{summary['migration_resolution_coverage']:.0%}**",
        "",
        "## Dataset lifecycle",
        "",
        "| Dataset | Status | Direct replacement | Preferred dataset | Consumers | Migration needed |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]

    for item in report["datasets"]:
        lines.append(
            f"| `{_cell(item['id'])}` | {_cell(item['status'])} | "
            f"{_cell(item['direct_replacement'])} | "
            f"{_cell(item['preferred_dataset_id'])} | "
            f"{item['active_consumer_count']} | "
            f"{item['migration_needed_consumer_count']} |"
        )

    lines.extend(["", "## Replacement chains", ""])
    nontrivial = [
        item for item in report["datasets"] if len(item["replacement_chain"]) > 1
    ]
    if nontrivial:
        for item in nontrivial:
            chain = " -> ".join(
                f"`{dataset_id}`" for dataset_id in item["replacement_chain"]
            )
            lines.append(f"- {chain}")
    else:
        lines.append("- No supersession chains are currently registered.")

    lines.extend(["", "## Consumer migration state", ""])
    if report["consumer_migrations"]:
        lines.extend(
            [
                "| Consumer | Dataset | State | Preferred dataset | Rationale |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in report["consumer_migrations"]:
            lines.append(
                f"| `{_cell(item['consumer_id'])}` | "
                f"`{_cell(item['dataset_id'])}` | {_cell(item['status'])} | "
                f"`{_cell(item['preferred_dataset_id'])}` | "
                f"{_cell(item.get('rationale'))} |"
            )
    else:
        lines.append("No active canonical consumer relationships are registered.")

    lines.extend(
        [
            "",
            "## Semantics",
            "",
            "- Missing lifecycle metadata is interpreted as `active`.",
            "- Replacement edges are derived from committed `supersedes` and `superseded_by` declarations.",
            "- A superseded dataset's preferred replacement is the active terminal dataset in its replacement chain.",
            "- Active consumers of superseded/deprecated datasets are classified as required, planned, or retained.",
            "- Retained historical consumption requires an explicit rationale.",
            "- Deprecated historical relationships may record migration.status=migrated when a matching active target relationship exists.",
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
    """Write lifecycle reports or return freshness errors."""

    json_text, markdown_text = expected_outputs(root)
    outputs = [
        (root / "reports" / "lifecycle.json", json_text),
        (root / "reports" / "lifecycle.md", markdown_text),
    ]

    if write:
        (root / "reports").mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: generated lifecycle report is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path}: lifecycle report is stale; run with --write")
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
        help="Regenerate lifecycle reports.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        errors = run(args.root.resolve(), write=args.write)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.write:
        print("Lifecycle reports updated.")
    else:
        print("Lifecycle reports are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
