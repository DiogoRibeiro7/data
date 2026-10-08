#!/usr/bin/env python3
"""Search, inspect, verify, and fetch entries from the local data registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_registry import fetch as FETCH  # noqa: E402
from data_registry.core import (  # noqa: E402
    LAYER_CHOICES,
    RegistryEntry,
    RegistryError,
    consumer_summaries,
    consumers_for_dataset,
    datasets_for_consumer,
    entry_summary,
    fetch_entry_file,
    filter_debt_items,
    filter_layer,
    find_consumer,
    find_debt_item,
    find_entry,
    find_lifecycle_dataset,
    json_compatible,
    load_consumer_graph,
    load_lifecycle_report,
    load_provenance_debt,
    load_registry,
    replacement_payload,
    search_entries,
    show_payload,
    supersedes_payload,
)
import validate_repository as VALIDATOR  # noqa: E402


def render_consumer_summary_table(items: Sequence[dict[str, Any]]) -> str:
    """Render a compact table of consumer repositories and dataset counts."""

    if not items:
        return "No canonical consumers are registered."

    rows = [
        (
            str(item["consumer_id"]),
            str(item.get("consumer_repository") or "—"),
            str(item["dataset_count"]),
            ", ".join(str(value) for value in item["datasets"]) or "—",
        )
        for item in items
    ]
    headers = ("CONSUMER", "REPOSITORY", "DATASETS", "DATASET IDS")
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    ]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend(
        "  ".join(row[index].ljust(widths[index]) for index in range(len(headers)))
        for row in rows
    )
    return "\n".join(lines)


def render_dependency_table(
    items: Sequence[dict[str, Any]],
    *,
    mode: str,
) -> str:
    """Render dependency rows for used-by and uses queries."""

    if not items:
        return "No matching consumer dependencies."

    if mode == "used-by":
        rows = [
            (
                str(item.get("consumer_id", "")),
                str(item.get("consumer_repository", "")),
                str(item.get("status", "")),
                str(item.get("registry_commit", "")),
            )
            for item in items
        ]
        headers = ("CONSUMER", "REPOSITORY", "STATUS", "REGISTRY COMMIT")
    elif mode == "uses":
        rows = [
            (
                str(item.get("dataset_id", "")),
                str(item.get("status", "")),
                str(item.get("registry_commit", "")),
                str(item.get("path", "")),
            )
            for item in items
        ]
        headers = ("DATASET", "STATUS", "REGISTRY COMMIT", "CANONICAL PATH")
    else:
        raise RegistryError(f"unknown dependency table mode: {mode}")

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    ]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend(
        "  ".join(row[index].ljust(widths[index]) for index in range(len(headers)))
        for row in rows
    )
    return "\n".join(lines)


def render_debt_table(items: Sequence[dict[str, Any]]) -> str:
    """Render compact human-readable provenance-debt output."""

    if not items:
        return "No matching provenance debt items."

    rows = [
        (
            str(item.get("layer") or "—"),
            str(item.get("id") or "—"),
            str(item.get("review_status") or "—"),
            str(item.get("blocker_category") or "—"),
            str(item.get("age_days") if item.get("age_days") is not None else "—"),
        )
        for item in items
    ]
    headers = ("LAYER", "ID", "STATUS", "CATEGORY", "AGE")
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    ]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend(
        "  ".join(row[index].ljust(widths[index]) for index in range(len(headers)))
        for row in rows
    )
    return "\n".join(lines)


def render_lifecycle_summary(item: dict[str, Any]) -> str:
    """Render one canonical dataset lifecycle entry."""

    chain = item.get("replacement_chain")
    rendered_chain = " -> ".join(str(value) for value in chain) if isinstance(chain, list) else "—"
    return "\n".join(
        [
            f"Dataset:            {item.get('id')}",
            f"Status:             {item.get('status')}",
            f"Direct replacement: {item.get('direct_replacement') or '—'}",
            f"Preferred dataset:  {item.get('preferred_dataset_id') or '—'}",
            f"Deprecated at:      {item.get('deprecated_at') or '—'}",
            f"Replacement chain:  {rendered_chain}",
            f"Active consumers:   {item.get('active_consumer_count', 0)}",
            f"Migration needed:   {item.get('migration_needed_consumer_count', 0)}",
            f"Migration note:     {item.get('migration_note') or '—'}",
        ]
    )


def render_replacement(payload: dict[str, Any]) -> str:
    """Render preferred replacement information."""

    chain = payload.get("replacement_chain")
    rendered_chain = " -> ".join(str(value) for value in chain) if isinstance(chain, list) else "—"
    return "\n".join(
        [
            f"Dataset:            {payload.get('dataset_id')}",
            f"Status:             {payload.get('status')}",
            f"Direct replacement: {payload.get('direct_replacement') or '—'}",
            f"Preferred dataset:  {payload.get('preferred_dataset_id') or '—'}",
            f"Replacement chain:  {rendered_chain}",
            f"Migration note:     {payload.get('migration_note') or '—'}",
        ]
    )


def render_supersedes(payload: dict[str, Any]) -> str:
    """Render reverse supersession lookup."""

    direct = payload.get("direct_predecessors")
    all_items = payload.get("superseded_datasets")
    direct_text = ", ".join(str(value) for value in direct) if direct else "—"
    all_text = ", ".join(str(value) for value in all_items) if all_items else "—"
    return "\n".join(
        [
            f"Dataset:             {payload.get('dataset_id')}",
            f"Direct predecessors: {direct_text}",
            f"Superseded datasets: {all_text}",
        ]
    )


def render_table(entries: Sequence[RegistryEntry]) -> str:
    """Render compact human-readable list/search output."""

    if not entries:
        return "No matching registry entries."

    rows = [
        (entry.layer, entry.id, entry.title, entry.publisher or "—")
        for entry in entries
    ]
    headers = ("LAYER", "ID", "TITLE", "PUBLISHER")
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    ]
    lines.append("  ".join("-" * width for width in widths))
    for row in rows:
        lines.append(
            "  ".join(row[index].ljust(widths[index]) for index in range(len(headers)))
        )
    return "\n".join(lines)


def verify_entry(root: Path, entry: RegistryEntry) -> list[VALIDATOR.Problem]:
    """Run focused local integrity and metadata validation for one entry."""

    root = root.resolve()
    problems: list[VALIDATOR.Problem] = []

    if entry.layer == "canonical":
        VALIDATOR.validate_canonical_dataset(
            root, root / "datasets" / entry.id, problems
        )
        return problems

    marker = f"{entry.layer}/{entry.id}"
    if entry.layer == "external":
        all_problems: list[VALIDATOR.Problem] = []
        VALIDATOR.validate_external(root, all_problems)
    elif entry.layer == "legacy":
        all_problems = []
        VALIDATOR.validate_legacy(root, all_problems)
    else:
        raise RegistryError(f"unsupported registry layer: {entry.layer}")

    return [problem for problem in all_problems if marker in problem.message.replace("\\", "/")]


def _add_common_read_options(parser: argparse.ArgumentParser) -> None:
    """Add output mode to a read command."""

    parser.add_argument("--json", action="store_true", help="Emit JSON output.")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List registry entries.")
    list_parser.add_argument(
        "--layer", choices=("all", *LAYER_CHOICES), default="all"
    )
    _add_common_read_options(list_parser)

    search_parser = subparsers.add_parser("search", help="Search registry entries.")
    search_parser.add_argument("text")
    search_parser.add_argument(
        "--layer", choices=("all", *LAYER_CHOICES), default="all"
    )
    _add_common_read_options(search_parser)

    show_parser = subparsers.add_parser("show", help="Show one registry entry.")
    show_parser.add_argument("id")
    show_parser.add_argument("--layer", choices=LAYER_CHOICES)
    _add_common_read_options(show_parser)

    verify_parser = subparsers.add_parser("verify", help="Verify one registry entry.")
    verify_parser.add_argument("id")
    verify_parser.add_argument("--layer", choices=LAYER_CHOICES)
    _add_common_read_options(verify_parser)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch one canonical file.")
    fetch_parser.add_argument("id")
    fetch_parser.add_argument("--file", required=True, help="Path relative to dataset directory.")
    fetch_parser.add_argument("--commit", required=True, help="Exact 40-character Git commit.")
    fetch_parser.add_argument("--output", required=True, type=Path)
    fetch_parser.add_argument("--repository", default=FETCH.DEFAULT_REPOSITORY)
    fetch_parser.add_argument("--timeout", type=float, default=60.0)
    fetch_parser.add_argument("--force", action="store_true")
    fetch_parser.add_argument("--json", action="store_true", help="Emit JSON output.")

    consumers_parser = subparsers.add_parser(
        "consumers",
        help="List registered canonical consumers.",
    )
    _add_common_read_options(consumers_parser)

    consumer_parser = subparsers.add_parser(
        "consumer",
        help="Show one registered canonical consumer.",
    )
    consumer_parser.add_argument("id")
    _add_common_read_options(consumer_parser)

    used_by_parser = subparsers.add_parser(
        "used-by",
        help="List consumers of one canonical dataset.",
    )
    used_by_parser.add_argument("dataset_id")
    _add_common_read_options(used_by_parser)

    uses_parser = subparsers.add_parser(
        "uses",
        help="List canonical datasets used by one consumer.",
    )
    uses_parser.add_argument("consumer_id")
    _add_common_read_options(uses_parser)

    debt_parser = subparsers.add_parser(
        "debt",
        help="List unresolved provenance/licensing debt.",
    )
    debt_parser.add_argument(
        "--layer",
        choices=("all", "external", "legacy"),
        default="all",
    )
    debt_parser.add_argument(
        "--category",
        help="Filter by blocker category.",
    )
    debt_parser.add_argument(
        "--status",
        choices=("all", "actionable", "terminal"),
        default="all",
    )
    _add_common_read_options(debt_parser)

    debt_show_parser = subparsers.add_parser(
        "debt-show",
        help="Show one provenance/licensing debt item.",
    )
    debt_show_parser.add_argument("id")
    _add_common_read_options(debt_show_parser)

    lifecycle_parser = subparsers.add_parser(
        "lifecycle",
        help="Show canonical lifecycle state for one dataset.",
    )
    lifecycle_parser.add_argument("dataset_id")
    _add_common_read_options(lifecycle_parser)

    replacement_parser = subparsers.add_parser(
        "replacement",
        help="Resolve the preferred canonical replacement for one dataset.",
    )
    replacement_parser.add_argument("dataset_id")
    _add_common_read_options(replacement_parser)

    supersedes_parser = subparsers.add_parser(
        "supersedes",
        help="Show datasets superseded by one canonical dataset.",
    )
    supersedes_parser.add_argument("dataset_id")
    _add_common_read_options(supersedes_parser)

    return parser


def _print_json(value: Any) -> None:
    """Print stable pretty JSON."""

    print(json.dumps(json_compatible(value), indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        entries = load_registry(root)

        if args.command == "debt":
            report = load_provenance_debt(root)
            result = filter_debt_items(
                report,
                layer=args.layer,
                category=args.category,
                status=args.status,
            )
            if args.json:
                _print_json(result)
            else:
                print(render_debt_table(result))
            return 0

        if args.command == "debt-show":
            report = load_provenance_debt(root)
            payload = find_debt_item(report, args.id)
            if args.json:
                _print_json(payload)
            else:
                print(yaml.safe_dump(json_compatible(payload), sort_keys=False).rstrip())
            return 0

        if args.command == "lifecycle":
            report = load_lifecycle_report(root)
            payload = find_lifecycle_dataset(report, args.dataset_id)
            if args.json:
                _print_json(payload)
            else:
                print(render_lifecycle_summary(payload))
            return 0

        if args.command == "replacement":
            report = load_lifecycle_report(root)
            payload = replacement_payload(report, args.dataset_id)
            if args.json:
                _print_json(payload)
            else:
                print(render_replacement(payload))
            return 0

        if args.command == "supersedes":
            report = load_lifecycle_report(root)
            payload = supersedes_payload(report, args.dataset_id)
            if args.json:
                _print_json(payload)
            else:
                print(render_supersedes(payload))
            return 0

        if args.command == "list":
            result = filter_layer(entries, args.layer)
            if args.json:
                _print_json([entry_summary(entry) for entry in result])
            else:
                print(render_table(result))
            return 0

        if args.command == "search":
            result = search_entries(entries, args.text, layer=args.layer)
            if args.json:
                _print_json([entry_summary(entry) for entry in result])
            else:
                print(render_table(result))
            return 0

        if args.command == "show":
            entry = find_entry(entries, args.id, layer=args.layer)
            payload = show_payload(entry)
            if args.json:
                _print_json(payload)
            else:
                print(f"Layer: {entry.layer}")
                print(f"Path:  {entry.path}")
                print("")
                print(yaml.safe_dump(json_compatible(entry.metadata), sort_keys=False).rstrip())
            return 0

        if args.command == "verify":
            entry = find_entry(entries, args.id, layer=args.layer)
            problems = verify_entry(root, entry)
            errors = [problem for problem in problems if problem.severity == "error"]
            if args.json:
                _print_json(
                    {
                        "id": entry.id,
                        "layer": entry.layer,
                        "ok": not errors,
                        "problems": [
                            {"severity": item.severity, "message": item.message}
                            for item in problems
                        ],
                    }
                )
            elif not problems:
                print(f"OK: {entry.layer}/{entry.id}")
            else:
                for problem in problems:
                    print(f"{problem.severity.upper()}: {problem.message}")
            return 1 if errors else 0

        if args.command == "consumers":
            graph = load_consumer_graph(root)
            result = consumer_summaries(graph)
            if args.json:
                _print_json(result)
            else:
                print(render_consumer_summary_table(result))
            return 0

        if args.command == "consumer":
            graph = load_consumer_graph(root)
            payload = find_consumer(graph, args.id)
            if args.json:
                _print_json(payload)
            else:
                print(f"Consumer:   {payload['consumer_id']}")
                print(f"Repository: {payload.get('consumer_repository') or '—'}")
                print("")
                print(render_dependency_table(payload["datasets"], mode="uses"))
            return 0

        if args.command == "used-by":
            graph = load_consumer_graph(root)
            known_dataset_ids = {
                entry.id for entry in entries if entry.layer == "canonical"
            }
            result = consumers_for_dataset(
                graph,
                args.dataset_id,
                known_dataset_ids=known_dataset_ids,
            )
            if args.json:
                _print_json(result)
            else:
                print(render_dependency_table(result, mode="used-by"))
            return 0

        if args.command == "uses":
            graph = load_consumer_graph(root)
            result = datasets_for_consumer(graph, args.consumer_id)
            if args.json:
                _print_json(result)
            else:
                print(render_dependency_table(result, mode="uses"))
            return 0

        if args.command == "fetch":
            entry = find_entry(entries, args.id, layer="canonical")
            output, repository_path, checksum = fetch_entry_file(
                entry,
                args.file,
                commit=args.commit,
                output=args.output,
                repository=args.repository,
                timeout=args.timeout,
                force=args.force,
            )
            payload = {
                "id": entry.id,
                "commit": args.commit,
                "repository": args.repository,
                "path": repository_path,
                "sha256": checksum,
                "output": str(output),
            }
            if args.json:
                _print_json(payload)
            else:
                print(f"Verified dataset file: {output}")
                print(f"Commit: {args.commit}")
                print(f"SHA-256: {checksum}")
            return 0

        raise RegistryError(f"unknown command: {args.command}")
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
