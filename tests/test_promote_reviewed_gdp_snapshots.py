"""Offline integrity tests for the reviewed-snapshot staging helper."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.promote_reviewed_gdp_snapshots import sha, verify_candidate


class TestReviewedSnapshots(unittest.TestCase):
    def fixture(self, directory: Path) -> dict:
        """Build an invented manifest; never contact the upstream API."""
        data = b"[]"
        (directory / "test.json").write_bytes(data)
        manifest = {
            "source_id": "2", "start": 1995, "end": 2025,
            "countries": [str(i) for i in range(33)],
            "files": [{"path": "test.json", "bytes": len(data), "sha256": sha(data)}],
            "status": "candidate_only",
        }
        raw = json.dumps(manifest).encode()
        (directory / "manifest.json").write_bytes(raw)
        return {"manifest": sha(raw), "source_id": "2",
                "start": 1995, "end": 2025, "file_count": 1}

    def test_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            spec = self.fixture(directory)
            _, _, records = verify_candidate(directory, spec)
            self.assertEqual(records[0][1], b"[]")

    def test_tampered_data(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            spec = self.fixture(directory)
            (directory / "test.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "does not match"):
                verify_candidate(directory, spec)

    def test_changed_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            spec = self.fixture(directory)
            (directory / "manifest.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                verify_candidate(directory, spec)

    def test_extra_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            spec = self.fixture(directory)
            (directory / "unexpected.json").write_text("[]")
            with self.assertRaisesRegex(ValueError, "Unexpected candidate"):
                verify_candidate(directory, spec)
