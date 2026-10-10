"""Tests for external-source health and drift classification."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_external_sources as HEALTH  # noqa: E402


class ExternalHealthTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "external" / "example").mkdir(parents=True)
        metadata = {
            "schema_version": 1,
            "status": "external-reference",
            "id": "example",
            "title": "Example",
            "publisher": "Example Publisher",
            "source_url": "https://example.test/data",
            "license": {
                "name": "Example licence",
                "url": "https://example.test/license",
            },
            "doi": "10.1000/example",
            "storage": "authoritative-upstream",
        }
        (root / "external" / "example" / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        (root / "external" / "catalog.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "sources": [
                        {
                            "id": "example",
                            "path": "external/example",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return temp, root

    def test_healthy_urls_do_not_create_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        def opener(_request, _timeout):
            return 200

        results = HEALTH.check_external_sources(root, opener=opener)
        payload = HEALTH.report_payload(results)
        self.assertEqual(payload["summary"]["drift"], 0)
        self.assertEqual(payload["summary"]["warning"], 0)
        self.assertEqual(payload["summary"]["healthy"], 3)

    def test_404_is_actionable_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        def opener(request, _timeout):
            return 404 if request.full_url.endswith("/data") else 200

        results = HEALTH.check_external_sources(root, opener=opener)
        source = next(item for item in results if item.check == "source-url")
        self.assertEqual(source.status, "drift")

    def test_429_and_5xx_are_transient_warnings(self) -> None:
        for code in (429, 500, 503):
            with self.subTest(code=code):
                status, _ = HEALTH.classify_http(code)
                self.assertEqual(status, "warning")

    def test_catalog_id_mismatch_is_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        catalog_path = root / "external" / "catalog.json"
        catalog_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "sources": [{"id": "other", "path": "external/other"}],
                }
            ),
            encoding="utf-8",
        )

        results = HEALTH.check_external_sources(
            root,
            opener=lambda _request, _timeout: 200,
        )
        details = [item.detail for item in results if item.status == "drift"]
        self.assertTrue(any("missing from generated catalog" in item for item in details))
        self.assertTrue(any("no matching external metadata" in item for item in details))

    def test_pinned_github_commit_is_checked(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        metadata_path = root / "external" / "example" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["source_url"] = "https://github.com/example/project"
        metadata["source_commit"] = "a" * 40
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 200

        results = HEALTH.check_external_sources(root, opener=opener)
        self.assertTrue(
            any(
                item.check == "pinned-commit"
                and item.target.endswith("/commit/" + "a" * 40)
                for item in results
            )
        )
        self.assertTrue(any("/commit/" + "a" * 40 in url for url in seen))

    def test_non_github_pinned_commit_is_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        metadata_path = root / "external" / "example" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["source_commit"] = "b" * 40
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        results = HEALTH.check_external_sources(
            root,
            opener=lambda _request, _timeout: 200,
        )
        pinned = next(item for item in results if item.check == "pinned-commit")
        self.assertEqual(pinned.status, "drift")

    def test_moved_source_checks_replacement_not_old_url(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        metadata_path = root / "external" / "example" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["availability"] = {
            "state": "moved",
            "last_reviewed": "2026-10-10",
            "replacement_url": "https://example.test/new-data",
            "evidence": ["https://example.test/move-notice"],
        }
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 200

        results = HEALTH.check_external_sources(root, opener=opener)
        self.assertTrue(any(item.status == "moved" for item in results))
        self.assertTrue(any(item.check == "replacement-url" for item in results))
        self.assertNotIn("https://example.test/data", seen)
        self.assertIn("https://example.test/new-data", seen)

    def test_terminal_tombstone_skips_live_endpoint_checks(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        metadata_path = root / "external" / "example" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["availability"] = {
            "state": "permanently-unavailable",
            "last_reviewed": "2026-10-10",
            "evidence": ["https://example.test/withdrawal-notice"],
        }
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 404

        results = HEALTH.check_external_sources(root, opener=opener)
        tombstone = next(
            item for item in results if item.check == "availability-state"
        )
        self.assertEqual(tombstone.status, "tombstone")
        self.assertEqual(seen, [])
        self.assertEqual(HEALTH.report_payload(results)["summary"]["drift"], 0)

    def test_report_rendering_distinguishes_warning_and_drift(self) -> None:
        results = [
            HEALTH.CheckResult("a", "source-url", "x", "healthy", "HTTP 200"),
            HEALTH.CheckResult("b", "source-url", "y", "warning", "transient HTTP 503"),
            HEALTH.CheckResult("c", "source-url", "z", "drift", "HTTP 404"),
        ]
        payload = HEALTH.report_payload(results)
        markdown = HEALTH.render_markdown(payload)
        self.assertIn("Transient warnings: **1**", markdown)
        self.assertIn("Actionable drift: **1**", markdown)


if __name__ == "__main__":
    unittest.main()
