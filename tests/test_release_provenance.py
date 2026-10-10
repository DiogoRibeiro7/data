"""Tests for deterministic immutable release provenance metadata."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.generate_release_provenance import build_provenance, write_provenance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "schemas" / "release-provenance-v1.schema.json").read_text(
        encoding="utf-8"
    )
)
TAG = "snapshot-2026.10.10"
COMMIT = "1" * 40


class ReleaseProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.release_dir = Path(self.tempdir.name)
        self.manifest = {
            "manifest_version": 7,
            "repository": "DiogoRibeiro7/data",
            "tag": TAG,
            "commit": COMMIT,
            "registry_client": {
                "name": "diogo-data-registry",
                "version": "0.1.0",
                "public_api_version": 1,
            },
            "static_distribution": {"distribution_version": 1},
        }
        (self.release_dir / "snapshot-manifest.json").write_text(
            json.dumps(self.manifest, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (self.release_dir / "snapshot-summary.md").write_text(
            "# Snapshot\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_output_validates_against_schema(self) -> None:
        provenance = build_provenance(
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
        )
        Draft202012Validator(SCHEMA).validate(provenance)

    def test_artifact_digests_bind_manifest_and_summary(self) -> None:
        provenance = build_provenance(
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
        )
        digests = {item["name"]: item["sha256"] for item in provenance["artifacts"]}
        expected_manifest = hashlib.sha256(
            (self.release_dir / "snapshot-manifest.json").read_bytes()
        ).hexdigest()
        expected_summary = hashlib.sha256(
            (self.release_dir / "snapshot-summary.md").read_bytes()
        ).hexdigest()
        self.assertEqual(digests["snapshot-manifest.json"], expected_manifest)
        self.assertEqual(digests["snapshot-summary.md"], expected_summary)

    def test_generation_is_byte_deterministic(self) -> None:
        first = write_provenance(
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
        ).read_bytes()
        second = write_provenance(
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
        ).read_bytes()
        self.assertEqual(first, second)

    def test_manifest_identity_mismatch_is_rejected(self) -> None:
        self.manifest["commit"] = "2" * 40
        (self.release_dir / "snapshot-manifest.json").write_text(
            json.dumps(self.manifest, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "commit does not match"):
            build_provenance(
                self.release_dir,
                tag=TAG,
                commit=COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
