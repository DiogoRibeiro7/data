"""Tests for offline immutable release verification."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

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
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    summary_text = "# Summary\n"
    (root / "snapshot-manifest.json").write_text(manifest_text, encoding="utf-8")
    (root / "snapshot-summary.md").write_text(summary_text, encoding="utf-8")
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
        "interfaces": {"snapshot_manifest_version": 7},
        "assertions": [{"id": "fixture", "result": "pass"}],
    }
    (root / "snapshot-provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return tag, commit


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
