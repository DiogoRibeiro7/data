"""Tests for deterministic provenance/licensing debt reporting."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_provenance_debt as DEBT  # noqa: E402


class ProvenanceDebtTests(unittest.TestCase):
    """Exercise debt discovery, projection, ageing, and freshness."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "external").mkdir()
        (self.root / "legacy").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_external(
        self,
        source_id: str,
        *,
        redistribution: str | None = "unresolved",
        resolution: dict[str, object] | None = None,
    ) -> None:
        """Add one external metadata fixture."""

        directory = self.root / "external" / source_id
        directory.mkdir()
        metadata: dict[str, object] = {
            "schema_version": 1,
            "status": "external-reference",
            "id": source_id,
            "title": source_id,
            "publisher": "Fixture",
            "source_url": "https://example.test/source",
            "storage": "authoritative-upstream",
        }
        if redistribution is not None:
            metadata["redistribution"] = redistribution
        if resolution is not None:
            metadata["resolution"] = resolution
        (directory / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

    def add_legacy(
        self,
        package_id: str,
        *,
        resolution: dict[str, object] | None = None,
    ) -> None:
        """Add one legacy metadata fixture."""

        directory = self.root / "legacy" / package_id
        directory.mkdir()
        metadata: dict[str, object] = {
            "schema_version": 0,
            "status": "legacy-quarantine",
            "id": package_id,
            "title": package_id,
            "source": {"publisher": None, "url": None},
            "license": {"name": "unknown", "redistribution": "unknown"},
            "files": [],
        }
        if resolution is not None:
            metadata["resolution"] = resolution
        (directory / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

    @staticmethod
    def resolution(
        *,
        status: str,
        reviewed: str,
        category: str,
        terminal: bool,
    ) -> dict[str, object]:
        """Build a structured resolution fixture."""

        return {
            "review_status": status,
            "last_reviewed": reviewed,
            "blocker_category": category,
            "blocker_summary": "Fixture blocker.",
            "evidence": ["https://example.test/evidence"],
            "next_action": "Review later.",
            "terminal": terminal,
        }

    def test_unstructured_external_and_legacy_debt_remain_visible(self) -> None:
        self.add_external("external-a")
        self.add_legacy("legacy-a")

        report = DEBT.build_report(self.root)

        self.assertEqual(report["summary"]["total_debt"], 2)
        self.assertEqual(report["summary"]["unstructured_count"], 2)
        self.assertEqual(
            [(item["layer"], item["id"]) for item in report["items"]],
            [("external", "external-a"), ("legacy", "legacy-a")],
        )

    def test_resolved_external_without_resolution_is_not_debt(self) -> None:
        self.add_external("resolved", redistribution="allowed")

        report = DEBT.build_report(self.root)

        self.assertEqual(report["items"], [])

    def test_explicit_resolution_keeps_non_unresolved_external_in_queue(self) -> None:
        self.add_external(
            "snapshot-blocker",
            redistribution="allowed",
            resolution=self.resolution(
                status="actionable",
                reviewed="2026-10-01",
                category="exact-snapshot-identity",
                terminal=False,
            ),
        )

        report = DEBT.build_report(self.root)

        self.assertEqual(report["summary"]["total_debt"], 1)
        self.assertTrue(report["items"][0]["structured_evidence"])

    def test_age_is_relative_to_latest_committed_review_date(self) -> None:
        self.add_external(
            "older",
            resolution=self.resolution(
                status="actionable",
                reviewed="2026-10-01",
                category="redistribution-rights",
                terminal=False,
            ),
        )
        self.add_external(
            "newer",
            resolution=self.resolution(
                status="terminal",
                reviewed="2026-10-05",
                category="dataset-vs-repository-licence-scope",
                terminal=True,
            ),
        )

        report = DEBT.build_report(self.root)
        by_id = {item["id"]: item for item in report["items"]}

        self.assertEqual(report["age_reference_date"], "2026-10-05")
        self.assertEqual(by_id["older"]["age_days"], 4)
        self.assertEqual(by_id["newer"]["age_days"], 0)
        self.assertEqual(report["summary"]["actionable_count"], 1)
        self.assertEqual(report["summary"]["terminal_count"], 1)

    def test_missing_redistribution_defaults_to_unresolved(self) -> None:
        self.add_external("missing", redistribution=None)

        report = DEBT.build_report(self.root)

        self.assertEqual(report["items"][0]["redistribution"], "unresolved")

    def test_markdown_contains_queue_and_age_semantics(self) -> None:
        self.add_external("external-a")

        markdown = DEBT.render_markdown(DEBT.build_report(self.root))

        self.assertIn("Provenance and licensing debt queue", markdown)
        self.assertIn("Unstructured debt: **1**", markdown)
        self.assertIn("Age is deterministic and content-based", markdown)

    def test_write_then_check_is_current(self) -> None:
        self.add_external("external-a")

        self.assertEqual(DEBT.run(self.root, write=True), [])
        self.assertEqual(DEBT.run(self.root, write=False), [])

        payload = json.loads(
            (self.root / "reports" / "provenance-debt.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["summary"]["total_debt"], 1)

    def test_stale_report_is_reported(self) -> None:
        self.add_external("external-a")
        DEBT.run(self.root, write=True)
        (self.root / "reports" / "provenance-debt.md").write_text(
            "stale\n",
            encoding="utf-8",
        )

        errors = DEBT.run(self.root, write=False)

        self.assertTrue(any("provenance debt report is stale" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
