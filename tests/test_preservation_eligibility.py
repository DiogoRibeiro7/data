"""Tests for deterministic archival preservation eligibility."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_preservation_eligibility as PRESERVE  # noqa: E402


class PreservationEligibilityTests(unittest.TestCase):
    """Protect the preservation policy and generated eligibility state."""

    def test_committed_report_is_current(self) -> None:
        self.assertEqual(PRESERVE.run(ROOT, write=False), [])

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(
            PRESERVE.expected_outputs(ROOT),
            PRESERVE.expected_outputs(ROOT),
        )

    def test_current_registry_archive_counts(self) -> None:
        """Check report membership and counts against independent disk inventory."""
        report = PRESERVE.build_report(ROOT)
        summary = report["summary"]

        inventories = {
            layer: {
                path.parent.name: yaml.safe_load(path.read_text(encoding="utf-8"))
                for path in (ROOT / directory).glob("*/metadata.yaml")
                if path.is_file()
            }
            for layer, directory in (
                ("canonical", "datasets"), ("external", "external"), ("legacy", "legacy")
            )
        }
        canonical = inventories["canonical"]
        external = inventories["external"]
        legacy = inventories["legacy"]
        eligible = sum(
            item["license"]["redistribution"] == "allowed"
            for item in canonical.values()
        )

        for layer, inventory in inventories.items():
            with self.subTest(layer=layer):
                records = report[layer]
                self.assertEqual(len(records), len(inventory))
                self.assertCountEqual(
                    [item["id"] for item in records],
                    [item["id"] for item in inventory.values()],
                )

        self.assertEqual(summary["canonical_dataset_count"], len(canonical))
        self.assertEqual(summary["canonical_byte_archive_eligible_count"], eligible)
        self.assertEqual(summary["canonical_metadata_only_count"], len(canonical) - eligible)
        self.assertEqual(summary["external_source_count"], len(external))
        self.assertEqual(summary["external_metadata_only_count"], len(external))
        self.assertEqual(summary["legacy_package_count"], len(legacy))
        self.assertEqual(summary["legacy_metadata_only_count"], len(legacy))

    def test_archive_counts_follow_registry_expansion(self) -> None:
        """Exercise changing counts and licence flags on an isolated registry."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for layer in ("datasets", "external", "legacy", "preservation"):
                (root / layer).mkdir()
            (root / PRESERVE.POLICY_PATH).write_text(
                (ROOT / PRESERVE.POLICY_PATH).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            def add_record(layer: str, slug: str, redistribution: str) -> None:
                """Write synthetic metadata without introducing source bytes."""
                path = root / layer / slug / "metadata.yaml"
                path.parent.mkdir()
                path.write_text(
                    yaml.safe_dump({
                        "id": slug,
                        "title": slug,
                        "license": {
                            "name": "Synthetic fixture",
                            "redistribution": redistribution,
                        },
                    }),
                    encoding="utf-8",
                )

            add_record("datasets", "first", "allowed")
            initial = PRESERVE.build_report(root)["summary"]
            self.assertEqual(initial["canonical_dataset_count"], 1)
            self.assertEqual(initial["canonical_byte_archive_eligible_count"], 1)

            add_record("datasets", "second", "allowed")
            add_record("datasets", "third", "restricted")
            add_record("datasets", "fourth", "unknown")
            add_record("external", "external-source", "allowed")
            add_record("legacy", "legacy-package", "allowed")
            expanded = PRESERVE.build_report(root)

            self.assertEqual(expanded["summary"], {
                "canonical_dataset_count": 4,
                "canonical_byte_archive_eligible_count": 2,
                "canonical_metadata_only_count": 2,
                "external_source_count": 1,
                "external_metadata_only_count": 1,
                "legacy_package_count": 1,
                "legacy_metadata_only_count": 1,
            })
            self.assertEqual(
                {item["id"]: item["byte_archive_eligibility"] for item in expanded["canonical"]},
                {
                    "first": "eligible",
                    "second": "eligible",
                    "third": "metadata-only",
                    "fourth": "metadata-only",
                },
            )
            for layer in ("external", "legacy"):
                self.assertEqual(expanded[layer][0]["byte_archive_eligibility"], "metadata-only")

    def test_external_and_legacy_bytes_are_never_default_archive_eligible(self) -> None:
        report = PRESERVE.build_report(ROOT)

        self.assertTrue(
            all(
                item["byte_archive_eligibility"] == "metadata-only"
                for item in report["external"]
            )
        )
        self.assertTrue(
            all(
                item["byte_archive_eligibility"] == "metadata-only"
                for item in report["legacy"]
            )
        )

    def test_canonical_eligibility_follows_redistribution_flag(self) -> None:
        report = PRESERVE.build_report(ROOT)
        by_id = {item["id"]: item for item in report["canonical"]}

        self.assertTrue(
            all(item["redistribution"] == "allowed" for item in by_id.values())
        )
        self.assertTrue(
            all(
                item["byte_archive_eligibility"] == "eligible"
                for item in by_id.values()
            )
        )

    def test_policy_exposes_release_metadata_and_canonical_byte_profiles(self) -> None:
        policy = json.loads(
            (ROOT / "preservation" / "policy-v1.json").read_text(encoding="utf-8")
        )

        profiles = policy["archive_profiles"]
        self.assertFalse(profiles["release-metadata"]["canonical_dataset_bytes"])
        self.assertTrue(
            profiles["eligible-canonical-bytes"]["canonical_dataset_bytes"]
        )

    def test_policy_and_report_versions_match(self) -> None:
        policy = json.loads(
            (ROOT / "preservation" / "policy-v1.json").read_text(encoding="utf-8")
        )
        report = PRESERVE.build_report(ROOT)

        self.assertEqual(policy["schema_version"], 1)
        self.assertEqual(policy["policy_version"], 1)
        self.assertEqual(report["policy"]["schema_version"], 1)
        self.assertEqual(report["policy"]["policy_version"], 1)


if __name__ == "__main__":
    unittest.main()
