"""Tests for deterministic snapshot-to-snapshot diffs."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import diff_snapshots as DIFF  # noqa: E402


def manifest(tag: str, commit: str) -> dict[str, object]:
    """Return one compact v7 manifest fixture."""

    return {
        "manifest_version": 7,
        "repository": "DiogoRibeiro7/data",
        "tag": tag,
        "commit": commit,
        "canonical_datasets": [
            {
                "id": "dataset-a",
                "source": {"snapshot": "v1"},
                "license": {"redistribution": "allowed"},
                "lifecycle": {"status": "active"},
                "files": [
                    {
                        "path": "raw/a.csv",
                        "sha256": "a" * 64,
                    }
                ],
            }
        ],
        "consumer_registry": {
            "relationship_count": 1,
            "active_relationship_count": 1,
            "deprecated_relationship_count": 0,
            "repository_count": 1,
            "relationships": [
                {
                    "consumer_id": "consumer-a",
                    "consumer_repository": "DiogoRibeiro7/consumer-a",
                    "dataset_id": "dataset-a",
                    "status": "active",
                    "registry_commit": "1" * 40,
                    "path": "datasets/dataset-a/raw/a.csv",
                    "sha256": "a" * 64,
                }
            ],
        },
        "canonical_lifecycle": {
            "preferred_replacements": {},
            "datasets": [
                {
                    "id": "dataset-a",
                    "status": "active",
                    "preferred_dataset_id": "dataset-a",
                    "replacement_chain": ["dataset-a"],
                }
            ],
        },
        "provenance_debt": {
            "total_debt": 1,
            "actionable_count": 0,
            "terminal_count": 1,
            "by_blocker_category": {"redistribution-rights": 1},
            "items": [
                {
                    "id": "source-a",
                    "layer": "external",
                    "review_status": "terminal",
                    "terminal": True,
                    "blocker_category": "redistribution-rights",
                    "redistribution": "unresolved",
                }
            ],
        },
        "metadata_schemas": {
            "canonical": {
                "schema_version": 1,
                "sha256": "b" * 64,
            }
        },
        "registry_client": {
            "name": "diogo-data-registry",
            "version": "0.1.0",
            "public_api_version": 1,
        },
        "static_distribution": {
            "distribution_version": 1,
            "artifacts": [
                {
                    "name": "canonical",
                    "path": "canonical.json",
                    "schema_version": 1,
                    "source": "datasets/catalog.json",
                }
            ],
        },
    }


class SnapshotDiffTests(unittest.TestCase):
    """Exercise deterministic semantic snapshot comparisons."""

    def test_identical_snapshots_have_empty_semantic_diff(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = copy.deepcopy(base)

        diff = DIFF.build_diff(base, target)

        self.assertTrue(diff["empty"])
        self.assertEqual(diff["canonical"]["added"], [])
        self.assertEqual(diff["consumers"]["changed"], [])
        self.assertTrue(diff["consumers"]["exact_relationship_diff_available"])
        self.assertTrue(diff["provenance_debt"]["exact_item_diff_available"])

    def test_canonical_add_remove_and_checksum_change_are_classified(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = copy.deepcopy(base)
        target["tag"] = "snapshot-2026.10.10"
        target["commit"] = "b" * 40
        target["canonical_datasets"][0]["files"][0]["sha256"] = "c" * 64
        target["canonical_datasets"].append(
            {
                "id": "dataset-b",
                "source": {"snapshot": "v1"},
                "license": {"redistribution": "allowed"},
                "lifecycle": {"status": "active"},
                "files": [{"path": "raw/b.csv", "sha256": "d" * 64}],
            }
        )

        diff = DIFF.build_diff(base, target)

        self.assertFalse(diff["empty"])
        self.assertEqual(diff["canonical"]["added"], ["dataset-b"])
        changed = diff["canonical"]["changed"][0]
        self.assertEqual(changed["id"], "dataset-a")
        self.assertEqual(changed["file_checksum_changed"], ["raw/a.csv"])

    def test_consumer_and_debt_item_changes_are_exact_in_v7(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = copy.deepcopy(base)
        target["tag"] = "snapshot-2026.10.10"
        target["commit"] = "b" * 40
        target["consumer_registry"]["relationships"][0]["status"] = "deprecated"
        target["consumer_registry"]["active_relationship_count"] = 0
        target["consumer_registry"]["deprecated_relationship_count"] = 1
        target["provenance_debt"]["items"][0]["review_status"] = "actionable"
        target["provenance_debt"]["items"][0]["terminal"] = False
        target["provenance_debt"]["actionable_count"] = 1
        target["provenance_debt"]["terminal_count"] = 0

        diff = DIFF.build_diff(base, target)

        self.assertEqual(
            diff["consumers"]["changed"],
            ["consumer-a|dataset-a|datasets/dataset-a/raw/a.csv"],
        )
        self.assertEqual(
            diff["provenance_debt"]["changed"],
            ["external|source-a"],
        )

    def test_lifecycle_and_preferred_replacement_changes_are_classified(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = copy.deepcopy(base)
        target["tag"] = "snapshot-2026.10.10"
        target["commit"] = "b" * 40
        target["canonical_lifecycle"]["datasets"][0].update(
            {
                "status": "superseded",
                "preferred_dataset_id": "dataset-b",
                "replacement_chain": ["dataset-a", "dataset-b"],
            }
        )
        target["canonical_lifecycle"]["preferred_replacements"] = {
            "dataset-a": "dataset-b"
        }

        diff = DIFF.build_diff(base, target)

        self.assertEqual(diff["lifecycle"]["changed"], ["dataset-a"])
        self.assertTrue(diff["lifecycle"]["preferred_replacements_changed"])

    def test_versions_client_and_distribution_changes_are_classified(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = copy.deepcopy(base)
        target["manifest_version"] = 8
        target["registry_client"]["version"] = "0.2.0"
        target["static_distribution"]["distribution_version"] = 2
        target["metadata_schemas"]["canonical"]["schema_version"] = 2

        diff = DIFF.build_diff(base, target)

        self.assertTrue(diff["manifest_version_changed"])
        self.assertTrue(diff["registry_client"]["changed"])
        self.assertTrue(diff["static_distribution"]["version_changed"])
        self.assertEqual(
            diff["metadata_schemas"]["changed"][0]["after_version"],
            2,
        )

    def test_v6_fallback_does_not_claim_exact_relationship_or_debt_diff(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        base["manifest_version"] = 6
        base["consumer_registry"].pop("relationships")
        base["provenance_debt"].pop("items")
        target = manifest("snapshot-2026.10.10", "b" * 40)

        diff = DIFF.build_diff(base, target)

        self.assertFalse(diff["consumers"]["exact_relationship_diff_available"])
        self.assertFalse(diff["provenance_debt"]["exact_item_diff_available"])

    def test_deterministic_output_bytes(self) -> None:
        base = manifest("snapshot-2026.10.09", "a" * 40)
        target = manifest("snapshot-2026.10.10", "b" * 40)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base_path = root / "base.json"
            target_path = root / "target.json"
            base_path.write_text(json.dumps(base), encoding="utf-8")
            target_path.write_text(json.dumps(target), encoding="utf-8")

            first_json = root / "first.json"
            first_md = root / "first.md"
            second_json = root / "second.json"
            second_md = root / "second.md"

            DIFF.write_outputs(
                base_path,
                target_path,
                json_output=first_json,
                markdown_output=first_md,
            )
            DIFF.write_outputs(
                base_path,
                target_path,
                json_output=second_json,
                markdown_output=second_md,
            )

            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_md.read_bytes(), second_md.read_bytes())


if __name__ == "__main__":
    unittest.main()
