#!/usr/bin/env python3
"""Prepare generated catalog pages for MkDocs without duplicating source-of-truth files."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GENERATED = DOCS / "generated"

def copy_text(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def main() -> int:
    copy_text(ROOT / "datasets" / "CATALOG.md", GENERATED / "canonical-catalog.md")
    copy_text(ROOT / "external" / "CATALOG.md", GENERATED / "external-catalog.md")
    copy_text(ROOT / "legacy" / "INVENTORY.md", GENERATED / "legacy-inventory.md")
    copy_text(ROOT / "CONTRIBUTING.md", DOCS / "CONTRIBUTING.md")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
