#!/usr/bin/env python3
"""Generate or verify the versioned machine-readable registry distribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

DISTRIBUTION_VERSION = 1
REPOSITORY = "DiogoRibeiro7/data"

SOURCE_ARTIFACTS = {
    "canonical": "datasets/catalog.json",
    "external": "external/catalog.json",
    "consumers": "consumers/catalog.json",
    "dependencies": "consumers/dependency-graph.json",
    "provenance-debt": "reports/provenance-debt.json",
    "lifecycle": "reports/lifecycle.json",
    "registry-quality": "reports/registry-quality.json",
}


def _json_safe(value: Any) -> Any:
    """Convert YAML-native values into JSON-compatible values."""

    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _json_text(value: Any) -> str:
    """Render deterministic JSON."""

    return json.dumps(
        _json_safe(value),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    ) + "\n"


def _sha256_text(text: str) -> str:
    """Return SHA-256 for UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return raw


def _legacy_catalog(root: Path) -> dict[str, Any]:
    """Build deterministic legacy registry records from committed metadata."""

    records: list[dict[str, Any]] = []
    legacy_root = root / "legacy"
    if not legacy_root.is_dir():
        return {"schema_version": 1, "records": records}

    for directory in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        metadata_path = directory / "metadata.yaml"
        if not metadata_path.is_file():
            continue
        raw = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{metadata_path}: metadata root must be an object")
        record_id = raw.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(f"{metadata_path}: missing non-empty id")
        records.append(
            {
                "id": record_id,
                "path": metadata_path.relative_to(root).as_posix(),
                "metadata": _json_safe(raw),
            }
        )

    records.sort(key=lambda item: item["id"])
    return {"schema_version": 1, "records": records}


def expected_outputs(root: Path) -> dict[str, str]:
    """Return every deterministic distribution file keyed by relative path."""

    root = root.resolve()
    outputs: dict[str, str] = {}

    for name, source_path in sorted(SOURCE_ARTIFACTS.items()):
        source = root / source_path
        text = source.read_text(encoding="utf-8")
        raw = json.loads(text)
        if not isinstance(raw, dict):
            raise ValueError(f"{source}: JSON root must be an object")
        outputs[f"{name}.json"] = text

    outputs["legacy.json"] = _json_text(_legacy_catalog(root))

    artifacts: list[dict[str, Any]] = []
    for filename, text in sorted(outputs.items()):
        raw = json.loads(text)
        schema_version = raw.get("schema_version") if isinstance(raw, dict) else None
        artifacts.append(
            {
                "name": filename.removesuffix(".json"),
                "path": filename,
                "schema_version": schema_version,
                "sha256": _sha256_text(text),
            }
        )

    index = {
        "distribution_version": DISTRIBUTION_VERSION,
        "repository": REPOSITORY,
        "artifacts": artifacts,
    }
    outputs["index.json"] = _json_text(index)
    return dict(sorted(outputs.items()))


def run(root: Path, *, write: bool) -> list[str]:
    """Write the distribution or return freshness errors."""

    outputs = expected_outputs(root)
    distribution = root / "distribution" / f"v{DISTRIBUTION_VERSION}"

    if write:
        distribution.mkdir(parents=True, exist_ok=True)
        expected_names = set(outputs)
        for existing in distribution.glob("*.json"):
            if existing.name not in expected_names:
                existing.unlink()
        for filename, text in outputs.items():
            (distribution / filename).write_text(text, encoding="utf-8")
        return []

    errors: list[str] = []
    for filename, expected in outputs.items():
        path = distribution / filename
        if not path.is_file():
            errors.append(f"{path}: static distribution artifact is missing")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(
                f"{path}: static distribution artifact is stale; run with --write"
            )
    return errors


def stage_for_docs(root: Path, docs_root: Path) -> None:
    """Copy the committed distribution into the MkDocs static tree."""

    source = root / "distribution" / f"v{DISTRIBUTION_VERSION}"
    destination = docs_root / "registry" / f"v{DISTRIBUTION_VERSION}"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

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
        help="Regenerate committed distribution artifacts.",
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
        print(f"Static registry distribution v{DISTRIBUTION_VERSION} updated.")
    else:
        print(f"Static registry distribution v{DISTRIBUTION_VERSION} is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
