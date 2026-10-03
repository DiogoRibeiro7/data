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
            "title": f"Legacy {slug}",
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

    def add_external(
        self,
        slug: str,
        *,
        schema_version: int = 1,
        publisher: object = "Fixture publisher",
        extra: dict[str, Any] | None = None,
    ) -> Path:
        """Add one external source record."""

        source = self.root / "external" / slug
        source.mkdir(parents=True)
        (source / "README.md").write_text(f"# {slug}\n", encoding="utf-8")
        metadata: dict[str, Any] = {
            "schema_version": schema_version,
            "status": "external-reference",
            "id": slug,
            "title": f"External {slug}",
            "publisher": publisher,
            "source_url": "https://example.test/source",
            "storage": "authoritative-upstream",
        }
        if extra:
            metadata.update(extra)
        metadata_path = source / "metadata.yaml"
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return metadata_path

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

    def add_consumer(
        self,
        consumer_id: str,
        dataset_id: str,
        *,
        record_dataset_id: str | None = None,
        filename: str | None = None,
        path: str | None = None,
        sha256: str | None = None,
        registry_commit: str = "a" * 40,
        consumer_id_value: str | None = None,
        status: str = "active",
    ) -> Path:
        """Add one canonical consumer relationship record."""

        dataset_metadata_path = self.root / "datasets" / dataset_id / "metadata.yaml"
        dataset_metadata = yaml.safe_load(dataset_metadata_path.read_text(encoding="utf-8"))
        canonical_file = dataset_metadata["files"][0]
        resolved_dataset_id = record_dataset_id or dataset_id

        consumer_dir = self.root / "consumers" / consumer_id
        consumer_dir.mkdir(parents=True, exist_ok=True)
        record_path = consumer_dir / (filename or f"{resolved_dataset_id}.yaml")

        metadata: dict[str, Any] = {
            "schema_version": 1,
            "status": status,
            "consumer_id": consumer_id_value or consumer_id,
            "consumer_repository": f"DiogoRibeiro7/{consumer_id}",
            "dataset_id": resolved_dataset_id,
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": registry_commit,
            "path": path or f"datasets/{dataset_id}/{canonical_file['path']}",
            "sha256": sha256 or canonical_file["sha256"],
            "consumer_commit": "b" * 40,
        }
        record_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return record_path


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

    def test_canonical_schema_rejects_wrong_field_type(self) -> None:
        self.fixture.add_canonical("bad-domain")
        metadata_path = self.fixture.root / "datasets" / "bad-domain" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["domain"] = "testing"
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("schema violation" in msg and "domain" in msg for msg in self.errors()))

    def test_canonical_schema_rejects_unknown_root_field(self) -> None:
        self.fixture.add_canonical("extra-field")
        metadata_path = self.fixture.root / "datasets" / "extra-field" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["unexpected"] = "not allowed"
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("Additional properties are not allowed" in msg for msg in self.errors()))

    def test_external_schema_is_validated(self) -> None:
        self.fixture.add_external("example-source", publisher=123)
        self.assertTrue(any("schema violation" in msg and "publisher" in msg for msg in self.errors()))

    def test_external_schema_version_mismatch_fails(self) -> None:
        self.fixture.add_external("old-source", schema_version=2)
        errors = self.errors()
        self.assertTrue(any("schema violation" in msg and "schema_version" in msg for msg in errors))
        self.assertTrue(any("external schema_version must be 1" in msg for msg in errors))

    def test_legacy_schema_rejects_malformed_file_metadata(self) -> None:
        self.fixture.add_legacy("bad-legacy")
        metadata_path = self.fixture.root / "legacy" / "bad-legacy" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["files"][0]["size_bytes"] = "not-an-integer"
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("schema violation" in msg and "size_bytes" in msg for msg in self.errors()))

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
        self.assertTrue(any("git_blob_sha does not match stored Git blob" in msg for msg in self.errors()))

    def test_stale_catalog_fails(self) -> None:
        self.fixture.write_catalogs()
        self.fixture.add_canonical("new-dataset")
        self.assertTrue(any("catalog is stale" in msg for msg in self.errors()))

    def test_valid_consumer_relationship_is_accepted(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer("example-consumer", "example-dataset")
        self.fixture.write_catalogs()
        self.assertEqual(self.errors(), [])

    def test_consumer_schema_rejects_floating_registry_ref(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            registry_commit="main",
        )
        self.assertTrue(
            any(
                "schema violation" in msg and "registry_commit" in msg
                for msg in self.errors()
            )
        )

    def test_consumer_missing_canonical_dataset_fails(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            record_dataset_id="missing-dataset",
        )
        self.assertTrue(
            any(
                "canonical dataset 'missing-dataset' does not exist" in msg
                for msg in self.errors()
            )
        )

    def test_consumer_path_must_match_dataset(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            path="datasets/other-dataset/raw/example.csv",
        )
        self.assertTrue(
            any("path must belong to canonical dataset" in msg for msg in self.errors())
        )

    def test_consumer_checksum_must_match_canonical_metadata(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            sha256="0" * 64,
        )
        self.assertTrue(
            any(
                "sha256 does not match canonical dataset metadata" in msg
                for msg in self.errors()
            )
        )

    def test_consumer_identity_must_match_directory_and_filename(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            consumer_id_value="other-consumer",
            filename="wrong-name.yaml",
        )
        errors = self.errors()
        self.assertTrue(any("consumer_id must match directory" in msg for msg in errors))
        self.assertTrue(any("filename must be 'example-dataset.yaml'" in msg for msg in errors))

    def test_duplicate_consumer_dataset_relationship_fails(self) -> None:
        self.fixture.add_canonical("example-dataset")
        first = self.fixture.add_consumer("example-consumer", "example-dataset")
        duplicate = first.parent / "duplicate.yaml"
        duplicate.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")

        self.assertTrue(
            any("duplicate consumer/dataset relationship" in msg for msg in self.errors())
        )

    def test_consumer_record_at_root_is_rejected(self) -> None:
        consumers = self.fixture.root / "consumers"
        consumers.mkdir(parents=True)
        (consumers / "bad.yaml").write_text("schema_version: 1\n", encoding="utf-8")

        self.assertTrue(
            any("consumer records must live under" in msg for msg in self.errors())
        )

    def test_consumer_yml_extension_is_rejected(self) -> None:
        self.fixture.add_canonical("example-dataset")
        path = self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            filename="example-dataset.yml",
        )

        self.assertTrue(path.exists())
        self.assertTrue(
            any("consumer records must use the .yaml extension" in msg for msg in self.errors())
        )

    def test_deprecated_consumer_may_reference_missing_dataset(self) -> None:
        self.fixture.add_canonical("example-dataset")
        self.fixture.add_consumer(
            "example-consumer",
            "example-dataset",
            record_dataset_id="old-dataset",
            status="deprecated",
        )
        self.fixture.write_catalogs()
        self.assertEqual(self.errors(), [])

    def test_consumer_template_matches_schema(self) -> None:
        template_dir = self.fixture.root / "templates"
        template_dir.mkdir()
        source = Path(__file__).resolve().parents[1] / "templates" / "consumer-dataset.yaml"
        (template_dir / "consumer-dataset.yaml").write_text(
            source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.fixture.write_catalogs()
        self.assertEqual(self.errors(), [])


    def test_broken_dataset_link_fails(self) -> None:
        self.fixture.write_catalogs()
        (self.fixture.root / "datasets" / "README.md").write_text(
            "[missing](missing.md)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("broken relative link" in msg for msg in self.errors()))


if __name__ == "__main__":
    unittest.main()
