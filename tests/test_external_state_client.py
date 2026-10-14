"""Tests for external resolution and availability state in the public client."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from data_registry import RegistryClient
from data_registry.core import RegistryEntry, entry_summary
from data_registry.models import ExternalRecord

ROOT = Path(__file__).resolve().parents[1]


class ExternalStateClientTests(unittest.TestCase):
    def test_terminal_external_record_exposes_resolution_state(self) -> None:
        client = RegistryClient(ROOT)
        record = client.external("medium-crawlfeeds-corpus")

        self.assertIsInstance(record, ExternalRecord)
        self.assertEqual(record.resolution_status, "terminal")
        self.assertTrue(record.terminal)
        self.assertEqual(record.blocker_category, "redistribution-rights")
        self.assertIsNone(record.availability_state)
        self.assertIsNone(record.replacement_url)

    def test_moved_external_record_exposes_availability_state(self) -> None:
        raw = {
            "schema_version": 1,
            "status": "external-reference",
            "id": "moved-source",
            "title": "Moved source",
            "publisher": "Example",
            "source_url": "https://example.test/old",
            "storage": "authoritative-upstream",
            "availability": {
                "state": "moved",
                "last_reviewed": "2026-10-11",
                "replacement_url": "https://example.test/new",
                "evidence": ["https://example.test/move-notice"],
            },
        }

        record = ExternalRecord.from_mapping(raw)

        self.assertEqual(record.availability_state, "moved")
        self.assertEqual(record.replacement_url, "https://example.test/new")
        self.assertIsNone(record.resolution_status)
        self.assertIsNone(record.terminal)

    def test_external_records_filter_terminal_status(self) -> None:
        client = RegistryClient(ROOT)

        records = client.external_records(resolution_status="terminal")

        self.assertTrue(records)
        self.assertTrue(all(item.resolution_status == "terminal" for item in records))
        self.assertEqual(
            [item.id for item in records],
            sorted(item.id for item in records),
        )

    def test_external_records_filter_availability_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "external" / "moved-source"
            source.mkdir(parents=True)
            metadata = {
                "schema_version": 1,
                "status": "external-reference",
                "id": "moved-source",
                "title": "Moved source",
                "publisher": "Example",
                "source_url": "https://example.test/old",
                "storage": "authoritative-upstream",
                "availability": {
                    "state": "moved",
                    "last_reviewed": "2026-10-14",
                    "replacement_url": "https://example.test/new",
                    "evidence": ["https://example.test/move-notice"],
                },
            }
            (source / "metadata.yaml").write_text(
                yaml.safe_dump(metadata, sort_keys=False),
                encoding="utf-8",
            )

            records = RegistryClient(root).external_records(
                availability_state="moved"
            )

        self.assertEqual([item.id for item in records], ["moved-source"])

    def test_external_records_reject_invalid_filters(self) -> None:
        client = RegistryClient(ROOT)

        with self.assertRaisesRegex(
            Exception,
            "unknown external resolution status",
        ):
            client.external_records(resolution_status="maybe")

        with self.assertRaisesRegex(
            Exception,
            "unknown external availability state",
        ):
            client.external_records(availability_state="missing")


    def test_cli_summary_exposes_external_state(self) -> None:
        entry = RegistryEntry(
            layer="external",
            id="terminal-source",
            title="Terminal source",
            path="external/terminal-source",
            metadata={
                "schema_version": 1,
                "status": "external-reference",
                "id": "terminal-source",
                "title": "Terminal source",
                "publisher": "Example",
                "source_url": "https://example.test/source",
                "storage": "authoritative-upstream",
                "resolution": {
                    "review_status": "terminal",
                    "terminal": True,
                    "blocker_category": "redistribution-rights",
                },
                "availability": {
                    "state": "legal-withdrawal",
                    "replacement_url": None,
                },
            },
        )

        summary = entry_summary(entry)

        self.assertEqual(summary["resolution_status"], "terminal")
        self.assertTrue(summary["terminal"])
        self.assertEqual(
            summary["blocker_category"],
            "redistribution-rights",
        )
        self.assertEqual(summary["availability_state"], "legal-withdrawal")
        self.assertIsNone(summary["replacement_url"])


if __name__ == "__main__":
    unittest.main()
