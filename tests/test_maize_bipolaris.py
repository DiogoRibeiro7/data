"""Validate the canonical maize Bipolaris dataset package."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "maize-bipolaris-disease-progress"
RAW = DATASET / "raw" / "maize_bipolaris.csv"
METADATA = DATASET / "metadata.yaml"

EXPECTED_SHA256 = "eb013e32ca60f7a80e2be10c91b6cac5df68f863ce24597ebf48ebd07ec9e705"
EXPECTED_COLUMNS = ["Ambiente", "Hibrido", "DAE", "Fenologia", "Bipolaris"]


def _sha256(path: Path) -> str:
    """Return a file SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_maize_bipolaris_canonical_identity() -> None:
    """The committed canonical bytes and tabular shape remain fixed."""
    assert RAW.stat().st_size == 53_293
    assert _sha256(RAW) == EXPECTED_SHA256

    with RAW.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows[0] == EXPECTED_COLUMNS
    assert len(rows) - 1 == 1_105


def test_maize_bipolaris_metadata_and_license_notice() -> None:
    """Metadata records the pinned source and redistributable MIT snapshot."""
    metadata = yaml.safe_load(METADATA.read_text(encoding="utf-8"))

    assert metadata["id"] == "maize-bipolaris-disease-progress"
    assert metadata["license"]["name"] == "MIT"
    assert metadata["license"]["redistribution"] == "allowed"
    assert "d793d54c17ad404df2f6618d2681c993fcf144cf" in metadata["source"]["snapshot"]
    assert metadata["files"][0]["sha256"] == EXPECTED_SHA256

    notice = (DATASET / "LICENSE.upstream.txt").read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Emerson M. Del Ponte" in notice
    assert "Permission is hereby granted, free of charge" in notice


def test_external_record_was_replaced() -> None:
    """Canonical promotion removes the redundant external source record."""
    assert not (ROOT / "external" / "maize-bipolaris-disease-progress").exists()
