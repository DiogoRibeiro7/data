"""Tests for external-state filtering in the registry CLI."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import yaml

from data_registry.cli import main

ROOT = Path(__file__).resolve().parents[1]


class ExternalStateCliTests(unittest.TestCase):
    def test_list_filters_terminal_external_records_as_json(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            code = main(
                [
                    "--root",
                    str(ROOT),
                    "list",
                    "--layer",
                    "external",
                    "--resolution-status",
                    "terminal",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(payload)
        self.assertTrue(
            all(item["resolution_status"] == "terminal" for item in payload)
        )
        self.assertEqual(
            [item["id"] for item in payload],
            sorted(item["id"] for item in payload),
        )

    def test_search_combines_text_and_resolution_filter(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            code = main(
                [
                    "--root",
                    str(ROOT),
                    "search",
                    "medium",
                    "--layer",
                    "external",
                    "--resolution-status",
                    "terminal",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(payload)
        self.assertTrue(all("medium" in item["id"] for item in payload))
        self.assertTrue(
            all(item["resolution_status"] == "terminal" for item in payload)
        )

    def test_availability_filter_works_in_human_output(self) -> None:
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
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(
                    [
                        "--root",
                        str(root),
                        "list",
                        "--layer",
                        "external",
                        "--availability-state",
                        "moved",
                    ]
                )

        self.assertEqual(code, 0)
        self.assertIn("moved-source", output.getvalue())

    def test_external_filters_require_external_layer(self) -> None:
        output = io.StringIO()
        error = io.StringIO()

        with redirect_stdout(output), redirect_stderr(error):
            code = main(
                [
                    "--root",
                    str(ROOT),
                    "list",
                    "--layer",
                    "canonical",
                    "--resolution-status",
                    "terminal",
                ]
            )

        self.assertEqual(code, 1)
        self.assertIn(
            "external-state filters require --layer external",
            error.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
