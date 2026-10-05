#!/usr/bin/env python3
"""Generate or verify deterministic provenance/licensing debt reports."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one metadata YAML mapping."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def redistribution_policy(metadata: dict[str, Any]) -> str:
    """Return normalized redistribution state for one external record."""

    value = metadata.get("redistribution")
    if isinstance(value, str) and value.strip():
        return value.strip()

    usage = metadata.get("usage")
    if isinstance(usage, dict):
        nested = usage.get("redistribution")
        if isinstance(nested, str) and nested.strip():
            return nested.strip()

    return "unresolved"


def _iso_date(value: object) -> str | None:
    """Normalize YAML date/string values to an ISO date string."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and value:
        return value
    return None


def _resolution_projection(metadata: dict[str, Any]) -> dict[str, Any]:
    """Project optional structured resolution evidence into report fields."""

    resolution = metadata.get("resolution")
    if not isinstance(resolution, dict):
        return {
            "structured_evidence": False,
            "review_status": None,
            "terminal": None,
            "blocker_category": None,
            "blocker_summary": "Structured resolution evidence not yet recorded.",
            "last_reviewed": None,
            "evidence_count": 0,
            "next_action": "Backfill structured resolution evidence.",
        }

    evidence = resolution.get("evidence")
    evidence_count = len(evidence) if isinstance(evidence, list) else 0
    return {
        "structured_evidence": True,
        "review_status": resolution.get("review_status"),
        "terminal": resolution.get("terminal"),
        "blocker_category": resolution.get("blocker_category"),
        "blocker_summary": resolution.get("blocker_summary"),
        "last_reviewed": _iso_date(resolution.get("last_reviewed")),
        "evidence_count": evidence_count,
        "next_action": resolution.get("next_action"),
    }


def _external_debt_items(root: Path) -> list[dict[str, Any]]:
    """Return unresolved or otherwise explicitly blocked external records."""

    external_root = root / "external"
    items: list[dict[str, Any]] = []
    if not external_root.is_dir():
        return items

    for source_dir in sorted(path for path in external_root.iterdir() if path.is_dir()):
        metadata_path = source_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_yaml(metadata_path)
        redistribution = redistribution_policy(metadata)
        has_resolution = isinstance(metadata.get("resolution"), dict)
        if redistribution != "unresolved" and not has_resolution:
            continue

        item = {
            "id": metadata.get("id", source_dir.name),
            "layer": "external",
            "title": metadata.get("title", source_dir.name),
            "path": f"external/{source_dir.name}/metadata.yaml",
            "redistribution": redistribution,
        }
        item.update(_resolution_projection(metadata))
        items.append(item)

    return items


def _legacy_debt_items(root: Path) -> list[dict[str, Any]]:
    """Return all remaining legacy quarantine packages."""

    legacy_root = root / "legacy"
    items: list[dict[str, Any]] = []
    if not legacy_root.is_dir():
        return items

    for package_dir in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        metadata_path = package_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_yaml(metadata_path)

        license_data = metadata.get("license")
        redistribution = None
        if isinstance(license_data, dict):
            value = license_data.get("redistribution")
            if isinstance(value, str) and value:
                redistribution = value

        item = {
            "id": metadata.get("id", package_dir.name),
            "layer": "legacy",
            "title": metadata.get("title", package_dir.name),
            "path": f"legacy/{package_dir.name}/metadata.yaml",
            "redistribution": redistribution or "unknown",
        }
        item.update(_resolution_projection(metadata))
        items.append(item)

    return items


def _age_reference(items: list[dict[str, Any]]) -> date | None:
    """Return the latest structured review date in the queue."""

    dates: list[date] = []
    for item in items:
        value = item.get("last_reviewed")
        if not isinstance(value, str):
            continue
        try:
            dates.append(date.fromisoformat(value))
        except ValueError:
            continue
    return max(dates) if dates else None


