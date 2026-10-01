"""Tests for deterministic registry snapshot generation."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import create_snapshot as SNAPSHOT  # noqa: E402


class SnapshotFixture:
    """Build a minimal repository layout for snapshot tests."""

    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "datasets").mkdir()
        (self.root / "external").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / "legacy").mkdir()

        (self.root / "datasets" / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "datasets": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "external" / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "sources": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        schemas = {
            "canonical-metadata-v1.schema.json": 1,
            "external-metadata-v1.schema.json": 1,
            "legacy-metadata-v0.schema.json": 0,
        }
        for name, version in schemas.items():
            (self.root / "schemas" / name).write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "type": "object",
                        "properties": {"schema_version": {"const": version}},
                    },
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )

    def close(self) -> None:
        self.temp.cleanup()

    def add_canonical(self, slug: str, payload: bytes = b"a,b\n1,2\n") -> str:
        dataset = self.root / "datasets" / slug
        raw = dataset / "raw"
        raw.mkdir(parents=True)
        data_path = raw / "example.csv"
        data_path.write_bytes(payload)
        checksum = hashlib.sha256(payload).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": slug,
            "title": slug,
            "description": "fixture",
            "domain": ["testing"],
            "source": {
                "publisher": "Fixture",
                "url": "https://example.test/data",
                "retrieved_at": "2026-10-01",
                "snapshot": "v1",
            },
            "license": {
                "name": "CC0-1.0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "citation": None,
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
        return checksum


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SnapshotFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_valid_snapshot_tags(self) -> None:
        for tag in ("snapshot-2026.10.01", "snapshot-2026.10.01.2"):
            SNAPSHOT.validate_snapshot_tag(tag)

    def test_invalid_snapshot_tag_or_date_fails(self) -> None:
        for tag in ("v1.0.0", "snapshot-2026-10-01", "snapshot-2026.02.30", "snapshot-2026.10.01.0"):
            with self.subTest(tag=tag):
                with self.assertRaises(ValueError):
                    SNAPSHOT.validate_snapshot_tag(tag)

    def test_commit_must_be_full_lowercase_sha(self) -> None:
        for commit in ("main", "a" * 7, "A" * 40):
            with self.subTest(commit=commit):
                with self.assertRaises(ValueError):
                    SNAPSHOT.validate_commit(commit)

    def test_manifest_contains_catalog_and_schema_digests(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="a" * 40,
        )
        self.assertEqual(manifest["commit"], "a" * 40)
        self.assertEqual(manifest["catalogs"]["canonical"]["schema_version"], 1)
        self.assertEqual(manifest["metadata_schemas"]["legacy"]["schema_version"], 0)
        self.assertEqual(len(manifest["catalogs"]["external"]["sha256"]), 64)

    def test_canonical_file_checksums_are_recorded(self) -> None:
        checksum = self.fixture.add_canonical("dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="b" * 40,
        )
        item = manifest["canonical_datasets"][0]
        self.assertEqual(item["id"], "dataset")
        self.assertEqual(item["files"][0]["sha256"], checksum)

    def test_canonical_checksum_mismatch_fails(self) -> None:
        self.fixture.add_canonical("dataset")
        metadata_path = self.fixture.root / "datasets" / "dataset" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["files"][0]["sha256"] = "0" * 64
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            SNAPSHOT.build_manifest(
                self.fixture.root,
                tag="snapshot-2026.10.01",
                commit="c" * 40,
            )

    def test_release_material_is_byte_deterministic(self) -> None:
        self.fixture.add_canonical("dataset")
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_json, first_md = SNAPSHOT.write_release_material(
                self.fixture.root,
                tag="snapshot-2026.10.01.3",
                commit="d" * 40,
                output_dir=Path(first),
            )
            second_json, second_md = SNAPSHOT.write_release_material(
                self.fixture.root,
                tag="snapshot-2026.10.01.3",
                commit="d" * 40,
                output_dir=Path(second),
            )
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_md.read_bytes(), second_md.read_bytes())


if __name__ == "__main__":
    unittest.main()
