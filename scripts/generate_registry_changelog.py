#!/usr/bin/env python3
"""Generate or verify the append-only machine-readable registry changelog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY = "DiogoRibeiro7/data"
SCHEMA_VERSION = 1
ENTRIES_DIR = "changelog/entries"
OUTPUT_JSON = "reports/registry-changelog.json"
OUTPUT_MD = "reports/registry-changelog.md"


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return raw


def _json_text(value: Any) -> str:
    return json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    ) + "\n"


def _load_entries(root: Path) -> list[dict[str, Any]]:
    entries_root = root / ENTRIES_DIR
    entries: list[dict[str, Any]] = []
    if not entries_root.is_dir():
        return entries

    for path in sorted(entries_root.glob("*.json")):
        entry = _load_json(path)
        if entry.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"{path}: schema_version must be {SCHEMA_VERSION}")
        transition_id = entry.get("transition_id")
        if not isinstance(transition_id, str) or not transition_id:
            raise ValueError(f"{path}: transition_id must be non-empty text")
        entries.append(entry)

    transition_ids = [str(item["transition_id"]) for item in entries]
    if transition_ids != sorted(transition_ids):
        raise ValueError("changelog transitions must be sorted deterministically")
    if len(transition_ids) != len(set(transition_ids)):
        raise ValueError("changelog transition_id values must be unique")

    for previous, current in zip(entries, entries[1:]):
        previous_target = previous.get("target")
        current_base = current.get("base")
        if not isinstance(previous_target, dict) or not isinstance(current_base, dict):
            raise ValueError("changelog entries require base/target identity objects")
        if previous_target.get("tag") != current_base.get("tag"):
            raise ValueError(
                "changelog transitions must form one contiguous append-only history"
            )
        if previous_target.get("commit") != current_base.get("commit"):
            raise ValueError(
                "changelog transitions must preserve exact commit continuity"
            )

    return entries


def build_changelog(root: Path) -> dict[str, Any]:
    entries = _load_entries(root)
    if not entries:
        raise ValueError("at least one changelog transition entry is required")

    first_base = entries[0].get("base")
    if not isinstance(first_base, dict):
        raise ValueError("first changelog entry must contain a base identity")

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": REPOSITORY,
        "history_start": {
            "tag": first_base.get("tag"),
            "commit": first_base.get("commit"),
        },
        "source_authority": (
            "Committed append-only transition entries derived from immutable "
            "snapshot release manifests; Git releases remain authoritative."
        ),
        "entries": entries,
    }


def render_markdown(changelog: dict[str, Any]) -> str:
    entries = changelog["entries"]
    lines = [
        "# Registry release changelog",
        "",
        "This changelog is generated from committed append-only transition entries.",
        "Git snapshot tags/releases remain the authoritative release identities.",
        "",
        f"- Repository: `{changelog['repository']}`",
        f"- History starts at: `{changelog['history_start']['tag']}`",
        f"- Transition count: **{len(entries)}**",
        "",
    ]

    for entry in entries:
        base = entry["base"]
        target = entry["target"]
        changes = entry["changes"]
        exactness = entry["exactness"]
        lines.extend(
            [
                f"## {base['tag']} → {target['tag']}",
                "",
                f"- Base commit: `{base['commit']}`",
                f"- Target commit: `{target['commit']}`",
                f"- Manifest: **v{base['manifest_version']} → v{target['manifest_version']}**",
                f"- Canonical added / removed / changed: "
                f"**{len(changes['canonical']['added'])} / "
                f"{len(changes['canonical']['removed'])} / "
                f"{len(changes['canonical']['changed'])}**",
                f"- Consumer relationship count: "
                f"**{changes['consumers']['relationship_count'][0]} → "
                f"{changes['consumers']['relationship_count'][1]}**",
                f"- Provenance debt: "
                f"**{changes['provenance_debt']['total_debt'][0]} → "
                f"{changes['provenance_debt']['total_debt'][1]}**",
                f"- Exact consumer diff available: **{exactness['consumers']}**",
                f"- Exact provenance-debt item diff available: **{exactness['provenance_debt']}**",
                "",
            ]
        )

    return "\n".join(lines)


def expected_outputs(root: Path) -> tuple[str, str]:
    changelog = build_changelog(root.resolve())
    return _json_text(changelog), render_markdown(changelog)


def run(root: Path, *, write: bool) -> list[str]:
    json_text, markdown_text = expected_outputs(root)
    outputs = [
        (root / OUTPUT_JSON, json_text),
        (root / OUTPUT_MD, markdown_text),
    ]

    if write:
        (root / "reports").mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: registry changelog is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(
                f"{path}: registry changelog is stale; run with --write"
            )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = run(args.root.resolve(), write=args.write)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Registry changelog updated."
        if args.write
        else "Registry changelog is current."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
