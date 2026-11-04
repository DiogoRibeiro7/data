"""Tests for offline immutable release verification."""

from __future__ import annotations

import hashlib
import io
from contextlib import redirect_stdout
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from data_registry import cli as CLI
from data_registry import release_verification as RELEASE
from data_registry.release_verification import (
    ReleaseVerificationError,
    verify_release_bundle,
)


def write_bundle(root: Path) -> tuple[str, str]:
    tag = "snapshot-2026.10.10"
    commit = "a" * 40
    manifest = {
        "manifest_version": 7,
        "repository": "DiogoRibeiro7/data",
        "tag": tag,
        "commit": commit,
        "static_distribution": {"distribution_version": 1},
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    summary_text = "# Summary\n"
    (root / "snapshot-manifest.json").write_text(manifest_text, encoding="utf-8", newline="\n")
    (root / "snapshot-summary.md").write_text(summary_text, encoding="utf-8", newline="\n")
    provenance = {
        "schema_version": 1,
        "predicate_type": "https://github.com/DiogoRibeiro7/data/attestations/snapshot-provenance/v1",
        "repository": "DiogoRibeiro7/data",
        "snapshot": {"tag": tag, "commit": commit},
        "artifacts": {
            "manifest": {
                "path": "snapshot-manifest.json",
                "sha256": hashlib.sha256(manifest_text.encode()).hexdigest(),
            },
            "summary": {
                "path": "snapshot-summary.md",
                "sha256": hashlib.sha256(summary_text.encode()).hexdigest(),
            },
        },
        "producer": {},
        "interfaces": {
            "snapshot_manifest_version": 7,
            "static_distribution_version": 1,
        },
        "assertions": [{"id": "fixture", "result": "pass"}],
    }
    (root / "snapshot-provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return tag, commit


def rewrite_release_versions(
    root: Path,
    *,
    manifest_version: object = 7,
    distribution_version: object = 1,
) -> None:
    """Keep a deliberately unsupported release internally self-consistent."""

    manifest_path = root / "snapshot-manifest.json"
    provenance_path = root / "snapshot-provenance.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    manifest["manifest_version"] = manifest_version
    manifest["static_distribution"]["distribution_version"] = distribution_version
    provenance["interfaces"]["snapshot_manifest_version"] = manifest_version
    provenance["interfaces"]["static_distribution_version"] = distribution_version

    content = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    manifest_path.write_text(content, encoding="utf-8")
    provenance["artifacts"]["manifest"]["sha256"] = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()
    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class ReleaseVerificationTests(unittest.TestCase):
    def test_valid_bundle_verifies_offline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            result = verify_release_bundle(
                root,
                expected_tag=tag,
                expected_commit=commit,
            )

        self.assertEqual(result.tag, tag)
        self.assertEqual(result.commit, commit)
        self.assertEqual(result.manifest_version, 7)

    def test_rejects_unknown_and_non_integer_manifest_versions(self) -> None:
        for version, message in (
            (10, "unsupported snapshot manifest version"),
            (True, "manifest version must be an integer"),
            (9.0, "manifest version must be an integer"),
        ):
            with self.subTest(version=version):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    write_bundle(root)
                    rewrite_release_versions(root, manifest_version=version)
                    with self.assertRaisesRegex(ReleaseVerificationError, message):
                        verify_release_bundle(root)

    def test_rejects_boolean_provenance_interface_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_bundle(root)
            rewrite_release_versions(root, manifest_version=1)
            path = root / "snapshot-provenance.json"
            provenance = json.loads(path.read_text(encoding="utf-8"))
            provenance["interfaces"]["snapshot_manifest_version"] = True
            path.write_text(json.dumps(provenance), encoding="utf-8")
            with self.assertRaisesRegex(
                ReleaseVerificationError, "provenance/manifest version mismatch"
            ):
                verify_release_bundle(root)

    def test_rejects_unsupported_distribution_version(self) -> None:
        for version in (2, True):
            with self.subTest(version=version):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    write_bundle(root)
                    rewrite_release_versions(root, distribution_version=version)
                    with self.assertRaisesRegex(
                        ReleaseVerificationError,
                        "unsupported static distribution version",
                    ):
                        verify_release_bundle(root)

    def test_rejects_boolean_provenance_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_bundle(root)
            path = root / "snapshot-provenance.json"
            provenance = json.loads(path.read_text(encoding="utf-8"))
            provenance["schema_version"] = True
            path.write_text(json.dumps(provenance), encoding="utf-8")
            with self.assertRaisesRegex(
                ReleaseVerificationError, "unsupported provenance schema version"
            ):
                verify_release_bundle(root)

    def test_reported_manifest_digest_identifies_parsed_bytes(self) -> None:
        """Later changes to a manifest cannot change the checked digest."""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_bundle(root)
            manifest_path = root / "snapshot-manifest.json"
            original = manifest_path.read_bytes()
            read_json = RELEASE._json

            def replace_after_manifest_parse(path: Path) -> dict[str, object]:
                # Provenance is read after the manifest has been parsed.
                if path.name == "snapshot-provenance.json":
                    manifest_path.write_text("{}\n", encoding="utf-8")
                return read_json(path)

            with patch.object(RELEASE, "_json", side_effect=replace_after_manifest_parse):
                result = verify_release_bundle(root)

            self.assertEqual(
                result.manifest_sha256, hashlib.sha256(original).hexdigest()
            )
            self.assertNotEqual(
                result.manifest_sha256,
                hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            )

    def test_cli_verify_release_returns_machine_readable_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = CLI.main(
                    [
                        "--root",
                        str(root),
                        "verify-release",
                        "--bundle",
                        str(root),
                        "--tag",
                        tag,
                        "--commit",
                        commit,
                        "--json",
                    ]
                )

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tag"], tag)
        self.assertEqual(payload["commit"], commit)

    def test_tampered_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            (root / "snapshot-manifest.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "digest mismatch",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)

    def test_tampered_summary_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            (root / "snapshot-summary.md").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "summary.md digest mismatch",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)

    def test_tag_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, commit = write_bundle(root)
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "release tag mismatch",
            ):
                verify_release_bundle(
                    root,
                    expected_tag="snapshot-2026.10.11",
                    expected_commit=commit,
                )

    def test_commit_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, _ = write_bundle(root)
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "release commit mismatch",
            ):
                verify_release_bundle(
                    root,
                    expected_tag=tag,
                    expected_commit="b" * 40,
                )

    def test_manifest_provenance_identity_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            provenance_path = root / "snapshot-provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["snapshot"]["tag"] = "snapshot-2026.10.11"
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "manifest/provenance tag mismatch",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)

    def test_static_distribution_version_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            provenance_path = root / "snapshot-provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["interfaces"]["static_distribution_version"] = 2
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "static-distribution version mismatch",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)

    def test_repository_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            provenance_path = root / "snapshot-provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["repository"] = "someone/else"
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "repository mismatch",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)

    def test_missing_asset_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tag, commit = write_bundle(root)
            (root / "snapshot-summary.md").unlink()
            with self.assertRaisesRegex(
                ReleaseVerificationError,
                "missing release asset",
            ):
                verify_release_bundle(root, expected_tag=tag, expected_commit=commit)


if __name__ == "__main__":
    unittest.main()