def build_report(root: Path) -> dict[str, Any]:
    """Build the deterministic provenance/licensing debt report."""

    items = _external_debt_items(root) + _legacy_debt_items(root)
    items.sort(key=lambda item: (str(item["layer"]), str(item["id"])))

    reference_date = _age_reference(items)
    for item in items:
        last_reviewed = item.get("last_reviewed")
        if reference_date is None or not isinstance(last_reviewed, str):
            item["age_days"] = None
            continue
        item["age_days"] = (
            reference_date - date.fromisoformat(last_reviewed)
        ).days

    category_counts: Counter[str] = Counter()
    for item in items:
        category = item.get("blocker_category")
        category_counts[str(category) if category else "unstructured"] += 1

    return {
        "schema_version": 1,
        "age_reference_date": reference_date.isoformat() if reference_date else None,
        "summary": {
            "total_debt": len(items),
            "external_count": sum(item["layer"] == "external" for item in items),
            "legacy_count": sum(item["layer"] == "legacy" for item in items),
            "structured_count": sum(bool(item["structured_evidence"]) for item in items),
            "unstructured_count": sum(not bool(item["structured_evidence"]) for item in items),
            "actionable_count": sum(item.get("review_status") == "actionable" for item in items),
            "terminal_count": sum(item.get("review_status") == "terminal" for item in items),
            "by_blocker_category": dict(sorted(category_counts.items())),
        },
        "items": items,
    }


def _markdown_cell(value: object) -> str:
    """Escape plain text for a Markdown table cell."""

    if value is None:
        return "—"
    text = str(value).replace("\\", "\\\\")
    return text.replace("|", "\\|").replace("\n", "<br>")


def render_markdown(report: dict[str, Any]) -> str:
    """Render the human-readable provenance debt queue."""

    summary = report["summary"]
    reference = report["age_reference_date"]
    lines = [
        "# Provenance and licensing debt queue",
        "",
        "This file is generated deterministically from committed external and legacy metadata.",
        "Do not edit it by hand.",
        "",
        f"- Total debt items: **{summary['total_debt']}**",
        f"- External records: **{summary['external_count']}**",
        f"- Legacy packages: **{summary['legacy_count']}**",
        f"- Structured evidence: **{summary['structured_count']}**",
        f"- Unstructured debt: **{summary['unstructured_count']}**",
        f"- Actionable: **{summary['actionable_count']}**",
        f"- Terminal: **{summary['terminal_count']}**",
        f"- Age reference date: **{reference or 'not available'}**",
        "",
        "## Blocker categories",
        "",
    ]

    for category, count in summary["by_blocker_category"].items():
        lines.append(f"- `{category}`: **{count}**")

    lines.extend(
        [
            "",
            "## Queue",
            "",
            "| Layer | ID | Review status | Blocker | Last reviewed | Age (days) | Evidence | Redistribution | Next action |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )

    for item in report["items"]:
        lines.append(
            f"| {_markdown_cell(item['layer'])} | "
            f"`{_markdown_cell(item['id'])}` | "
            f"{_markdown_cell(item['review_status'])} | "
            f"{_markdown_cell(item['blocker_category'])} | "
            f"{_markdown_cell(item['last_reviewed'])} | "
            f"{_markdown_cell(item['age_days'])} | "
            f"{item['evidence_count']} | "
            f"{_markdown_cell(item['redistribution'])} | "
            f"{_markdown_cell(item['next_action'])} |"
        )

    lines.extend(
        [
            "",
            "## Age semantics",
            "",
            "Age is deterministic and content-based. When structured review dates exist,",
            "the reference date is the latest `last_reviewed` date present in the queue.",
            "Items without structured review dates have no age value.",
            "",
            "Unstructured debt remains visible so introducing the queue does not hide",
            "records that have not yet been migrated to the structured resolution model.",
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

    json_text, markdown_text = expected_outputs(root)
    reports = root / "reports"
    outputs = [
        (reports / "provenance-debt.json", json_text),
        (reports / "provenance-debt.md", markdown_text),
    ]

    if write:
        reports.mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: generated provenance debt report is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path}: provenance debt report is stale; run with --write")
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
        help="Regenerate provenance debt reports.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        errors = run(args.root.resolve(), write=args.write)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.write:
        print("Provenance debt reports updated.")
    else:
        print("Provenance debt reports are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
