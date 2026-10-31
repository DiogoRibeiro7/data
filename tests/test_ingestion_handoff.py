"""Offline contract tests for provider-neutral canonical ingestion manifests."""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from importlib import resources
from pathlib import Path
from unittest.mock import patch

import jsonschema
import yaml

from data_registry import RegistryClient, RegistryError
from data_registry.cli import main

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "0123456789abcdef0123456789abcdef01234567"


class IngestionHandoffTests(unittest.TestCase):
    """A canonical handoff must be repeatable, safe, and storage agnostic."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        dataset_root = self.root / "datasets" / "test-dataset"
        dataset_root.joinpath("raw").mkdir(parents=True)
        dataset_root.joinpath("derived").mkdir()

        self.raw_bytes = b"year,value\n2024,1\n"
        self.derived_bytes = b"year,value\n2024,2\n"
        (dataset_root / "raw" / "input.csv").write_bytes(self.raw_bytes)
        (dataset_root / "derived" / "summary.csv").write_bytes(self.derived_bytes)

        self.metadata = {
            "schema_version": 1,
            "id": "test-dataset",
            "title": "Test dataset",
            "description": "Synthetic test data for offline transfer contracts.",
            "domain": ["testing"],
            "source": {
                "publisher": "Test publisher",
                "url": "https://example.org/data",
                "snapshot": "2024 release",
                "retrieved_at": "2026-10-31",
            },
            "license": {
                "name": "CC0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "citation": {"text": "Test publisher (2024). Test dataset."},
            # Reverse order intentionally; output must not depend on YAML order.
            "files": [
                {
                    "path": "raw/input.csv",
                    "role": "raw",
                    "format": "csv",
                    "sha256": hashlib.sha256(self.raw_bytes).hexdigest(),
                },
                {
                    "path": "derived/summary.csv",
                    "role": "derived",
                    "format": "csv",
                    "sha256": hashlib.sha256(self.derived_bytes).hexdigest(),
                },
            ],
        }
        self.metadata_path = dataset_root / "metadata.yaml"
        self.write_metadata()
        self.client = RegistryClient(self.root)

    def write_metadata(self) -> None:
        """Persist the small synthetic canonical record used by each test."""

        self.metadata_path.write_text(
            yaml.safe_dump(self.metadata, sort_keys=False), encoding="utf-8"
        )

    def test_manifest_is_stable_and_has_full_provenance(self) -> None:
        first = self.client.handoff("test-dataset", commit=COMMIT).to_mapping()
        second = self.client.handoff("test-dataset", commit=COMMIT).to_mapping()

        self.assertEqual(first, second)
        self.assertEqual(first["manifest_version"], 1)
        self.assertEqual(first["registry"], {
            "repository": "DiogoRibeiro7/data",
            "commit": COMMIT,
        })
        self.assertEqual(first["source"]["snapshot"], "2024 release")
        self.assertEqual(first["license"]["redistribution"], "allowed")
        self.assertFalse(first["local_bytes_verified"])
        self.assertEqual(
            [item["source_path"] for item in first["objects"]],
            [
                "datasets/test-dataset/derived/summary.csv",
                "datasets/test-dataset/raw/input.csv",
            ],
        )
        self.assertEqual(first["objects"][1]["size_bytes"], None)
        self.assertEqual(
            first["objects"][1]["storage_key"],
            "canonical/test-dataset/"
            f"{hashlib.sha256(self.raw_bytes).hexdigest()}/raw/input.csv",
        )
        self.assertIn(f"/{COMMIT}/datasets/", first["objects"][0]["source_uri"])

    def test_verify_local_reports_verified_sizes(self) -> None:
        result = self.client.handoff(
            "test-dataset", commit=COMMIT, verify_local=True
        ).to_mapping()

        self.assertTrue(result["local_bytes_verified"])
        self.assertEqual(
            {item["size_bytes"] for item in result["objects"]},
            {len(self.raw_bytes), len(self.derived_bytes)},
        )

    def test_checksum_mismatch_fails_before_manifest_is_emitted(self) -> None:
        (self.root / "datasets/test-dataset/raw/input.csv").write_bytes(b"changed")
        with self.assertRaisesRegex(RegistryError, "checksum mismatch"):
            self.client.handoff("test-dataset", commit=COMMIT, verify_local=True)

    def test_missing_local_source_fails_verification(self) -> None:
        (self.root / "datasets/test-dataset/raw/input.csv").unlink()
        with self.assertRaisesRegex(RegistryError, "missing or unsafe"):
            self.client.handoff("test-dataset", commit=COMMIT, verify_local=True)

    def test_symlink_into_unapproved_directory_is_refused(self) -> None:
        source_path = self.root / "datasets/test-dataset/raw/input.csv"
        unapproved = self.root / "external" / "unapproved.csv"
        unapproved.parent.mkdir()
        unapproved.write_bytes(self.raw_bytes)
        source_path.unlink()
        source_path.symlink_to(unapproved)
        with self.assertRaisesRegex(RegistryError, "missing or unsafe"):
            self.client.handoff("test-dataset", commit=COMMIT, verify_local=True)

    def test_restricted_redistribution_is_refused(self) -> None:
        self.metadata["license"]["redistribution"] = "restricted"
        self.write_metadata()
        with self.assertRaisesRegex(RegistryError, "redistribution permission"):
            self.client.handoff("test-dataset", commit=COMMIT)

    def test_path_traversal_is_refused(self) -> None:
        self.metadata["files"][0]["path"] = "raw/../outside.csv"
        self.write_metadata()
        with self.assertRaisesRegex(
            RegistryError, "invalid immutable source reference"
        ):
            self.client.handoff("test-dataset", commit=COMMIT)

    def test_ambiguous_or_duplicate_files_are_refused(self) -> None:
        self.metadata["files"].append(dict(self.metadata["files"][0]))
        self.write_metadata()
        with self.assertRaisesRegex(RegistryError, "duplicate canonical source"):
            self.client.handoff("test-dataset", commit=COMMIT)

    def test_invalid_commit_is_refused(self) -> None:
        with self.assertRaisesRegex(RegistryError, "40-character"):
            self.client.handoff("test-dataset", commit="main")

    def test_noncanonical_dataset_is_not_eligible(self) -> None:
        with self.assertRaisesRegex(RegistryError, "unknown registry id"):
            self.client.handoff("not-a-canonical-dataset", commit=COMMIT)

    def test_handoff_never_opens_network_connections(self) -> None:
        with patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("unexpected network access"),
        ):
            self.client.handoff("test-dataset", commit=COMMIT, verify_local=True)

    def test_cli_json_matches_versioned_schema(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "--root", str(self.root), "handoff", "test-dataset",
                    "--commit", COMMIT, "--verify-local", "--json",
                ]
            )

        self.assertEqual(code, 0)
        manifest = json.loads(output.getvalue())
        schema_path = ROOT / "schemas" / "ingestion-handoff-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(manifest, schema)

        packaged = resources.files("data_registry").joinpath(
            "schemas/ingestion-handoff-v1.schema.json"
        )
        self.assertEqual(schema, json.loads(packaged.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
