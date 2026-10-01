#!/usr/bin/env python3
"""Prepare generated catalog pages for MkDocs without duplicating source-of-truth files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GENERATED = DOCS / "generated"
GITHUB_BLOB = "https://github.com/DiogoRibeiro7/data/blob/main"

def write_catalog(source: Path, destination: Path, source_prefix: str) -> None:
    """Copy a generated catalog and rewrite repository-relative links."""

    text = source.read_text(encoding="utf-8")
    pattern = re.compile(r"\]\((?!https?://)([^)#]+)(#[^)]+)?\)")

    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        fragment = match.group(2) or ""
        return f"]({GITHUB_BLOB}/{source_prefix}/{target}{fragment})"

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(pattern.sub(replace, text), encoding="utf-8")

def copy_text(source: Path, destination: Path) -> None:
    """Copy a text source into the documentation tree."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def copy_root_markdown(source: Path, destination: Path) -> None:
    """Stage root Markdown and rewrite repository-relative links."""

    text = source.read_text(encoding="utf-8")
    replacements = {
        "](templates/metadata.yaml)": (
            f"]({GITHUB_BLOB}/templates/metadata.yaml)"
        ),
        "](docs/DATA_POLICY.md)": (
            f"]({GITHUB_BLOB}/docs/DATA_POLICY.md)"
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")

def main() -> int:
    write_catalog(
        ROOT / "datasets" / "CATALOG.md",
        GENERATED / "canonical-catalog.md",
        "datasets",
    )
    write_catalog(
        ROOT / "external" / "CATALOG.md",
        GENERATED / "external-catalog.md",
        "external",
    )
    legacy_text = (ROOT / "legacy" / "INVENTORY.md").read_text(encoding="utf-8")
    legacy_text = legacy_text.replace(
        "](../docs/migrations/LEGACY_RESOLUTION.md)",
        "](../migrations/LEGACY_RESOLUTION.md)",
    )
    (GENERATED / "legacy-inventory.md").write_text(legacy_text, encoding="utf-8")
    copy_root_markdown(ROOT / "CONTRIBUTING.md", DOCS / "CONTRIBUTING.md")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
