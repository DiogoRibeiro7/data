"""Tests for consumer contract health and drift classification."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_consumer_contracts as HEALTH  # noqa: E402


class ConsumerHealthTests(unittest.TestCase):
    """Exercise active-consumer reachability and drift classification."""

    def make_root(
        self,
        *,
        status: str = "active",
    ) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        directory = root / "consumers" / "example-consumer"
        directory.mkdir(parents=True)
        metadata = {
            "schema_version": 1,
            "status": status,
            "consumer_id": "example-consumer",
            "consumer_repository": "DiogoRibeiro7/example-consumer",
            "dataset_id": "example-dataset",
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": "a" * 40,
            "path": "datasets/example-dataset/raw/data.csv",
            "sha256": "b" * 64,
            "consumer_commit": "c" * 40,
            "evidence_url": "https://github.com/DiogoRibeiro7/example-consumer/pull/1",
        }
        (directory / "example-dataset.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return temp, root

    def test_healthy_active_contract_has_no_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        results = HEALTH.check_consumer_contracts(
            root,
            opener=lambda _request, _timeout: 200,
        )
        payload = HEALTH.report_payload(results)

        self.assertEqual(payload["summary"]["drift"], 0)
        self.assertEqual(payload["summary"]["warning"], 0)
        self.assertEqual(payload["summary"]["healthy"], 4)

    def test_404_is_actionable_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        def opener(request, _timeout):
            return 404 if "/commit/" in request.full_url else 200

        results = HEALTH.check_consumer_contracts(root, opener=opener)
        commit = next(item for item in results if item.check == "consumer-commit")
        self.assertEqual(commit.status, "drift")

    def test_429_and_5xx_are_transient_warnings(self) -> None:
        for code in (429, 500, 503):
            with self.subTest(code=code):
                status, _ = HEALTH.classify_http(code)
                self.assertEqual(status, "warning")

    def test_deprecated_contracts_are_not_polled(self) -> None:
        temp, root = self.make_root(status="deprecated")
        self.addCleanup(temp.cleanup)

        calls: list[str] = []

        def opener(request, _timeout):
            calls.append(request.full_url)
            return 200

        results = HEALTH.check_consumer_contracts(root, opener=opener)

        self.assertEqual(results, [])
        self.assertEqual(calls, [])

    def test_registry_contract_uses_exact_commit_and_path(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 200

        results = HEALTH.check_consumer_contracts(root, opener=opener)
        target = next(item.target for item in results if item.check == "registry-contract")

        self.assertIn("/blob/" + "a" * 40 + "/", target)
        self.assertTrue(target.endswith("/datasets/example-dataset/raw/data.csv"))
        self.assertIn(target, seen)

    def test_unsupported_evidence_scheme_is_warning_without_opening(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        path = root / "consumers" / "example-consumer" / "example-dataset.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["evidence_url"] = "file:///tmp/local"
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 200

        results = HEALTH.check_consumer_contracts(root, opener=opener)
        evidence = next(item for item in results if item.check == "evidence")

        self.assertEqual(evidence.status, "warning")
        self.assertIn("unsupported URL scheme", evidence.detail)
        self.assertNotIn("file:///tmp/local", seen)

    def test_invalid_url_value_is_warning(self) -> None:
        status, detail = HEALTH.request_url(
            "https://example.test:bad-port/path",
            opener=lambda _request, _timeout: (_ for _ in ()).throw(ValueError("bad port")),
            timeout=1,
        )
        self.assertEqual(status, "warning")
        self.assertIn("network error", detail)

    def test_registry_path_is_percent_encoded_and_repository_is_record_driven(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        path = root / "consumers" / "example-consumer" / "example-dataset.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["registry_repository"] = "example-org/example-registry"
        metadata["path"] = "datasets/example-dataset/raw/a b#c.csv"
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        seen: list[str] = []

        def opener(request, _timeout):
            seen.append(request.full_url)
            return 200

        results = HEALTH.check_consumer_contracts(root, opener=opener)
        target = next(item.target for item in results if item.check == "registry-contract")

        self.assertIn("example-org/example-registry", target)
        self.assertTrue(target.endswith("/datasets/example-dataset/raw/a%20b%23c.csv"))
        self.assertIn(target, seen)


    def test_missing_repository_is_drift(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        path = root / "consumers" / "example-consumer" / "example-dataset.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["consumer_repository"] = ""
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        results = HEALTH.check_consumer_contracts(
            root,
            opener=lambda _request, _timeout: 200,
        )

        self.assertEqual(results[0].status, "drift")
        self.assertEqual(results[0].check, "consumer-repository")

    def test_report_rendering_distinguishes_warning_and_drift(self) -> None:
        results = [
            HEALTH.CheckResult("a", "d", "repo", "x", "healthy", "HTTP 200"),
            HEALTH.CheckResult("b", "d", "repo", "y", "warning", "HTTP 503"),
            HEALTH.CheckResult("c", "d", "repo", "z", "drift", "HTTP 404"),
        ]
        payload = HEALTH.report_payload(results)
        markdown = HEALTH.render_markdown(payload)

        self.assertIn("Transient warnings: **1**", markdown)
        self.assertIn("Actionable drift: **1**", markdown)

    def test_reports_are_written(self) -> None:
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        with tempfile.TemporaryDirectory() as report_dir:
            report_root = Path(report_dir)
            payload = HEALTH.write_reports(
                HEALTH.check_consumer_contracts(
                    root,
                    opener=lambda _request, _timeout: 200,
                ),
                json_path=report_root / "report.json",
                markdown_path=report_root / "report.md",
            )
            written = json.loads(
                (report_root / "report.json").read_text(encoding="utf-8")
            )
            markdown = (report_root / "report.md").read_text(encoding="utf-8")

        self.assertEqual(written["summary"], payload["summary"])
        self.assertIn("Consumer contract health report", markdown)


if __name__ == "__main__":
    unittest.main()
