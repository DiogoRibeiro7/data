#!/usr/bin/env python3
"""Generate or verify deterministic archival preservation eligibility."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

POLICY_PATH = "preservation/policy-v1.json"
REPORT_JSON = "reports/preservation-eligibility.json"
REPORT_MD = "reports/preservation-eligibility.md"


def _json_safe(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _json_text(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    ) + "\n"


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return raw


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return raw


def _canonical_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for directory in sorted(
        path for path in (root / "datasets").iterdir() if path.is_dir()
    ):
        metadata_path = directory / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = _load_yaml(metadata_path)
        license_data = metadata.get("license")
        source = metadata.get("source")
        if not isinstance(license_data, dict):
            raise ValueError(f"{metadata_path}: license must be a mapping")
        if not isinstance(source, dict):
            raise ValueError(f"{metadata_path}: source must be a mapping")

        redistribution = license_data.get("redistribution")
        eligible = redistribution == "allowed"
        files = metadata.get("files")
        if not isinstance(files, list):
            raise ValueError(f"{metadata_path}: files must be a list")

        records.append(
            {
                "id": metadata.get("id"),
                "title": metadata.get("title"),
                "metadata_path": metadata_path.relative_to(root).as_posix(),
                "byte_archive_eligibility": (
                    "eligible" if eligible else "metadata-only"
                ),
                "reason": (
                    "canonical metadata explicitly permits redistribution"
                    if eligible
                    else "canonical bytes are not archive-eligible without explicit redistribution permission"
                ),
                "redistribution": redistribution,
                "license": {
                    "name": license_data.get("name"),
                    "url": license_data.get("url"),
                },
                "source": {
                    "publisher": source.get("publisher"),
                    "url": source.get("url"),
                    "snapshot": source.get("snapshot"),
                },
                "files": sorted(
                    [
                        {
                            "path": item.get("path"),
                            "sha256": item.get("sha256"),
                        }
                        for item in files
                        if isinstance(item, dict)
                    ],
                    key=lambda item: str(item["path"]),
                ),
            }
        )
    records.sort(key=lambda item: str(item["id"]))
    return records


def _external_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    external_root = root / "external"
    for directory in sorted(path for path in external_root.iterdir() if path.is_dir()):
        metadata_path = directory / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = _load_yaml(metadata_path)
        records.append(
            {
                "id": metadata.get("id"),
                "title": metadata.get("title"),
                "metadata_path": metadata_path.relative_to(root).as_posix(),
                "byte_archive_eligibility": "metadata-only",
                "reason": "external-layer source bytes are never archived by default",
                "redistribution": metadata.get("redistribution"),
            }
        )
    records.sort(key=lambda item: str(item["id"]))
    return records


def _legacy_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    legacy_root = root / "legacy"
    for directory in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        metadata_path = directory / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        metadata = _load_yaml(metadata_path)
        license_data = metadata.get("license")
        redistribution = (
            license_data.get("redistribution")
            if isinstance(license_data, dict)
            else None
        )
        records.append(
            {
                "id": metadata.get("id"),
                "title": metadata.get("title"),
                "metadata_path": metadata_path.relative_to(root).as_posix(),
                "byte_archive_eligibility": "metadata-only",
                "reason": "legacy quarantine bytes require separate canonical promotion before archival",
                "redistribution": redistribution,
            }
        )
    records.sort(key=lambda item: str(item["id"]))
    return records


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    policy = _load_json(root / POLICY_PATH)
    canonical = _canonical_records(root)
    external = _external_records(root)
    legacy = _legacy_records(root)

    canonical_eligible = sum(
        item["byte_archive_eligibility"] == "eligible" for item in canonical
    )

    return {
        "schema_version": 1,
        "policy": {
            "path": POLICY_PATH,
            "schema_version": policy.get("schema_version"),
            "policy_version": policy.get("policy_version"),
        },
        "archive_profiles": policy.get("archive_profiles"),
        "release_metadata_eligibility": "eligible",
        "static_distribution_eligibility": "eligible",
        "summary": {
            "canonical_dataset_count": len(canonical),
            "canonical_byte_archive_eligible_count": canonical_eligible,
            "canonical_metadata_only_count": len(canonical) - canonical_eligible,
            "external_source_count": len(external),
            "external_metadata_only_count": len(external),
            "legacy_package_count": len(legacy),
            "legacy_metadata_only_count": len(legacy),
        },
        "canonical": canonical,
        "external": external,
        "legacy": legacy,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Archival preservation eligibility",
        "",
        "This report is generated deterministically from committed registry metadata",
        "and the versioned preservation policy. It does not grant rights beyond",
        "the recorded upstream licence/terms.",
        "",
        f"- Preservation policy: `{report['policy']['path']}` (v{report['policy']['policy_version']})",
        f"- Release metadata: **{report['release_metadata_eligibility']}**",
        f"- Static distribution: **{report['static_distribution_eligibility']}**",
        f"- Canonical datasets: **{summary['canonical_dataset_count']}**",
        f"- Canonical byte-archive eligible: **{summary['canonical_byte_archive_eligible_count']}**",
        f"- Canonical metadata-only: **{summary['canonical_metadata_only_count']}**",
        f"- External sources (metadata-only): **{summary['external_metadata_only_count']}**",
        f"- Legacy packages (metadata-only): **{summary['legacy_metadata_only_count']}**",
        "",
        "## Canonical dataset bytes",
        "",
        "| Dataset | Eligibility | Redistribution | Licence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["canonical"]:
        licence = item["license"]["name"] or "unknown"
        lines.append(
            f"| `{item['id']}` | {item['byte_archive_eligibility']} | "
            f"{item['redistribution'] or 'unknown'} | {licence} |"
        )

    lines.extend(
        [
            "",
            "## External sources",
            "",
            "External records are archive-eligible as metadata only. Their upstream",
            "bytes are not copied into an archive unless they are separately promoted",
            "to the canonical layer under explicit redistribution permission.",
            "",
            "## Legacy quarantine",
            "",
            "Legacy records are archive-eligible as metadata only. Quarantined bytes",
            "are not included in preservation bundles unless a later canonical",
            "promotion establishes exact identity and redistribution permission.",
            "",
            "## Corrections and identifiers",
            "",
            "- Git snapshot tag + exact commit remain the primary technical identity.",
            "- DOI/archive identifiers are additive citation identifiers.",
            "- Published snapshot tags and archive records are not rewritten in place.",
            "- Corrections create a new record that links/supersedes the earlier one.",
            "- A mixed archive bundle never overrides per-dataset upstream terms.",
            "",
        ]
    )
    return "\n".join(lines)


def expected_outputs(root: Path) -> tuple[str, str]:
    report = build_report(root)
    return _json_text(report), render_markdown(report)


def run(root: Path, *, write: bool) -> list[str]:
    json_text, markdown_text = expected_outputs(root)
    outputs = [
        (root / REPORT_JSON, json_text),
        (root / REPORT_MD, markdown_text),
    ]
    if write:
        (root / "reports").mkdir(parents=True, exist_ok=True)
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
        return []

    errors: list[str] = []
    for path, expected in outputs:
        if not path.is_file():
            errors.append(f"{path}: preservation eligibility report is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(
                f"{path}: preservation eligibility report is stale; run with --write"
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
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Preservation eligibility report updated."
        if args.write
        else "Preservation eligibility report is current."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
