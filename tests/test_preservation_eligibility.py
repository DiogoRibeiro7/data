"""Tests for deterministic archival preservation eligibility."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

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
        report = PRESERVE.build_report(ROOT)
        summary = report["summary"]

        self.assertEqual(summary["canonical_dataset_count"], 4)
        self.assertEqual(summary["canonical_byte_archive_eligible_count"], 4)
        self.assertEqual(summary["canonical_metadata_only_count"], 0)
        self.assertEqual(summary["external_source_count"], 16)
        self.assertEqual(summary["external_metadata_only_count"], 16)
        self.assertEqual(summary["legacy_package_count"], 2)
        self.assertEqual(summary["legacy_metadata_only_count"], 2)

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

    def test_stale_report_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # A missing report is enough to prove freshness enforcement.
            errors = PRESERVE.run(root, write=False)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
