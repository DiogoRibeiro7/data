"""Tests for deterministic archive metadata and preservation bundles."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from data_registry import ReleaseVerificationError

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_archive_bundle as ARCHIVE  # noqa: E402

TAG = "snapshot-2099.01.01"
COMMIT = "a" * 40


def write_release_bundle(root: Path) -> Path:
    """Write a minimal valid deterministic snapshot release bundle."""

    release = root / "release"
    release.mkdir()
    manifest = {
        "manifest_version": 7,
        "repository": "DiogoRibeiro7/data",
        "tag": TAG,
        "commit": COMMIT,
        "static_distribution": {"distribution_version": 1},
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    summary_text = "# Fixture snapshot\n"

    (release / "snapshot-manifest.json").write_text(
        manifest_text,
        encoding="utf-8",
    )
    (release / "snapshot-summary.md").write_text(
        summary_text,
        encoding="utf-8",
    )

    provenance = {
        "schema_version": 1,
        "predicate_type": (
            "https://github.com/DiogoRibeiro7/data/"
            "attestations/snapshot-provenance/v1"
        ),
        "repository": "DiogoRibeiro7/data",
        "snapshot": {"tag": TAG, "commit": COMMIT},
        "artifacts": {
            "manifest": {
                "path": "snapshot-manifest.json",
                "sha256": hashlib.sha256(
                    manifest_text.encode("utf-8")
                ).hexdigest(),
            },
            "summary": {
                "path": "snapshot-summary.md",
                "sha256": hashlib.sha256(
                    summary_text.encode("utf-8")
                ).hexdigest(),
            },
        },
        "producer": {},
        "interfaces": {
            "snapshot_manifest_version": 7,
            "static_distribution_version": 1,
        },
        "assertions": [{"id": "fixture", "result": "pass"}],
    }
    (release / "snapshot-provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return release


class ArchiveBundleTests(unittest.TestCase):
    """Protect deterministic archive metadata and eligibility boundaries."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "repo"
        self.output_dir = Path(self.tempdir.name) / "archive"

        for directory in (
            "archive",
            "datasets/eligible/raw",
            "datasets/metadata-only/raw",
            "distribution/v1",
            "preservation",
            "reports",
            "schemas",
        ):
            (self.root / directory).mkdir(parents=True, exist_ok=True)

        (self.root / "CITATION.cff").write_text(
            yaml.safe_dump(
                {
                    "cff-version": "1.2.0",
                    "title": "Data Registry",
                    "abstract": "Deterministic registry archive fixture.",
                    "license": "MIT",
                    "authors": [
                        {
                            "family-names": "Ribeiro",
                            "given-names": "Diogo",
                        }
                    ],
                    "keywords": ["reproducibility", "data registry"],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        policy = {
            "schema_version": 1,
            "policy_version": 1,
            "repository": "DiogoRibeiro7/data",
            "archive_profiles": {
                "release-metadata": {
                    "description": "metadata only",
                    "include": [
                        "snapshot-manifest.json",
                        "snapshot-summary.md",
                        "snapshot-provenance.json",
                        "archive-metadata",
                    ],
                    "canonical_dataset_bytes": False,
                },
                "eligible-canonical-bytes": {
                    "description": "eligible bytes",
                    "include": [
                        "snapshot-manifest.json",
                        "snapshot-summary.md",
                        "snapshot-provenance.json",
                        "archive-metadata",
                        "eligible-canonical-dataset-bytes",
                    ],
                    "canonical_dataset_bytes": True,
                },
            },
        }
        (self.root / "preservation" / "policy-v1.json").write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        dataset_metadata = {
            "eligible": {
                "schema_version": 1,
                "id": "eligible",
                "title": "Eligible",
                "license": {
                    "name": "CC BY 4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0/",
                    "redistribution": "allowed",
                },
                "citation": {
                    "text": "Eligible dataset.",
                    "url": "https://example.test/eligible",
                },
            },
            "metadata-only": {
                "schema_version": 1,
                "id": "metadata-only",
                "title": "Metadata only",
                "license": {
                    "name": "Restricted",
                    "url": "https://example.test/restricted",
                    "redistribution": "restricted",
                },
                "citation": None,
            },
        }
        for dataset_id, metadata in dataset_metadata.items():
            (self.root / "datasets" / dataset_id / "metadata.yaml").write_text(
                yaml.safe_dump(metadata, sort_keys=False),
                encoding="utf-8",
            )

        (self.root / "datasets" / "eligible" / "raw" / "data.csv").write_text(
            "x\n1\n",
            encoding="utf-8",
        )
        (
            self.root
            / "datasets"
            / "metadata-only"
            / "raw"
            / "secret.csv"
        ).write_text(
            "x\n2\n",
            encoding="utf-8",
        )

        eligibility = {
            "schema_version": 1,
            "policy": {
                "path": "preservation/policy-v1.json",
                "schema_version": 1,
                "policy_version": 1,
            },
            "archive_profiles": policy["archive_profiles"],
            "release_metadata_eligibility": "eligible",
            "static_distribution_eligibility": "eligible",
            "summary": {
                "canonical_dataset_count": 2,
                "canonical_byte_archive_eligible_count": 1,
                "canonical_metadata_only_count": 1,
                "external_source_count": 0,
                "external_metadata_only_count": 0,
                "legacy_package_count": 0,
                "legacy_metadata_only_count": 0,
            },
            "canonical": [
                {
                    "id": "eligible",
                    "title": "Eligible",
                    "metadata_path": "datasets/eligible/metadata.yaml",
                    "byte_archive_eligibility": "eligible",
                    "reason": "allowed",
                    "redistribution": "allowed",
                    "license_name": "CC BY 4.0",
                },
                {
                    "id": "metadata-only",
                    "title": "Metadata only",
                    "metadata_path": "datasets/metadata-only/metadata.yaml",
                    "byte_archive_eligibility": "metadata-only",
                    "reason": "restricted",
                    "redistribution": "restricted",
                    "license_name": "Restricted",
                },
            ],
            "external": [],
            "legacy": [],
        }
        (self.root / "reports" / "preservation-eligibility.json").write_text(
            json.dumps(eligibility, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        (self.root / "archive" / "identifiers.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "entries": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "distribution" / "v1" / "index.json").write_text(
            json.dumps(
                {
                    "distribution_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "artifacts": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        for name in (
            "archive-metadata-v1.schema.json",
            "archive-identifiers-v1.schema.json",
            "archive-bundle-manifest-v1.schema.json",
        ):
            source = ROOT / "schemas" / name
            (self.root / "schemas" / name).write_bytes(source.read_bytes())

        self.release_dir = write_release_bundle(self.root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_archive_metadata_is_deterministic_and_preserves_licenses(self) -> None:
        first = ARCHIVE.build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        second = ARCHIVE.build_archive_metadata(
            self.root,
            self.release_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )

        self.assertEqual(first, second)
        by_id = {item["id"]: item for item in first["canonical_datasets"]}
        self.assertEqual(by_id["eligible"]["license"]["name"], "CC BY 4.0")
        self.assertEqual(
            by_id["eligible"]["citation"]["text"],
            "Eligible dataset.",
        )
        self.assertEqual(first["licensing"]["registry_tooling"], "MIT")
        self.assertTrue(
            first["licensing"]["archive_level_license_does_not_override_datasets"]
        )

    def test_default_profile_excludes_all_dataset_bytes(self) -> None:
        _, manifest_path = ARCHIVE.build_bundle(
            self.root,
            self.release_dir,
            self.output_dir,
            tag=TAG,
            commit=COMMIT,
            profile="release-metadata",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}

        self.assertFalse(any(path.startswith("datasets/") for path in paths))
        self.assertIn("release/snapshot-provenance.json", paths)
        self.assertIn("archive/archive-metadata.json", paths)

    def test_canonical_byte_profile_includes_only_eligible_dataset(self) -> None:
        _, manifest_path = ARCHIVE.build_bundle(
            self.root,
            self.release_dir,
            self.output_dir,
            tag=TAG,
            commit=COMMIT,
            profile="eligible-canonical-bytes",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}

        self.assertTrue(any(path.startswith("datasets/eligible/") for path in paths))
        self.assertFalse(
            any(path.startswith("datasets/metadata-only/") for path in paths)
        )

    def test_bundle_output_is_byte_deterministic_across_directories(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_meta, first_manifest = ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                Path(first),
                tag=TAG,
                commit=COMMIT,
                profile="release-metadata",
            )
            second_meta, second_manifest = ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                Path(second),
                tag=TAG,
                commit=COMMIT,
                profile="release-metadata",
            )

            self.assertEqual(first_meta.read_bytes(), second_meta.read_bytes())
            self.assertEqual(
                first_manifest.read_bytes(),
                second_manifest.read_bytes(),
            )

    def test_assigned_identifier_is_bound_to_exact_snapshot(self) -> None:
        identifiers_path = self.root / "archive" / "identifiers.json"
        payload = json.loads(identifiers_path.read_text(encoding="utf-8"))
        payload["entries"] = [
            {
                "tag": TAG,
                "commit": COMMIT,
                "provider": "zenodo",
                "identifier": "https://doi.org/10.5281/zenodo.1234567",
                "relation": "isIdenticalTo",
            }
        ]
        identifiers_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        metadata = ARCHIVE.build_archive_metadata(
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
                    "identifier": "https://doi.org/10.5281/zenodo.1234567",
                    "relation": "isIdenticalTo",
                }
            ],
        )

    def test_tampered_release_bundle_is_rejected(self) -> None:
        (self.release_dir / "snapshot-summary.md").write_text(
            "tampered\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ReleaseVerificationError,
            "digest mismatch",
        ):
            ARCHIVE.build_archive_metadata(
                self.root,
                self.release_dir,
                tag=TAG,
                commit=COMMIT,
                profile="release-metadata",
            )


if __name__ == "__main__":
    unittest.main()
