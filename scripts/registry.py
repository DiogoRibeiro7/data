#!/usr/bin/env python3
"""Search, inspect, verify, and fetch entries from the local data registry."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml

import fetch_dataset as FETCH
import validate_repository as VALIDATOR

LAYER_ORDER = {"canonical": 0, "external": 1, "legacy": 2}
LAYER_CHOICES = ("canonical", "external", "legacy")


class RegistryError(RuntimeError):
    """A user-facing registry operation error."""


@dataclass(frozen=True)
class RegistryEntry:
    """One normalized registry entry."""

    layer: str
    id: str
    title: str
    path: str
    metadata: dict[str, Any]

    @property
    def publisher(self) -> str:
        """Return a publisher/source label when available."""

        if self.layer == "canonical":
            source = self.metadata.get("source")
            if isinstance(source, dict):
                value = source.get("publisher")
                if isinstance(value, str):
                    return value
        if self.layer == "external":
            value = self.metadata.get("publisher")
            if isinstance(value, str):
                return value
        if self.layer == "legacy":
            source = self.metadata.get("source")
            if isinstance(source, dict):
                value = source.get("publisher")
                if isinstance(value, str):
                    return value
        return ""

    @property
    def description(self) -> str:
        """Return a searchable description when present."""

        value = self.metadata.get("description")
        return value if isinstance(value, str) else ""

    @property
    def domains(self) -> list[str]:
        """Return normalized canonical-domain tags."""

        value = self.metadata.get("domain")
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]


def json_compatible(value: Any) -> Any:
    """Convert YAML-native values into JSON-compatible values."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_compatible(item) for item in value]
    return value


def load_metadata(path: Path) -> dict[str, Any]:
    """Load one metadata file as a mapping."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RegistryError(f"{path}: cannot load metadata: {exc}") from exc
    if not isinstance(raw, dict):
        raise RegistryError(f"{path}: metadata root must be a mapping")
    return raw


def _entries_from_layer(root: Path, layer: str) -> list[RegistryEntry]:
    """Load entries from one registry layer."""

    directory_name = {
        "canonical": "datasets",
        "external": "external",
        "legacy": "legacy",
    }[layer]
    layer_root = root / directory_name
    if not layer_root.is_dir():
        return []

    entries: list[RegistryEntry] = []
    for item in sorted(path for path in layer_root.iterdir() if path.is_dir()):
        metadata_path = item / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_metadata(metadata_path)
        entry_id = metadata.get("id")
        title = metadata.get("title")
        if not isinstance(entry_id, str) or not entry_id:
            raise RegistryError(f"{metadata_path}: missing non-empty id")
        if not isinstance(title, str) or not title:
            title = entry_id
        entries.append(
            RegistryEntry(
                layer=layer,
                id=entry_id,
                title=title,
                path=str(item.relative_to(root)),
                metadata=metadata,
            )
        )
    return entries


def load_registry(root: Path) -> list[RegistryEntry]:
    """Load all registry layers deterministically."""

    root = root.resolve()
    entries: list[RegistryEntry] = []
    for layer in LAYER_CHOICES:
        entries.extend(_entries_from_layer(root, layer))
    entries.sort(key=lambda item: (LAYER_ORDER[item.layer], item.id))
    return entries


def filter_layer(entries: Iterable[RegistryEntry], layer: str) -> list[RegistryEntry]:
    """Filter entries by layer or return all."""

    if layer == "all":
        return list(entries)
    return [entry for entry in entries if entry.layer == layer]


def search_entries(
    entries: Iterable[RegistryEntry],
    query: str,
    *,
    layer: str = "all",
) -> list[RegistryEntry]:
    """Search IDs, titles, publishers, descriptions, and domains."""

    needle = query.casefold().strip()
    if not needle:
        return []
    matches: list[RegistryEntry] = []
    for entry in filter_layer(entries, layer):
        haystack = "\n".join(
            [entry.id, entry.title, entry.publisher, entry.description, *entry.domains]
        ).casefold()
        if needle in haystack:
            matches.append(entry)
    return matches


def find_entry(
    entries: Iterable[RegistryEntry],
    entry_id: str,
    *,
    layer: str | None = None,
) -> RegistryEntry:
    """Find one exact ID, requiring disambiguation across layers when necessary."""

    matches = [
        entry
        for entry in entries
        if entry.id == entry_id and (layer is None or entry.layer == layer)
    ]
    if not matches:
        suffix = f" in layer {layer}" if layer else ""
        raise RegistryError(f"unknown registry id {entry_id!r}{suffix}")
    if len(matches) > 1:
        layers = ", ".join(entry.layer for entry in matches)
        raise RegistryError(
            f"registry id {entry_id!r} is ambiguous across layers: {layers}; use --layer"
        )
    return matches[0]


def entry_summary(entry: RegistryEntry) -> dict[str, Any]:
    """Return a stable compact representation for list/search output."""

    return {
        "layer": entry.layer,
        "id": entry.id,
        "title": entry.title,
        "publisher": entry.publisher or None,
        "domains": entry.domains,
        "path": entry.path,
    }


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


def show_payload(entry: RegistryEntry) -> dict[str, Any]:
    """Return detailed show output."""

    return {
        "layer": entry.layer,
        "path": entry.path,
        "metadata": json_compatible(entry.metadata),
    }


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


def canonical_file_metadata(entry: RegistryEntry, relative_path: str) -> dict[str, Any]:
    """Return metadata for one canonical file."""

    if entry.layer != "canonical":
        raise RegistryError("fetch is available only for canonical datasets")
    files = entry.metadata.get("files")
    if not isinstance(files, list):
        raise RegistryError(f"{entry.id}: canonical metadata has no files list")
    for item in files:
        if isinstance(item, dict) and item.get("path") == relative_path:
            return item
    raise RegistryError(
        f"{entry.id}: canonical file {relative_path!r} is not declared in metadata"
    )


def fetch_entry_file(
    entry: RegistryEntry,
    relative_path: str,
    *,
    commit: str,
    output: Path,
    repository: str = FETCH.DEFAULT_REPOSITORY,
    timeout: float = 60.0,
    force: bool = False,
    base_url: str = FETCH.DEFAULT_RAW_BASE_URL,
) -> tuple[Path, str, str]:
    """Fetch one canonical file using its metadata SHA-256."""

    file_metadata = canonical_file_metadata(entry, relative_path)
    checksum = file_metadata.get("sha256")
    if not isinstance(checksum, str):
        raise RegistryError(f"{entry.id}: {relative_path} has no SHA-256")
    repository_path = f"datasets/{entry.id}/{relative_path}"
    try:
        reference = FETCH.DatasetReference(
            repository=repository,
            commit=commit,
            path=repository_path,
            sha256=checksum,
        )
        result = FETCH.fetch_dataset_file(
            reference,
            output,
            base_url=base_url,
            timeout_seconds=timeout,
            force=force,
        )
    except (ValueError, TypeError, FileExistsError, RuntimeError) as exc:
        raise RegistryError(str(exc)) from exc
    return result, repository_path, checksum


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
