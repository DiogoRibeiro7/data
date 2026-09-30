"""Tests for repository data validation."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_repository as VALIDATOR  # noqa: E402


class RepositoryFixture:
    """Build a small temporary repository for validation tests."""

    def __init__(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        (self.root / "datasets").mkdir()
        (self.root / "datasets" / "README.md").write_text("# Datasets\n", encoding="utf-8")

    def close(self) -> None:
        """Release the temporary repository."""

        self._temp.cleanup()

    def write_catalogs(self) -> None:
        """Generate the expected catalog files."""

        problems = VALIDATOR.validate_repository(self.root, write_catalog=True)
        errors = [problem for problem in problems if problem.severity == "error"]
        if errors:
            raise AssertionError(errors)

    def add_legacy(self, slug: str, data: bytes = b"a,b\n1,2\n") -> Path:
        """Add one valid legacy quarantine package."""

        group = self.root / "legacy" / slug
        raw = group / "raw"
        raw.mkdir(parents=True)
        file_path = raw / "example.csv"
        file_path.write_bytes(data)
        (group / "README.md").write_text(f"# {slug}\n", encoding="utf-8")

        header = f"blob {len(data)}\0".encode("ascii")
        git_sha = hashlib.sha1(header + data, usedforsecurity=False).hexdigest()
        metadata: dict[str, Any] = {
            "schema_version": 0,
            "status": "legacy-quarantine",
            "id": slug,
            "source": {"publisher": "unknown", "url": None},
            "license": {"name": "unknown", "redistribution": "unknown"},
            "files": [{
                "path": "raw/example.csv",
                "original_path": "example.csv",
                "size_bytes": len(data),
                "git_blob_sha": git_sha,
            }],
        }
        (group / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return file_path

    def add_canonical(
        self,
        slug: str,
        data: bytes = b"a,b\n1,2\n",
        *,
        sha256: str | None = None,
        redistribution: str = "allowed",
    ) -> Path:
        """Add one canonical dataset with valid metadata."""

        dataset = self.root / "datasets" / slug
        raw = dataset / "raw"
        raw.mkdir(parents=True)
        file_path = raw / "example.csv"
        file_path.write_bytes(data)
        (dataset / "README.md").write_text(f"# {slug}\n", encoding="utf-8")

        checksum = sha256 or hashlib.sha256(data).hexdigest()
        metadata: dict[str, Any] = {
            "schema_version": 1,
            "id": slug,
            "title": f"Dataset {slug}",
            "description": "Fixture dataset used by validator tests.",
            "domain": ["testing"],
            "source": {
                "publisher": "Fixture publisher",
                "url": "https://example.test/dataset",
                "retrieved_at": "2026-09-30",
                "snapshot": "v1",
            },
            "license": {
                "name": "CC0-1.0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": redistribution,
            },
            "citation": {
                "text": "Fixture dataset",
                "url": "https://example.test/citation",
            },
            "files": [{
                "path": "raw/example.csv",
                "role": "raw",
                "format": "csv",
                "sha256": checksum,
            }],
            "lineage": [],
        }
        (dataset / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return file_path


class ValidatorTests(unittest.TestCase):
    """Exercise core repository invariants."""

    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def errors(self) -> list[str]:
        """Return error messages from validation."""

        return [
            problem.message
            for problem in VALIDATOR.validate_repository(self.fixture.root)
            if problem.severity == "error"
        ]

    def test_empty_registry_with_generated_catalogs_is_valid(self) -> None:
        self.fixture.write_catalogs()
        self.assertEqual(self.errors(), [])

    def test_valid_canonical_dataset_is_catalogued(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.write_catalogs()
        self.assertEqual(self.errors(), [])
        catalog = json.loads(
            (self.fixture.root / "datasets" / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(catalog["datasets"][0]["id"], "example-dataset")

    def test_checksum_mismatch_fails(self) -> None:
        self.fixture.add_canonical("bad-checksum", sha256="0" * 64)
        self.assertTrue(any("sha256 does not match file" in msg for msg in self.errors()))

    def test_restricted_redistribution_fails_for_stored_canonical_data(self) -> None:
        self.fixture.add_canonical("restricted-data", redistribution="restricted")
        self.assertTrue(any("requires redistribution=allowed" in msg for msg in self.errors()))

    def test_exact_duplicate_bytes_fail(self) -> None:
        payload = b"same bytes\n"
        self.fixture.add_legacy("legacy-copy", payload)
        self.fixture.add_canonical("canonical-copy", payload)
        self.assertTrue(any("duplicate SHA-256" in msg for msg in self.errors()))

    def test_legacy_git_blob_integrity_is_checked(self) -> None:
        path = self.fixture.add_legacy("legacy-data")
        self.fixture.write_catalogs()
        path.write_bytes(b"changed\n")
        self.assertTrue(any("git_blob_sha does not match file" in msg for msg in self.errors()))

    def test_stale_catalog_fails(self) -> None:
        self.fixture.write_catalogs()
        self.fixture.add_canonical("new-dataset")
        self.assertTrue(any("catalog is stale" in msg for msg in self.errors()))

    def test_broken_dataset_link_fails(self) -> None:
        self.fixture.write_catalogs()
        (self.fixture.root / "datasets" / "README.md").write_text(
            "[missing](missing.md)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("broken relative link" in msg for msg in self.errors()))


if __name__ == "__main__":
    unittest.main()
