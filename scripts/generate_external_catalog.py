#!/usr/bin/env python3
"""Generate or verify the external source catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_metadata(path: Path) -> dict[str, Any]:
    """Load one external metadata mapping."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def storage_policy(metadata: dict[str, Any]) -> str:
    """Return normalized storage policy."""

    value = metadata.get("storage")
    if isinstance(value, str) and value.strip():
        return value.strip()
    usage = metadata.get("usage")
    if isinstance(usage, dict):
        value = usage.get("storage")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unresolved"


def redistribution_policy(metadata: dict[str, Any]) -> str:
    """Return normalized redistribution policy."""

    value = metadata.get("redistribution")
    if isinstance(value, str) and value.strip():
        return value.strip()
    usage = metadata.get("usage")
    if isinstance(usage, dict):
        value = usage.get("redistribution")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unresolved"


def catalog_entry(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build one stable catalog entry."""

    license_data = metadata.get("license")
    license_entry = None
    if isinstance(license_data, dict):
        license_entry = {
            "name": license_data.get("name"),
            "url": license_data.get("url"),
        }

    consumers = metadata.get("consumers")
    if not isinstance(consumers, list):
        consumers = []

    return {
        "id": metadata["id"],
        "title": metadata["title"],
        "publisher": metadata["publisher"],
        "source_url": metadata["source_url"],
        "license": license_entry,
        "redistribution": redistribution_policy(metadata),
        "storage": storage_policy(metadata),
        "consumers": sorted(str(item) for item in consumers),
        "path": f"external/{metadata['id']}",
    }


def build_catalog(external_root: Path) -> dict[str, Any]:
    """Build a deterministic catalog from external source records."""

    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_dir in sorted(path for path in external_root.iterdir() if path.is_dir()):
        metadata_path = source_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = load_metadata(metadata_path)
        source_id = metadata.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"{metadata_path}: missing non-empty id")
        if source_id in seen:
            raise ValueError(f"{metadata_path}: duplicate external id {source_id}")
        seen.add(source_id)
        entries.append(catalog_entry(metadata))

    entries.sort(key=lambda item: item["id"])
    return {"schema_version": 1, "sources": entries}


def render_markdown(catalog: dict[str, Any]) -> str:
    """Render the human-readable catalog."""

    sources = catalog["sources"]
    lines = [
        "# External source catalog",
        "",
        "This file is generated from `external/*/metadata.yaml` records.",
        "Do not edit it by hand.",
        "",
    ]
    if not sources:
        lines.extend(["No external sources are registered yet.", ""])
        return "\n".join(lines)

    lines.extend([
        "| Source | Publisher | Storage | Redistribution | Licence / terms | Consumers |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in sources:
        license_data = item["license"]
        if license_data is None:
            license_text = "Unresolved"
        else:
            license_text = f"[{license_data['name']}]({license_data['url']})"
        consumers = ", ".join(item["consumers"]) if item["consumers"] else "—"
        lines.append(
            f"| [{item['title']}]({item['id']}/README.md) | "
            f"[{item['publisher']}]({item['source_url']}) | "
            f"{item['storage']} | {item['redistribution']} | "
            f"{license_text} | {consumers} |"
        )
    lines.append("")
    return "\n".join(lines)


def expected_outputs(root: Path) -> tuple[str, str]:
    """Return JSON and Markdown catalog text."""

    catalog = build_catalog(root / "external")
    json_text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    markdown_text = render_markdown(catalog)
    return json_text, markdown_text


def run(root: Path, *, write: bool) -> list[str]:
    """Write catalogs or return stale/missing-file errors."""

    json_text, markdown_text = expected_outputs(root)
    outputs = [
        (root / "external" / "catalog.json", json_text),
        (root / "external" / "CATALOG.md", markdown_text),
    ]
    if write:
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: generated catalog file is missing")
            continue
        if path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path}: catalog is stale; run with --write")
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
    parser.add_argument("--write", action="store_true", help="Regenerate catalogs.")
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
        print("External catalogs updated.")
    else:
        print("External catalogs are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
