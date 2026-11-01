"""Offline contract tests for provider-neutral canonical ingestion manifests."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from importlib import resources
from pathlib import Path
from unittest.mock import patch

import jsonschema
import yaml

import data_registry.handoff_verification as handoff_verification
from data_registry import (
    HandoffVerificationError,
    RegistryClient,
    RegistryError,
    verify_handoff_manifest,
)
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

    def create_committed_checkout(self) -> str:
        """Commit the fixture in an isolated Git repository and return HEAD."""

        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(
            [
                "git", "-C", str(self.root), "add", "--",
                "datasets/test-dataset/metadata.yaml",
                "datasets/test-dataset/raw/input.csv",
                "datasets/test-dataset/derived/summary.csv",
            ],
            check=True,
        )
        subprocess.run(
            [
                "git", "-C", str(self.root),
                "-c", "user.name=Fixture Author",
                "-c", "user.email=fixture@example.test",
                "-c", "commit.gpgsign=false",
                "commit", "-qm", "Synthetic canonical fixture",
            ],
            check=True,
        )
        return subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            text=True,
        ).strip()

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
        self.assertFalse(first["checkout_identity_verified"])
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
        self.assertFalse(result["checkout_identity_verified"])
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

    def test_checkout_verification_requires_local_byte_verification(self) -> None:
        with self.assertRaisesRegex(RegistryError, "requires verify_local"):
            self.client.handoff("test-dataset", commit=COMMIT, verify_checkout=True)

    def test_checkout_verification_rejects_non_git_directory(self) -> None:
        with self.assertRaisesRegex(RegistryError, "Git checkout verification failed"):
            self.client.handoff(
                "test-dataset", commit=COMMIT,
                verify_local=True, verify_checkout=True,
            )

    def test_checkout_verification_accepts_committed_fixture(self) -> None:
        head = self.create_committed_checkout()
        payload = self.client.handoff(
            "test-dataset", commit=head,
            verify_local=True, verify_checkout=True,
        ).to_mapping()

        self.assertTrue(payload["checkout_identity_verified"])
        self.assertTrue(payload["local_bytes_verified"])
        self.assertEqual(payload["registry"]["commit"], head)

    def test_checkout_verification_rejects_wrong_commit(self) -> None:
        head = self.create_committed_checkout()
        wrong = "b" * 40 if head != "b" * 40 else "c" * 40

        with self.assertRaisesRegex(RegistryError, "checkout identity mismatch"):
            self.client.handoff(
                "test-dataset", commit=wrong,
                verify_local=True, verify_checkout=True,
            )

    def test_checkout_verification_rejects_dirty_metadata(self) -> None:
        head = self.create_committed_checkout()
        self.metadata["title"] = "Locally changed title"
        self.write_metadata()

        with self.assertRaisesRegex(RegistryError, "metadata.yaml"):
            self.client.handoff(
                "test-dataset", commit=head,
                verify_local=True, verify_checkout=True,
            )

    def test_checkout_verification_rejects_mismatched_git_blob(self) -> None:
        # Metadata declares the original checksum, but HEAD contains other bytes.
        source = self.root / "datasets/test-dataset/raw/input.csv"
        source.write_bytes(b"committed-but-unexpected\n")
        head = self.create_committed_checkout()
        source.write_bytes(self.raw_bytes)

        # The metadata checksum passes, yet HEAD contains different bytes.
        with self.assertRaisesRegex(RegistryError, "raw/input.csv"):
            self.client.handoff(
                "test-dataset", commit=head,
                verify_local=True, verify_checkout=True,
            )

    def test_checkout_verification_type_check(self) -> None:
        with self.assertRaisesRegex(TypeError, "verify_checkout must be bool"):
            self.client.handoff(  # type: ignore[arg-type]
                "test-dataset", commit=COMMIT,
                verify_local=True, verify_checkout="yes",
            )

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

    def test_checkout_schema_field_is_optional_for_existing_v1_consumers(self) -> None:
        """The additive proof flag must not invalidate existing v1 manifests."""

        payload = self.client.handoff("test-dataset", commit=COMMIT).to_mapping()
        schema = json.loads(
            (ROOT / "schemas/ingestion-handoff-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        del payload["checkout_identity_verified"]
        jsonschema.validate(payload, schema)

        payload["checkout_identity_verified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_cli_reports_verified_checkout_identity(self) -> None:
        head = self.create_committed_checkout()
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "--root", str(self.root), "handoff", "test-dataset",
                    "--commit", head, "--verify-local", "--verify-checkout",
                    "--json",
                ]
            )

        self.assertEqual(exit_code, 0)
        result = json.loads(output.getvalue())
        schema = json.loads(
            (ROOT / "schemas/ingestion-handoff-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(result, schema)
        self.assertTrue(result["checkout_identity_verified"])

    def received_handoff(
        self, *, verify_local: bool = False, commit: str = COMMIT
    ) -> tuple[dict[str, object], Path, Path]:
        """Create a consumer storage fixture from the source-side plan."""

        payload = self.client.handoff(
            "test-dataset", commit=commit, verify_local=verify_local
        ).to_mapping()
        storage_root = self.root / "received"
        storage_root.mkdir()
        for obj in payload["objects"]:
            source = self.root / obj["source_path"]
            target = storage_root / obj["storage_key"]
            target.parent.mkdir(parents=True)
            target.write_bytes(source.read_bytes())
        manifest = self.root / "handoff.json"
        self.write_handoff(manifest, payload)
        return payload, manifest, storage_root

    @staticmethod
    def write_handoff(path: Path, payload: dict[str, object]) -> None:
        """Persist an altered or unaltered manifest for a consumer."""

        path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    def test_offline_verifier_accepts_metadata_only_handoff(self) -> None:
        _, manifest, storage_root = self.received_handoff()
        with patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("unexpected network access"),
        ):
            result = verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=COMMIT,
                expected_repository="DiogoRibeiro7/data",
                expected_dataset_id="test-dataset",
            )
        self.assertEqual(result.verified_objects, 2)
        self.assertEqual(result.total_bytes, len(self.raw_bytes) + len(self.derived_bytes))
        self.assertEqual(result.manifest_sha256, hashlib.sha256(manifest.read_bytes()).hexdigest())

    def test_offline_verifier_accepts_preverified_sizes_and_extra_files(self) -> None:
        _, manifest, storage_root = self.received_handoff(verify_local=True)
        (storage_root / "unrelated.txt").write_text("other dataset", encoding="utf-8")
        result = verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        self.assertEqual(result.verified_objects, 2)

    def test_offline_verifier_requires_independent_commit(self) -> None:
        _, manifest, storage_root = self.received_handoff()
        for commit in ("main", "a" * 40):
            with self.subTest(commit=commit), self.assertRaises(HandoffVerificationError):
                verify_handoff_manifest(manifest, storage_root, expected_commit=commit)

    def test_offline_verifier_checks_optional_identities(self) -> None:
        _, manifest, storage_root = self.received_handoff()
        for options in (
            {"expected_repository": "other/repository"},
            {"expected_dataset_id": "another-dataset"},
        ):
            with self.subTest(options=options), self.assertRaises(HandoffVerificationError):
                verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT, **options)

    def test_offline_verifier_rejects_missing_and_changed_files(self) -> None:
        payload, manifest, storage_root = self.received_handoff(verify_local=True)
        target = storage_root / payload["objects"][0]["storage_key"]
        original = target.read_bytes()
        target.write_bytes(original.replace(b"2024,2", b"2024,8"))
        with self.assertRaisesRegex(HandoffVerificationError, "SHA-256 mismatch"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        target.write_bytes(original[:-1])
        with self.assertRaisesRegex(HandoffVerificationError, "byte size mismatch"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        target.unlink()
        with self.assertRaisesRegex(HandoffVerificationError, "missing or unsafe"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_rejects_symlinked_object(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        target = storage_root / payload["objects"][0]["storage_key"]
        alternate = self.root / "object-copy.csv"
        alternate.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(alternate)
        with self.assertRaisesRegex(HandoffVerificationError, "missing or unsafe"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_rejects_traversal_and_wrong_key(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        original = payload["objects"][0]["storage_key"]
        for invalid in ("canonical/test-dataset/../escape.csv", "canonical/test-dataset/not-a-hash/raw/input.csv"):
            payload["objects"][0]["storage_key"] = invalid
            self.write_handoff(manifest, payload)
            with self.subTest(invalid=invalid), self.assertRaises(HandoffVerificationError):
                verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        payload["objects"][0]["storage_key"] = original

    def test_offline_verifier_rejects_wrong_dataset_source_path(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        payload["objects"][0]["source_path"] = (
            "datasets/other-dataset/derived/summary.csv"
        )
        self.write_handoff(manifest, payload)
        with self.assertRaisesRegex(HandoffVerificationError, "source identity"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_rejects_symlinked_storage_directory(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        key = payload["objects"][0]["storage_key"]
        target = storage_root / key
        outside = self.root / "alternate-storage"
        outside.mkdir()
        (outside / target.name).write_bytes(target.read_bytes())
        target.unlink()
        target.parent.rmdir()
        target.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(HandoffVerificationError, "missing or unsafe"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_rejects_wrong_source_uri_and_duplicate(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        original = payload["objects"][0]["source_uri"]
        payload["objects"][0]["source_uri"] = "https://example.org/mutable.csv"
        self.write_handoff(manifest, payload)
        with self.assertRaisesRegex(HandoffVerificationError, "source URI mismatch"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        payload["objects"][0]["source_uri"] = original
        payload["objects"].append(dict(payload["objects"][0]))
        self.write_handoff(manifest, payload)
        with self.assertRaisesRegex(HandoffVerificationError, "duplicate"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_rejects_invalid_schema_and_bad_json(self) -> None:
        payload, manifest, storage_root = self.received_handoff()
        payload["manifest_version"] = 2
        self.write_handoff(manifest, payload)
        with self.assertRaisesRegex(HandoffVerificationError, "schema"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)
        manifest.write_text("{not valid json", encoding="utf-8")
        with self.assertRaisesRegex(HandoffVerificationError, "cannot read"):
            verify_handoff_manifest(manifest, storage_root, expected_commit=COMMIT)

    def test_offline_verifier_cli_runs_outside_git_checkout(self) -> None:
        _, manifest, storage_root = self.received_handoff()
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main([
                "--root", str(self.root / "nonexistent-registry"), "verify-handoff",
                "--manifest", str(manifest), "--storage-root", str(storage_root),
                "--commit", COMMIT, "--repository", "DiogoRibeiro7/data",
                "--dataset-id", "test-dataset", "--json",
            ])
        self.assertEqual(exit_code, 0)
        result = json.loads(output.getvalue())
        self.assertTrue(result["ok"])
        self.assertEqual(result["verified_objects"], 2)
        self.assertEqual(result["commit"], COMMIT)
        self.assertFalse(result["trusted_checkout_verified"])

    def test_trusted_checkout_accepts_metadata_only_plan(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        with patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("unexpected network access"),
        ):
            result = verify_handoff_manifest(
                manifest,
                storage_root,
                expected_commit=head,
                expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root,
            )
        self.assertTrue(result.trusted_checkout_verified)
        self.assertEqual(result.verified_objects, 2)

    def test_trusted_checkout_requires_independent_repository_identity(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        with self.assertRaisesRegex(HandoffVerificationError, "expected repository"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, trusted_checkout=self.root,
            )

    def test_trusted_checkout_accepts_checked_and_legacy_v1_plans(self) -> None:
        head = self.create_committed_checkout()
        payload, manifest, storage_root = self.received_handoff(
            commit=head, verify_local=True
        )
        payload.pop("checkout_identity_verified")  # Older v1 plans lack this flag.
        self.write_handoff(manifest, payload)
        result = verify_handoff_manifest(
            manifest, storage_root, expected_commit=head,
            expected_repository="DiogoRibeiro7/data", trusted_checkout=self.root,
        )
        self.assertTrue(result.trusted_checkout_verified)

    def test_trusted_checkout_rejects_self_consistent_forged_object(self) -> None:
        """The commit string alone cannot authenticate an invented checksum."""

        head = self.create_committed_checkout()
        payload, manifest, storage_root = self.received_handoff(commit=head)
        obj = payload["objects"][0]
        forged = b"plausible but not committed\n"
        forged_sha = hashlib.sha256(forged).hexdigest()
        obj["sha256"] = forged_sha
        obj["storage_key"] = f"canonical/test-dataset/{forged_sha}/derived/summary.csv"
        path = storage_root / obj["storage_key"]
        path.parent.mkdir(parents=True)
        path.write_bytes(forged)
        self.write_handoff(manifest, payload)

        # The original verifier proves only internal consistency.
        verify_handoff_manifest(manifest, storage_root, expected_commit=head)
        with self.assertRaisesRegex(HandoffVerificationError, "trusted checkout disagrees"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root,
            )

    def test_trusted_checkout_rejects_incomplete_source_list(self) -> None:
        head = self.create_committed_checkout()
        payload, manifest, storage_root = self.received_handoff(commit=head)
        payload["objects"].pop()
        self.write_handoff(manifest, payload)
        verify_handoff_manifest(manifest, storage_root, expected_commit=head)
        with self.assertRaisesRegex(HandoffVerificationError, "source file set"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root,
            )

    def test_trusted_checkout_rejects_changed_provenance_fields(self) -> None:
        head = self.create_committed_checkout()
        payload, manifest, storage_root = self.received_handoff(commit=head)
        for field in ("title", "citation", "source", "license"):
            altered = json.loads(json.dumps(payload))
            if isinstance(altered[field], dict):
                first = "publisher" if field == "source" else "name"
                altered[field][first] = "Forged provenance"
            else:
                altered[field] = "Forged provenance"
            self.write_handoff(manifest, altered)
            with self.subTest(field=field), self.assertRaisesRegex(
                HandoffVerificationError, f"handoff field: {field}"
            ):
                verify_handoff_manifest(
                    manifest, storage_root,
                    expected_commit=head, expected_repository="DiogoRibeiro7/data",
                    trusted_checkout=self.root,
                )

    def test_trusted_checkout_rejects_nonrepository(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        with self.assertRaisesRegex(HandoffVerificationError, "trusted checkout could not"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root / "not-a-repository",
            )

    def test_trusted_checkout_rejects_wrong_head(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        subprocess.run(
            [
                "git", "-C", str(self.root),
                "-c", "user.name=Fixture Author",
                "-c", "user.email=fixture@example.test",
                "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "Later unrelated commit",
            ],
            check=True,
        )
        with self.assertRaisesRegex(HandoffVerificationError, "checkout identity mismatch"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root,
            )

    def test_trusted_checkout_rejects_dirty_metadata(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        self.metadata["title"] = "Dirty working tree"
        self.write_metadata()
        with self.assertRaisesRegex(HandoffVerificationError, "metadata.yaml"):
            verify_handoff_manifest(
                manifest, storage_root,
                expected_commit=head, expected_repository="DiogoRibeiro7/data",
                trusted_checkout=self.root,
            )

    def test_trusted_checkout_cli_reports_provenance_verification(self) -> None:
        head = self.create_committed_checkout()
        _, manifest, storage_root = self.received_handoff(commit=head)
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([
                "--root", str(self.root / "not-used"), "verify-handoff",
                "--manifest", str(manifest), "--storage-root", str(storage_root),
                "--commit", head, "--repository", "DiogoRibeiro7/data",
                "--trusted-checkout", str(self.root), "--json",
            ])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())["trusted_checkout_verified"])

    def test_manifest_fingerprint_uses_exact_parsed_bytes(self) -> None:
        """A changing manifest cannot re-label an earlier verification result."""

        _, manifest, storage_root = self.received_handoff()
        original_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
        original_hasher = handoff_verification._sha256_file
        calls = 0

        def mutate_manifest_on_first_object(path: Path) -> str:
            nonlocal calls
            calls += 1
            if calls == 1:
                manifest.write_text('"changed"', encoding="utf-8")
            return original_hasher(path)

        with patch(
            "data_registry.handoff_verification._sha256_file",
            side_effect=mutate_manifest_on_first_object,
        ):
            result = verify_handoff_manifest(
                manifest, storage_root, expected_commit=COMMIT
            )
        self.assertEqual(result.manifest_sha256, original_sha)


if __name__ == "__main__":
    unittest.main()
