"""Tests for deterministic archive metadata and preservation bundles."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.generate_archive_bundle import build_archive_metadata, build_bundle

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "schemas" / "archive-metadata-v1.schema.json").read_text(
        encoding="utf-8"
    )
)
TAG = "snapshot-2026.10.10"
COMMIT = "a" * 40


class ArchiveBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "repo"
        self.release_dir = Path(self.tempdir.name) / "release"
        self.output_dir = Path(self.tempdir.name) / "archive"
        self.release_dir.mkdir(parents=True)

        (self.root / "preservation").mkdir(parents=True)
        (self.root / "reports").mkdir(parents=True)
        (self.root / "archive").mkdir(parents=True)
        (self.root / "distribution" / "v1").mkdir(parents=True)
        (self.root / "datasets" / "eligible" / "raw").mkdir(parents=True)
        (self.root / "datasets" / "metadata-only" / "raw").mkdir(parents=True)

        (self.root / "CITATION.cff").write_text(
            """cff-version: 1.2.0
title: Data Registry
abstract: Deterministic registry archive fixture.
license: MIT
authors:
  - family-names: Ribeiro
    given-names: Diogo
keywords:
  - reproducibility
  - data registry
""",
            encoding="utf-8",
        )
        (self.root / "preservation" / "policy-v1.json").write_text(
            json.dumps(
                {
                    "policy_version": 1,
                    "archive_profiles": {
                        "release-metadata": {"canonical_dataset_bytes": False},
                        "eligible-canonical-bytes": {
                            "canonical_dataset_bytes": True
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        (self.root / "reports" / "preservation-eligibility.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "summary": {"canonical_byte_archive_eligible_count": 1},
                    "canonical": [
                        {
                            "id": "eligible",
                            "byte_archive_eligibility": "eligible",
                        },
                        {
                            "id": "metadata-only",
                            "byte_archive_eligibility": "metadata-only",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.root / "archive" / "identifiers.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "entries": [],
                }
            ),
            encoding="utf-8",
        )
        (self.root / "distribution" / "v1" / "index.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        (self.root / "datasets" / "eligible" / "metadata.yaml").write_text(
            "id: eligible\n",
            encoding="utf-8",
        )
        (self.root / "datasets" / "eligible" / "raw" / "data.csv").write_text(
            "x\n1\n",
            encoding="utf-8",
        )
        (
            self.root / "datasets" / "metadata-only" / "metadata.yaml"
        ).write_text("id: metadata-only\n", encoding="utf-8")
        (
            self.root / "datasets" / "metadata-only" / "raw" / "secret.csv"
        ).write_text("x\n2\n", encoding="utf-8")

        (self.release_dir / "snapshot-manifest.json").write_text(
            json.dumps(
                {
                    "repository": "DiogoRibeiro7/data",
                    "tag": TAG,
                    "commit": COMMIT,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.release_dir / "snapshot-summary.md").write_text(
            "# Snapshot\n",
            encoding="utf-8",
        )
        (self.release_dir / "snapshot-provenance.json").write_text(
            json.dumps(
                {
                    "snapshot": {"tag": TAG, "commit": COMMIT},
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_archive_metadata_validates_against_schema(self) -> None:
        metadata = build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        Draft202012Validator(SCHEMA).validate(metadata)
        self.assertEqual(metadata["snapshot"]["tag"], TAG)
        self.assertEqual(metadata["snapshot"]["commit"], COMMIT)

    def test_metadata_generation_is_deterministic(self) -> None:
        first = build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        second = build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        self.assertEqual(first, second)

    def test_default_profile_excludes_all_dataset_bytes(self) -> None:
        _, manifest_path = build_bundle(
            self.root,
            self.release_dir,
            self.output_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}
        self.assertFalse(any("/datasets/" in path for path in paths))

    def test_canonical_byte_profile_includes_only_eligible_dataset(self) -> None:
        _, manifest_path = build_bundle(
            self.root,
            self.release_dir,
            self.output_dir,
            tag=TAG,
            commit=COMMIT,
            profile="eligible-canonical-bytes",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}
        self.assertTrue(
            any("datasets/eligible/raw/data.csv" in path for path in paths)
        )
        self.assertFalse(
            any("datasets/metadata-only/raw/secret.csv" in path for path in paths)
        )

    def test_assigned_identifier_is_bound_to_exact_snapshot(self) -> None:
        (self.root / "archive" / "identifiers.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "entries": [
                        {
                            "tag": TAG,
                            "commit": COMMIT,
                            "provider": "zenodo",
                            "identifier": "10.5281/zenodo.1234567",
                            "relation": "isIdenticalTo",
                        },
                        {
                            "tag": TAG,
                            "commit": "b" * 40,
                            "provider": "zenodo",
                            "identifier": "10.5281/zenodo.7654321",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        metadata = build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        self.assertEqual(
            metadata["assigned_archive_identifiers"],
            [
                {
                    "provider": "zenodo",
                    "identifier": "10.5281/zenodo.1234567",
                    "relation": "isIdenticalTo",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
