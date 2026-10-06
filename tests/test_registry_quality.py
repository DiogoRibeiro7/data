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
        (self.root / "reports").mkdir()

        import json
        adoption_policy = {
            "baseline": {
                "snapshot": "snapshot-2026.10.05",
                "dataset_ids": ["example"],
            },
            "exemptions": [],
        }
        (self.root / "reports" / "canonical-adoption-policy.json").write_text(
            json.dumps(adoption_policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        debt_report = {
            "schema_version": 1,
            "age_reference_date": "2026-10-05",
            "summary": {},
            "items": [
                {
                    "id": "external-terminal",
                    "layer": "external",
                    "review_status": "terminal",
                    "blocker_category": "redistribution-rights",
                    "last_reviewed": "2026-10-05",
                    "age_days": 0,
                },
                {
                    "id": "legacy-actionable",
                    "layer": "legacy",
                    "review_status": "actionable",
                    "blocker_category": "exact-snapshot-identity",
                    "last_reviewed": "2026-10-03",
                    "age_days": 2,
                },
            ],
        }
        (self.root / "reports" / "provenance-debt.json").write_text(
            json.dumps(debt_report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

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
        self.assertEqual(
            consumers["active_consumer_repositories"],
            ["DiogoRibeiro7/consumer-one"],
        )

        self.assertEqual(legacy["package_count"], 1)
        self.assertEqual(legacy["unresolved_package_count"], 1)


    def test_provenance_debt_metrics_distinguish_layers_and_status(self) -> None:
        debt = QUALITY._provenance_debt_metrics(self.root)

        self.assertEqual(debt["total_count"], 2)
        self.assertEqual(debt["external"], {"actionable": 0, "terminal": 1})
        self.assertEqual(debt["legacy"], {"actionable": 1, "terminal": 0})
        self.assertEqual(
            debt["by_blocker_category"],
            {"exact-snapshot-identity": 1, "redistribution-rights": 1},
        )
        self.assertEqual(debt["oldest_review_date"], "2026-10-03")
        self.assertEqual(debt["oldest_age_days"], 2)

    def test_provenance_debt_metrics_empty_state(self) -> None:
        path = self.root / "reports" / "provenance-debt.json"
        path.write_text(
            '{"schema_version": 1, "items": []}\n',
            encoding="utf-8",
        )

        debt = QUALITY._provenance_debt_metrics(self.root)

        self.assertEqual(debt["total_count"], 0)
        self.assertEqual(debt["by_blocker_category"], {})
        self.assertIsNone(debt["oldest_review_date"])
        self.assertIsNone(debt["oldest_age_days"])

    def test_canonical_expansion_tracks_added_datasets(self) -> None:
        second = self.root / "datasets" / "second"
        (second / "raw").mkdir(parents=True)
        raw = second / "raw" / "data.csv"
        raw.write_text("x\n2\n", encoding="utf-8")

        import hashlib
        checksum = hashlib.sha256(raw.read_bytes()).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": "second",
            "title": "Second",
            "description": "Second dataset",
            "domain": ["example"],
            "source": {
                "publisher": "Example",
                "url": "https://example.com/second",
                "retrieved_at": "2026-10-06",
                "snapshot": "second-v1",
            },
            "license": {
                "name": "CC0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "files": [{
                "path": "raw/data.csv",
                "role": "raw",
                "format": "csv",
                "sha256": checksum,
            }],
            "lineage": [],
        }
        (second / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        second_consumer = self.root / "consumers" / "consumer-two"
        second_consumer.mkdir()
        relationship = {
            "schema_version": 1,
            "status": "active",
            "consumer_id": "consumer-two",
            "consumer_repository": "DiogoRibeiro7/consumer-two",
            "dataset_id": "second",
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": "d" * 40,
            "path": "datasets/second/raw/data.csv",
            "sha256": checksum,
            "consumer_commit": "e" * 40,
        }
        (second_consumer / "second.yaml").write_text(
            yaml.safe_dump(relationship, sort_keys=False),
            encoding="utf-8",
        )

        expansion = QUALITY._canonical_expansion_metrics(self.root)

        self.assertEqual(expansion["baseline_snapshot"], "snapshot-2026.10.05")
        self.assertEqual(expansion["datasets_added_since_baseline"], ["second"])
        self.assertEqual(expansion["added_datasets_with_consumers"], ["second"])
        self.assertEqual(expansion["uncovered_datasets"], [])

    def test_build_report_rejects_unconsumed_dataset_without_exemption(self) -> None:
        path = self.root / "consumers" / "consumer-one" / "example.yaml"
        path.unlink()

        with self.assertRaisesRegex(ValueError, "without an active consumer"):
            QUALITY.build_report(self.root)

    def test_build_report_allows_documented_adoption_exemption(self) -> None:
        path = self.root / "consumers" / "consumer-one" / "example.yaml"
        path.unlink()
        policy_path = self.root / "reports" / "canonical-adoption-policy.json"
        policy = {
            "baseline": {
                "snapshot": "snapshot-2026.10.05",
                "dataset_ids": ["example"],
            },
            "exemptions": [
                {
                    "dataset_id": "example",
                    "rationale": "Historical reference dataset retained without a live consumer.",
                }
            ],
        }
        import json
        policy_path.write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        report = QUALITY.build_report(self.root)

        self.assertEqual(
            report["canonical_expansion"]["exemptions"],
            {"example": "Historical reference dataset retained without a live consumer."},
        )
        self.assertEqual(report["canonical_expansion"]["uncovered_datasets"], [])

    def test_build_report_rejects_unpinned_active_contract(self) -> None:
        path = self.root / "consumers" / "consumer-one" / "example.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["sha256"] = "0" * 64
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "every active relationship"):
            QUALITY.build_report(self.root)

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


    def test_consumer_repository_count_deduplicates_consumer_ids(self) -> None:
        second_dir = self.root / "consumers" / "consumer-two"
        second_dir.mkdir()
        source = self.root / "consumers" / "consumer-one" / "example.yaml"
        metadata = yaml.safe_load(source.read_text(encoding="utf-8"))
        metadata["consumer_id"] = "consumer-two"
        metadata["consumer_repository"] = "DiogoRibeiro7/consumer-one"
        (second_dir / "example.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        consumers = QUALITY._consumer_metrics(self.root)

        self.assertEqual(consumers["active_relationship_count"], 2)
        self.assertEqual(consumers["active_consumer_repository_count"], 1)
        self.assertEqual(
            consumers["active_consumers"],
            ["consumer-one", "consumer-two"],
        )


    def test_pinned_contract_requires_canonical_path_and_checksum_match(self) -> None:
        path = self.root / "consumers" / "consumer-one" / "example.yaml"
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        metadata["sha256"] = "0" * 64
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")

        consumers = QUALITY._consumer_metrics(self.root)

        self.assertEqual(consumers["active_relationship_count"], 1)
        self.assertEqual(consumers["pinned_contract_count"], 0)
        self.assertEqual(consumers["pinned_contract_coverage"], 0.0)

    def test_missing_consumer_generated_artifact_is_not_current(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            for name in ("datasets", "external", "consumers", "scripts"):
                (temp_root / name).mkdir()

            # Reuse production generator modules through the production scripts directory.
            # The generated consumer files are deliberately absent.
            original_scripts = root / "scripts"
            for script_name in (
                "generate_consumer_catalog.py",
                "generate_external_catalog.py",
                "validate_repository.py",
            ):
                (temp_root / "scripts" / script_name).write_text(
                    (original_scripts / script_name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

            (temp_root / "datasets" / "catalog.json").write_text(
                '{"schema_version": 1, "datasets": []}\n',
                encoding="utf-8",
            )
            (temp_root / "datasets" / "CATALOG.md").write_text(
                "# Canonical dataset catalog\n\nNo canonical datasets are registered yet.\n",
                encoding="utf-8",
            )
            (temp_root / "external" / "catalog.json").write_text(
                '{"schema_version": 1, "sources": []}\n',
                encoding="utf-8",
            )
            (temp_root / "external" / "CATALOG.md").write_text(
                "# External source catalog\n\n"
                "This file is generated from `external/*/metadata.yaml` records.\n"
                "Do not edit it by hand.\n\n"
                "No external sources are registered yet.\n",
                encoding="utf-8",
            )

            status = QUALITY._catalog_status(temp_root)

        self.assertFalse(status["consumer_current"])


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
            "canonical_expansion": {
                "baseline_snapshot": "snapshot-2026.10.05",
                "baseline_dataset_count": 1,
                "current_dataset_count": 1,
                "datasets_added_since_baseline": [],
                "datasets_removed_since_baseline": [],
                "added_datasets_with_consumers": [],
                "added_datasets_exempted": [],
                "exemptions": {},
                "uncovered_datasets": [],
            },
            "legacy": {"package_count": 1, "unresolved_package_count": 1},
            "provenance_debt": {
                "total_count": 2,
                "external": {"actionable": 0, "terminal": 1},
                "legacy": {"actionable": 1, "terminal": 0},
                "by_blocker_category": {"redistribution-rights": 2},
                "oldest_review_date": "2026-10-03",
                "oldest_age_days": 2,
            },
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
        self.assertIn("Pinned contract coverage: **100%**", markdown)
        self.assertIn("External source usage annotations", markdown)

    def test_report_generation_is_deterministic(self) -> None:
        """Production report generation is byte-deterministic."""
        root = Path(__file__).resolve().parents[1]
        first = QUALITY.expected_outputs(root)
        second = QUALITY.expected_outputs(root)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
