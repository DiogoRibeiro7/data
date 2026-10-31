"""Tests for deterministic archive metadata and preservation bundles."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import yaml

from data_registry import (
    ArchiveVerificationError,
    ReleaseVerificationError,
    verify_archive_bundle,
)
from data_registry.cli import main as registry_main

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
        newline="\n",
    )
    (release / "snapshot-summary.md").write_text(
        summary_text,
        encoding="utf-8",
        newline="\n",
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
                "files": [
                    {
                        "path": "raw/data.csv",
                        "role": "raw",
                        "format": "csv",
                        "sha256": hashlib.sha256(b"x\n1\n").hexdigest(),
                    }
                ],
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
                "files": [
                    {
                        "path": "raw/secret.csv",
                        "role": "raw",
                        "format": "csv",
                        "sha256": hashlib.sha256(b"x\n2\n").hexdigest(),
                    }
                ],
            },
        }
        for dataset_id, metadata in dataset_metadata.items():
            (self.root / "datasets" / dataset_id / "metadata.yaml").write_text(
                yaml.safe_dump(metadata, sort_keys=False),
                encoding="utf-8",
            )
            (self.root / "datasets" / dataset_id / "README.md").write_text(
                f"# {dataset_id}\n",
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
                    "artifacts": [
                        {
                            "name": "canonical",
                            "path": "canonical.json",
                            "schema_version": 1,
                            "source": "datasets/catalog.json",
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "distribution" / "v1" / "canonical.json").write_text(
            '{"schema_version": 1}\n', encoding="utf-8"
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

    def _build_verifiable_archive(self, profile: str = "release-metadata") -> Path:
        """Create an isolated archive ready for offline verification."""

        output = Path(self.tempdir.name) / f"verifiable-{profile}"
        ARCHIVE.build_bundle(
            self.root,
            self.release_dir,
            output,
            tag=TAG,
            commit=COMMIT,
            profile=profile,
        )
        return output

    @staticmethod
    def _update_record_for_file(archive: Path, relative: str) -> None:
        """Keep the outer manifest internally consistent after fixture tampering."""

        file_path = archive / "archive-bundle" / relative
        manifest_path = archive / "archive-bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = next(item for item in manifest["files"] if item["path"] == relative)
        record["sha256"] = hashlib.sha256(file_path.read_bytes()).hexdigest()
        record["size"] = file_path.stat().st_size
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_offline_verifier_accepts_both_archive_profiles(self) -> None:
        for profile in ("release-metadata", "eligible-canonical-bytes"):
            with self.subTest(profile=profile):
                archive = self._build_verifiable_archive(profile)
                manifest = json.loads(
                    (archive / "archive-bundle-manifest.json").read_text(encoding="utf-8")
                )

                result = verify_archive_bundle(
                    archive,
                    expected_tag=TAG,
                    expected_commit=COMMIT,
                    expected_profile=profile,
                )

                self.assertEqual(result.file_count, len(manifest["files"]))
                self.assertGreater(result.total_bytes, 0)
                self.assertEqual(result.profile, profile)
                self.assertEqual(len(result.manifest_sha256), 64)

    def test_offline_verifier_rejects_corrupted_declared_bytes(self) -> None:
        archive = self._build_verifiable_archive()
        path = archive / "archive-bundle" / "distribution/v1/canonical.json"
        path.write_text('{"schema_version": 2}\n', encoding="utf-8")

        with self.assertRaisesRegex(ArchiveVerificationError, "SHA-256 mismatch"):
            verify_archive_bundle(archive)

    def test_offline_verifier_rejects_missing_file(self) -> None:
        archive = self._build_verifiable_archive()
        (archive / "archive-bundle" / "CITATION.cff").unlink()

        with self.assertRaisesRegex(ArchiveVerificationError, "missing or unsafe"):
            verify_archive_bundle(archive)

    def test_offline_verifier_rejects_symlinked_file(self) -> None:
        archive = self._build_verifiable_archive()
        declared = archive / "archive-bundle" / "CITATION.cff"
        original = Path(self.tempdir.name) / "citation-copy.cff"
        original.write_bytes(declared.read_bytes())
        declared.unlink()
        declared.symlink_to(original)

        with self.assertRaisesRegex(ArchiveVerificationError, "missing or unsafe"):
            verify_archive_bundle(archive)

    def test_offline_verifier_rejects_undeclared_file(self) -> None:
        archive = self._build_verifiable_archive()
        (archive / "archive-bundle" / "unexpected.txt").write_text(
            "not in manifest\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(ArchiveVerificationError, "undeclared or missing"):
            verify_archive_bundle(archive)

    def test_offline_verifier_rejects_path_traversal(self) -> None:
        archive = self._build_verifiable_archive()
        path = archive / "archive-bundle-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "../outside.txt"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ArchiveVerificationError, "invalid archive file path"):
            verify_archive_bundle(archive)

    def test_offline_verifier_rejects_duplicate_paths(self) -> None:
        archive = self._build_verifiable_archive()
        path = archive / "archive-bundle-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"].append(manifest["files"][0].copy())
        path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ArchiveVerificationError, "duplicate archive file"):
            verify_archive_bundle(archive)

    def test_offline_verifier_enforces_requested_identity_and_profile(self) -> None:
        archive = self._build_verifiable_archive()
        for overrides, message in (
            ({"expected_tag": "snapshot-wrong"}, "tag does not match"),
            ({"expected_commit": "b" * 40}, "commit does not match"),
            ({"expected_profile": "eligible-canonical-bytes"}, "profile does not match"),
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(ArchiveVerificationError, message):
                    verify_archive_bundle(archive, **overrides)

    def test_offline_verifier_rechecks_canonical_redistribution_rights(self) -> None:
        archive = self._build_verifiable_archive("eligible-canonical-bytes")
        relative = "datasets/eligible/metadata.yaml"
        metadata_path = archive / "archive-bundle" / relative
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["license"]["redistribution"] = "restricted"
        metadata_path.write_text(yaml.safe_dump(metadata), encoding="utf-8")
        self._update_record_for_file(archive, relative)

        with self.assertRaisesRegex(ArchiveVerificationError, "redistribution is not allowed"):
            verify_archive_bundle(archive)

    def test_offline_verifier_detects_conflicting_eligibility_rights(self) -> None:
        archive = self._build_verifiable_archive("eligible-canonical-bytes")
        relative = "reports/preservation-eligibility.json"
        eligibility_path = archive / "archive-bundle" / relative
        report = json.loads(eligibility_path.read_text(encoding="utf-8"))
        report["canonical"][0]["redistribution"] = "restricted"
        eligibility_path.write_text(json.dumps(report), encoding="utf-8")
        self._update_record_for_file(archive, relative)

        with self.assertRaisesRegex(ArchiveVerificationError, "lacks redistribution rights"):
            verify_archive_bundle(archive)

    def test_offline_verifier_checks_distribution_index_coverage(self) -> None:
        archive = self._build_verifiable_archive()
        relative = "distribution/v1/index.json"
        index_path = archive / "archive-bundle" / relative
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["artifacts"][0]["path"] = "unlisted.json"
        index_path.write_text(json.dumps(index), encoding="utf-8")
        self._update_record_for_file(archive, relative)

        with self.assertRaisesRegex(ArchiveVerificationError, "artifacts differ"):
            verify_archive_bundle(archive)

    def test_verify_archive_cli_runs_without_registry_checkout(self) -> None:
        archive = self._build_verifiable_archive()
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            code = registry_main(
                [
                    "--root", str(Path(self.tempdir.name) / "not-a-checkout"),
                    "verify-archive", "--bundle", str(archive),
                    "--tag", TAG, "--commit", COMMIT,
                    "--profile", "release-metadata", "--json",
                ]
            )

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["profile"], "release-metadata")
        self.assertGreater(payload["file_count"], 0)

    def test_verify_archive_cli_reports_mismatch_and_failure_status(self) -> None:
        archive = self._build_verifiable_archive()
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = registry_main(
                [
                    "verify-archive", "--bundle", str(archive),
                    "--tag", TAG, "--commit", "b" * 40,
                ]
            )

        self.assertEqual(code, 1)
        self.assertIn("commit does not match", errors.getvalue())

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
        self.assertIn("distribution/v1/index.json", paths)
        self.assertIn("distribution/v1/canonical.json", paths)

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
        self.assertIn("datasets/eligible/raw/data.csv", paths)
        self.assertIn("datasets/eligible/metadata.yaml", paths)
        self.assertIn("datasets/eligible/README.md", paths)
        self.assertFalse(
            any(path.startswith("datasets/metadata-only/") for path in paths)
        )

    def test_unlisted_files_are_not_copied_into_byte_archive(self) -> None:
        stray = self.root / "datasets" / "eligible" / "raw" / ".partial-export.tmp"
        stray.write_bytes(b"not registered for redistribution\n")

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

        self.assertNotIn("datasets/eligible/raw/.partial-export.tmp", paths)
        self.assertFalse(
            (
                self.output_dir
                / "archive-bundle"
                / "datasets"
                / "eligible"
                / "raw"
                / ".partial-export.tmp"
            ).exists()
        )

    def test_unlisted_distribution_files_are_not_archived(self) -> None:
        (self.root / "distribution" / "v1" / ".untracked.json").write_text(
            '{"private": true}\n', encoding="utf-8"
        )

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

        self.assertIn("distribution/v1/canonical.json", paths)
        self.assertNotIn("distribution/v1/.untracked.json", paths)

    def test_distribution_index_cannot_reference_parent_directory(self) -> None:
        index_path = self.root / "distribution" / "v1" / "index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["artifacts"][0]["path"] = "../private.json"
        index_path.write_text(json.dumps(index), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "invalid distribution artifact path"):
            ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                self.output_dir,
                tag=TAG,
                commit=COMMIT,
                profile="release-metadata",
            )

    def test_false_eligibility_cannot_override_restricted_license(self) -> None:
        report_path = self.root / "reports" / "preservation-eligibility.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        restricted = next(
            item for item in report["canonical"] if item["id"] == "metadata-only"
        )
        restricted["byte_archive_eligibility"] = "eligible"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "eligibility conflicts with"):
            ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                self.output_dir,
                tag=TAG,
                commit=COMMIT,
                profile="eligible-canonical-bytes",
            )

    def test_declared_file_checksum_is_reverified_before_archiving(self) -> None:
        source = self.root / "datasets" / "eligible" / "raw" / "data.csv"
        source.write_text("tampered source\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "archived bytes have SHA-256 mismatch"):
            ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                self.output_dir,
                tag=TAG,
                commit=COMMIT,
                profile="eligible-canonical-bytes",
            )

    def test_declared_file_path_cannot_escape_dataset(self) -> None:
        metadata_path = self.root / "datasets" / "eligible" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["files"][0]["path"] = "../metadata-only/raw/secret.csv"
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "noncanonical dataset file path"):
            ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                self.output_dir,
                tag=TAG,
                commit=COMMIT,
                profile="eligible-canonical-bytes",
            )

    def test_declared_symlink_cannot_read_outside_dataset(self) -> None:
        outside = Path(self.tempdir.name) / "private.csv"
        outside.write_text("not in the dataset\n", encoding="utf-8")
        source = self.root / "datasets" / "eligible" / "raw" / "data.csv"
        source.unlink()
        source.symlink_to(outside)

        metadata_path = self.root / "datasets" / "eligible" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["files"][0]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "escapes dataset root"):
            ARCHIVE.build_bundle(
                self.root,
                self.release_dir,
                self.output_dir,
                tag=TAG,
                commit=COMMIT,
                profile="eligible-canonical-bytes",
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
