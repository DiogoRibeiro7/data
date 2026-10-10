#!/usr/bin/env python3
"""Compare two immutable registry snapshot manifests deterministically."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

DIFF_SCHEMA_VERSION = 1


def load_manifest(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: manifest root must be an object")
    for key in ("manifest_version", "repository", "tag", "commit"):
        if key not in raw:
            raise ValueError(f"{path}: missing {key}")
    return raw


def _identity(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_version": manifest.get("manifest_version"),
        "repository": manifest.get("repository"),
        "tag": manifest.get("tag"),
        "commit": manifest.get("commit"),
    }


def _index(
    items: object,
    key: Callable[[dict[str, Any]], str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        result[key(item)] = item
    return dict(sorted(result.items()))


def _changed_keys(
    base: dict[str, dict[str, Any]],
    target: dict[str, dict[str, Any]],
) -> list[str]:
    return sorted(
        key for key in base.keys() & target.keys() if base[key] != target[key]
    )


def _simple_collection_diff(
    base_items: object,
    target_items: object,
    *,
    key: Callable[[dict[str, Any]], str],
) -> dict[str, Any]:
    base = _index(base_items, key)
    target = _index(target_items, key)
    return {
        "added": sorted(target.keys() - base.keys()),
        "removed": sorted(base.keys() - target.keys()),
        "changed": _changed_keys(base, target),
    }


def _canonical_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    base_items = _index(
        base.get("canonical_datasets"),
        lambda item: str(item.get("id")),
    )
    target_items = _index(
        target.get("canonical_datasets"),
        lambda item: str(item.get("id")),
    )
    changed: list[dict[str, Any]] = []
    for dataset_id in sorted(base_items.keys() & target_items.keys()):
        before = base_items[dataset_id]
        after = target_items[dataset_id]
        if before == after:
            continue
        before_files = _index(
            before.get("files"),
            lambda item: str(item.get("path")),
        )
        after_files = _index(
            after.get("files"),
            lambda item: str(item.get("path")),
        )
        changed_files = [
            path
            for path in sorted(before_files.keys() & after_files.keys())
            if before_files[path].get("sha256") != after_files[path].get("sha256")
        ]
        changed.append(
            {
                "id": dataset_id,
                "file_added": sorted(after_files.keys() - before_files.keys()),
                "file_removed": sorted(before_files.keys() - after_files.keys()),
                "file_checksum_changed": changed_files,
                "source_changed": before.get("source") != after.get("source"),
                "license_changed": before.get("license") != after.get("license"),
                "lifecycle_changed": before.get("lifecycle") != after.get("lifecycle"),
            }
        )
    return {
        "added": sorted(target_items.keys() - base_items.keys()),
        "removed": sorted(base_items.keys() - target_items.keys()),
        "changed": changed,
    }


def _consumer_key(item: dict[str, Any]) -> str:
    return "|".join(
        str(item.get(field, ""))
        for field in ("consumer_id", "dataset_id", "path")
    )


def _consumer_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("consumer_registry", {})
    after = target.get("consumer_registry", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    exact_available = isinstance(before.get("relationships"), list) and isinstance(
        after.get("relationships"), list
    )
    if exact_available:
        result = _simple_collection_diff(
            before.get("relationships"),
            after.get("relationships"),
            key=_consumer_key,
        )
    else:
        result = {"added": [], "removed": [], "changed": []}

    result["exact_relationship_diff_available"] = exact_available
    result["aggregate"] = {
        "relationship_count": [
            before.get("relationship_count"),
            after.get("relationship_count"),
        ],
        "active_relationship_count": [
            before.get("active_relationship_count"),
            after.get("active_relationship_count"),
        ],
        "deprecated_relationship_count": [
            before.get("deprecated_relationship_count"),
            after.get("deprecated_relationship_count"),
        ],
        "repository_count": [
            before.get("repository_count"),
            after.get("repository_count"),
        ],
    }
    return result


def _debt_key(item: dict[str, Any]) -> str:
    return f"{item.get('layer', '')}|{item.get('id', '')}"


def _debt_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("provenance_debt", {})
    after = target.get("provenance_debt", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    exact_available = isinstance(before.get("items"), list) and isinstance(
        after.get("items"), list
    )
    if exact_available:
        result = _simple_collection_diff(
            before.get("items"),
            after.get("items"),
            key=_debt_key,
        )
    else:
        result = {"added": [], "removed": [], "changed": []}

    result["exact_item_diff_available"] = exact_available
    result["aggregate"] = {
        "total_debt": [before.get("total_debt"), after.get("total_debt")],
        "actionable_count": [
            before.get("actionable_count"),
            after.get("actionable_count"),
        ],
        "terminal_count": [
            before.get("terminal_count"),
            after.get("terminal_count"),
        ],
        "by_blocker_category": [
            before.get("by_blocker_category"),
            after.get("by_blocker_category"),
        ],
    }
    return result


def _lifecycle_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("canonical_lifecycle", {})
    after = target.get("canonical_lifecycle", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    result = _simple_collection_diff(
        before.get("datasets"),
        after.get("datasets"),
        key=lambda item: str(item.get("id")),
    )
    result["preferred_replacements_changed"] = (
        before.get("preferred_replacements") != after.get("preferred_replacements")
    )
    result["preferred_replacements"] = [
        before.get("preferred_replacements", {}),
        after.get("preferred_replacements", {}),
    ]
    return result


def _schema_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("metadata_schemas")
    after = target.get("metadata_schemas")
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    layers = sorted(before.keys() | after.keys())
    changes: list[dict[str, Any]] = []
    for layer in layers:
        old = before.get(layer)
        new = after.get(layer)
        if old == new:
            continue
        changes.append(
            {
                "layer": layer,
                "before_version": (
                    old.get("schema_version") if isinstance(old, dict) else None
                ),
                "after_version": (
                    new.get("schema_version") if isinstance(new, dict) else None
                ),
                "digest_changed": old != new,
            }
        )
    return {"changed": changes}


def _client_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("registry_client")
    after = target.get("registry_client")
    return {
        "available_in_base": isinstance(before, dict),
        "available_in_target": isinstance(after, dict),
        "changed": before != after,
        "before": before,
        "after": after,
    }


def _distribution_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    before = base.get("static_distribution")
    after = target.get("static_distribution")
    if not isinstance(before, dict) or not isinstance(after, dict):
        return {
            "available_in_base": isinstance(before, dict),
            "available_in_target": isinstance(after, dict),
            "version_changed": before != after,
            "artifacts": {"added": [], "removed": [], "changed": []},
        }
    return {
        "available_in_base": True,
        "available_in_target": True,
        "version_changed": before.get("distribution_version")
        != after.get("distribution_version"),
        "artifacts": _simple_collection_diff(
            before.get("artifacts"),
            after.get("artifacts"),
            key=lambda item: str(item.get("name")),
        ),
    }


def build_diff(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    if base.get("repository") != target.get("repository"):
        raise ValueError("snapshot repositories do not match")

    result = {
        "schema_version": DIFF_SCHEMA_VERSION,
        "base": _identity(base),
        "target": _identity(target),
        "manifest_version_changed": base.get("manifest_version")
        != target.get("manifest_version"),
        "canonical": _canonical_diff(base, target),
        "consumers": _consumer_diff(base, target),
        "lifecycle": _lifecycle_diff(base, target),
        "provenance_debt": _debt_diff(base, target),
        "metadata_schemas": _schema_diff(base, target),
        "registry_client": _client_diff(base, target),
        "static_distribution": _distribution_diff(base, target),
    }
    result["empty"] = _semantic_empty(result)
    return result


def _semantic_empty(diff: dict[str, Any]) -> bool:
    if diff["manifest_version_changed"]:
        return False
    canonical = diff["canonical"]
    if canonical["added"] or canonical["removed"] or canonical["changed"]:
        return False
    for section in ("consumers", "provenance_debt"):
        value = diff[section]
        if value["added"] or value["removed"] or value["changed"]:
            return False
        for before, after in value["aggregate"].values():
            if before != after:
                return False
    lifecycle = diff["lifecycle"]
    if (
        lifecycle["added"]
        or lifecycle["removed"]
        or lifecycle["changed"]
        or lifecycle["preferred_replacements_changed"]
    ):
        return False
    if diff["metadata_schemas"]["changed"]:
        return False
    if diff["registry_client"]["changed"]:
        return False
    distribution = diff["static_distribution"]
    if (
        distribution["version_changed"]
        or distribution["artifacts"]["added"]
        or distribution["artifacts"]["removed"]
        or distribution["artifacts"]["changed"]
    ):
        return False
    return True


def render_markdown(diff: dict[str, Any]) -> str:
    lines = [
        f"# Registry snapshot diff: {diff['base']['tag']} → {diff['target']['tag']}",
        "",
        f"- Base commit: `{diff['base']['commit']}`",
        f"- Target commit: `{diff['target']['commit']}`",
        f"- Base / target manifest: **v{diff['base']['manifest_version']} / v{diff['target']['manifest_version']}**",
        f"- Semantic changes: **{'none' if diff['empty'] else 'present'}**",
        "",
    ]

    def add_ids(title: str, section: dict[str, Any]) -> None:
        lines.extend([f"## {title}", ""])
        for key in ("added", "removed"):
            values = section.get(key, [])
            lines.append(
                f"- {key.title()}: "
                + (", ".join(f"`{value}`" for value in values) if values else "None")
            )
        changed = section.get("changed", [])
        if changed and isinstance(changed[0], dict):
            ids = [str(item.get("id", item.get("layer", "changed"))) for item in changed]
            lines.append("- Changed: " + ", ".join(f"`{value}`" for value in ids))
        else:
            lines.append(
                "- Changed: "
                + (", ".join(f"`{value}`" for value in changed) if changed else "None")
            )
        lines.append("")

    add_ids("Canonical datasets", diff["canonical"])
    add_ids("Consumer relationships", diff["consumers"])
    lines.append(
        f"- Exact consumer relationship diff available: **{diff['consumers']['exact_relationship_diff_available']}**"
    )
    lines.append("")
    add_ids("Lifecycle", diff["lifecycle"])
    add_ids("Provenance and licensing debt", diff["provenance_debt"])
    lines.append(
        f"- Exact debt-item diff available: **{diff['provenance_debt']['exact_item_diff_available']}**"
    )
    lines.extend(["", "## Versions and contracts", ""])
    lines.append(
        f"- Manifest version changed: **{diff['manifest_version_changed']}**"
    )
    lines.append(
        f"- Metadata schema changes: **{len(diff['metadata_schemas']['changed'])}**"
    )
    lines.append(
        f"- Registry client changed: **{diff['registry_client']['changed']}**"
    )
    lines.append(
        f"- Static distribution version changed: **{diff['static_distribution']['version_changed']}**"
    )
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    base_path: Path,
    target_path: Path,
    *,
    json_output: Path,
    markdown_output: Path,
) -> None:
    diff = build_diff(load_manifest(base_path), load_manifest(target_path))
    json_output.write_text(
        json.dumps(diff, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_output.write_text(render_markdown(diff), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        write_outputs(
            args.base,
            args.target,
            json_output=args.json_output,
            markdown_output=args.markdown_output,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
