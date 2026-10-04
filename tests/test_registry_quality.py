"""Tests for deterministic registry quality reporting."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import registry_quality as QUALITY  # noqa: E402


class RegistryQualityTests(unittest.TestCase):
    """Exercise report metrics and deterministic rendering."""

    def setUp(self) -> None:
        """Create a minimal temporary registry."""
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        (self.root / "datasets" / "example" / "raw").mkdir(parents=True)
        (self.root / "external" / "source").mkdir(parents=True)
        (self.root / "consumers" / "consumer-one").mkdir(parents=True)
        (self.root / "legacy" / "legacy-one").mkdir(parents=True)
        (self.root / "scripts").mkdir()

        raw = self.root / "datasets" / "example" / "raw" / "data.csv"
        raw.write_text("x\n1\n", encoding="utf-8")

        import hashlib

        checksum = hashlib.sha256(raw.read_bytes()).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": "example",
            "title": "Example",
            "description": "Example dataset",
            "domain": ["example"],
            "source": {
                "publisher": "Example",
                "url": "https://example.com/data",
                "retrieved_at": "2026-10-03",
                "snapshot": "example-v1",
            },
            "license": {
                "name": "CC0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "files": [
                {
                    "path": "raw/data.csv",
                    "role": "raw",
                    "format": "csv",
                    "sha256": checksum,
                }
            ],
            "lineage": [],
        }
        (self.root / "datasets" / "example" / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        external = {
            "schema_version": 1,
            "status": "external-reference",
            "id": "source",
            "title": "Source",
            "publisher": "Publisher",
            "source_url": "https://example.com/source",
            "source_commit": "a" * 40,
            "redistribution": "unresolved",
            "storage": "authoritative-upstream-pinned-snapshot",
            "consumers": ["consumer-repo"],
        }
        (self.root / "external" / "source" / "metadata.yaml").write_text(
            yaml.safe_dump(external, sort_keys=False),
            encoding="utf-8",
        )

        consumer = {
            "schema_version": 1,
            "status": "active",
            "consumer_id": "consumer-one",
            "consumer_repository": "DiogoRibeiro7/consumer-one",
            "dataset_id": "example",
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": "b" * 40,
            "path": "datasets/example/raw/data.csv",
            "sha256": checksum,
            "consumer_commit": "c" * 40,
        }
        (
            self.root
            / "consumers"
            / "consumer-one"
            / "example.yaml"
        ).write_text(
            yaml.safe_dump(consumer, sort_keys=False),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """Remove temporary files."""
        self._temp.cleanup()

    def test_layer_metrics(self) -> None:
        """Canonical, external and legacy metrics preserve semantic distinctions."""
        canonical = QUALITY._canonical_metrics(self.root)
        external = QUALITY._external_metrics(self.root)
        consumers = QUALITY._consumer_metrics(self.root)
        legacy = QUALITY._legacy_metrics(self.root)

        self.assertEqual(canonical["dataset_count"], 1)
        self.assertEqual(canonical["verified_checksum_files"], 1)
        self.assertEqual(canonical["complete_license_datasets"], 1)

        self.assertEqual(external["source_count"], 1)
        self.assertEqual(external["redistribution"]["resolved"], 0)
        self.assertEqual(external["redistribution"]["unresolved"], 1)
        self.assertEqual(external["pinned_immutable_identity_sources"], 1)
        self.assertEqual(external["source_usage"]["consumers"], ["consumer-repo"])

        self.assertEqual(consumers["active_consumer_repository_count"], 1)
        self.assertEqual(consumers["active_relationship_count"], 1)
        self.assertEqual(consumers["deprecated_relationship_count"], 0)
        self.assertEqual(consumers["pinned_contract_count"], 1)
        self.assertEqual(consumers["canonical_datasets_with_consumers"], 1)
        self.assertEqual(consumers["canonical_datasets_without_consumers"], 0)
        self.assertEqual(consumers["canonical_dataset_adoption_coverage"], 1.0)
        self.assertEqual(consumers["active_consumers"], ["consumer-one"])

        self.assertEqual(legacy["package_count"], 1)
        self.assertEqual(legacy["unresolved_package_count"], 1)


    def test_consumer_metrics_distinguish_deprecated_relationships(self) -> None:
        path = self.root / "consumers" / "consumer-one" / "example.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["status"] = "deprecated"
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        consumers = QUALITY._consumer_metrics(self.root)

        self.assertEqual(consumers["active_relationship_count"], 0)
        self.assertEqual(consumers["deprecated_relationship_count"], 1)
        self.assertEqual(consumers["canonical_datasets_with_consumers"], 0)
        self.assertEqual(consumers["canonical_datasets_without_consumers"], 1)
        self.assertEqual(consumers["canonical_dataset_adoption_coverage"], 0.0)


    def test_missing_redistribution_is_unresolved(self) -> None:
        """Missing redistribution metadata is incomplete, not resolved."""
        metadata_path = self.root / "external" / "source" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata.pop("redistribution")
        metadata_path.write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        external = QUALITY._external_metrics(self.root)

        self.assertEqual(external["redistribution"]["resolved"], 0)
        self.assertEqual(external["redistribution"]["unresolved"], 1)

    def test_markdown_does_not_call_unresolved_invalid(self) -> None:
        """Unresolved licensing is represented as an intentional state."""
        report = {
            "canonical": {
                "dataset_count": 1,
                "file_count": 1,
                "verified_checksum_files": 1,
                "complete_license_datasets": 1,
            },
            "external": {
                "source_count": 1,
                "redistribution": {"resolved": 0, "unresolved": 1},
                "pinned_immutable_identity_sources": 1,
                "source_usage": {
                    "consumer_count": 1,
                    "consumer_references": 1,
                    "consumers": ["consumer-repo"],
                },
            },
            "consumers": {
                "active_consumer_repository_count": 1,
                "active_relationship_count": 1,
                "deprecated_relationship_count": 0,
                "pinned_contract_count": 1,
                "pinned_contract_coverage": 1.0,
                "canonical_datasets_with_consumers": 1,
                "canonical_datasets_without_consumers": 0,
                "canonical_dataset_adoption_coverage": 1.0,
                "active_consumers": ["consumer-one"],
                "datasets_with_consumers": ["example"],
                "datasets_without_consumers": [],
            },
            "legacy": {"package_count": 1, "unresolved_package_count": 1},
            "catalogs": {
                "canonical_current": True,
                "external_current": True,
                "consumer_current": True,
            },
            "snapshots": {
                "available_from_repository_state": False,
                "count": None,
                "note": "Not available.",
            },
        }
        markdown = QUALITY.render_markdown(report)
        self.assertIn("unresolved redistribution state is not treated as an invalid record", markdown)
        self.assertIn("Canonical consumer adoption", markdown)
        self.assertIn("Canonical dataset adoption coverage: **100%**", markdown)
        self.assertIn("External source usage annotations", markdown)

    def test_report_generation_is_deterministic(self) -> None:
        """Production report generation is byte-deterministic."""
        root = Path(__file__).resolve().parents[1]
        first = QUALITY.expected_outputs(root)
        second = QUALITY.expected_outputs(root)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
