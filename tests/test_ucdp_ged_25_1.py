"""Integrity tests for canonical UCDP GED 25.1."""

from __future__ import annotations

import csv
import hashlib
import io
import unittest
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "ucdp-ged-25-1"
ARCHIVE = DATASET / "raw" / "ged251-csv.zip"
METADATA = DATASET / "metadata.yaml"

EXPECTED_ARCHIVE_SHA256 = "e256f1fb20a579d8b2f910e5bae212f486d3002adaa2e4359ace740c737da05d"
EXPECTED_MEMBER = "GEDEvent_v25_1.csv"
EXPECTED_MEMBER_SIZE = 250_393_383
EXPECTED_COLUMNS = 49


def _sha256(path: Path) -> str:
    """Return SHA-256 for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class UcdpGed251Tests(unittest.TestCase):
    """Validate exact archive identity and ZIP structure."""

    def test_archive_identity(self) -> None:
        """Canonical archive is the exact reviewed upstream object."""
        self.assertEqual(ARCHIVE.stat().st_size, 29_307_888)
        self.assertEqual(_sha256(ARCHIVE), EXPECTED_ARCHIVE_SHA256)

    def test_archive_contains_expected_csv(self) -> None:
        """Archive contains one GED CSV with the expected header and size."""
        with zipfile.ZipFile(ARCHIVE) as archive:
            csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            self.assertEqual(csv_members, [EXPECTED_MEMBER])

            info = archive.getinfo(EXPECTED_MEMBER)
            self.assertEqual(info.file_size, EXPECTED_MEMBER_SIZE)

            with archive.open(EXPECTED_MEMBER) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                reader = csv.reader(text)
                header = next(reader)

        self.assertEqual(len(header), EXPECTED_COLUMNS)
        self.assertEqual(header[0], "id")
        self.assertEqual(header[-1], "gwnob")

    def test_metadata_records_redistribution_and_checksums(self) -> None:
        """Canonical metadata records licence and both archive identities."""
        metadata = yaml.safe_load(METADATA.read_text(encoding="utf-8"))

        self.assertEqual(metadata["id"], "ucdp-ged-25-1")
        self.assertEqual(metadata["license"]["name"], "CC BY 4.0")
        self.assertEqual(metadata["license"]["redistribution"], "allowed")
        self.assertEqual(metadata["files"][0]["sha256"], EXPECTED_ARCHIVE_SHA256)
        self.assertIn(
            "3f286de84cc0cb9152403f53e6aea2ac604d623f156e61079338596e09e8b550",
            metadata["files"][0]["notes"],
        )


if __name__ == "__main__":
    unittest.main()
