"""Tests for deterministic canonical lifecycle reporting."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_lifecycle_report as LIFECYCLE  # noqa: E402


class LifecycleReportTests(unittest.TestCase):
    """Exercise lifecycle projection, chains, migration state, and freshness."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "datasets").mkdir()
        (self.root / "consumers").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_dataset(
        self,
        dataset_id: str,
        *,
        status: str | None = None,
        superseded_by: str | None = None,
        supersedes: list[str] | None = None,
    ) -> None:
        directory = self.root / "datasets" / dataset_id
        directory.mkdir()
        metadata: dict[str, object] = {
            "schema_version": 1,
            "id": dataset_id,
            "title": dataset_id,
        }
        if status is not None:
            lifecycle: dict[str, object] = {"status": status}
            if superseded_by is not None:
                lifecycle["superseded_by"] = superseded_by
            if supersedes is not None:
                lifecycle["supersedes"] = supersedes
            metadata["lifecycle"] = lifecycle
        (directory / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

    def write_consumers(self, relationships: list[dict[str, object]]) -> None:
        (self.root / "consumers" / "catalog.json").write_text(
            json.dumps(
                {"schema_version": 1, "relationships": relationships},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_missing_lifecycle_defaults_to_active(self) -> None:
        self.add_dataset("dataset")
        self.write_consumers([])
        report = LIFECYCLE.build_report(self.root)
        self.assertEqual(report["summary"]["active_count"], 1)
        self.assertEqual(report["datasets"][0]["status"], "active")
        self.assertEqual(report["datasets"][0]["preferred_dataset_id"], "dataset")

    def test_superseded_chain_resolves_preferred_terminal_dataset(self) -> None:
        self.add_dataset("v1", status="superseded", superseded_by="v2")
        self.add_dataset(
            "v2",
            status="superseded",
            superseded_by="v3",
            supersedes=["v1"],
        )
        self.add_dataset("v3", status="active", supersedes=["v2"])
        self.write_consumers([])
        report = LIFECYCLE.build_report(self.root)
        by_id = {item["id"]: item for item in report["datasets"]}
        self.assertEqual(by_id["v1"]["replacement_chain"], ["v1", "v2", "v3"])
        self.assertEqual(by_id["v1"]["preferred_dataset_id"], "v3")
        self.assertEqual(report["summary"]["replacement_edge_count"], 2)

    def test_active_consumer_on_superseded_dataset_needs_migration(self) -> None:
        self.add_dataset("old", status="superseded", superseded_by="new")
        self.add_dataset("new", status="active", supersedes=["old"])
        self.write_consumers(
            [
                {
                    "consumer_id": "consumer",
                    "consumer_repository": "DiogoRibeiro7/consumer",
                    "dataset_id": "old",
                    "status": "active",
                }
            ]
        )
        report = LIFECYCLE.build_report(self.root)
        self.assertEqual(report["summary"]["migration_needed_count"], 1)
        self.assertEqual(
            report["consumer_migrations"][0],
            {
                "consumer_id": "consumer",
                "consumer_repository": "DiogoRibeiro7/consumer",
                "dataset_id": "old",
                "status": "required",
                "preferred_dataset_id": "new",
                "rationale": None,
            },
        )
        self.assertEqual(report["summary"]["migration_required_count"], 1)
        self.assertEqual(report["summary"]["migration_resolution_coverage"], 0.0)

    def test_planned_migration_is_resolved_but_still_needed(self) -> None:
        self.add_dataset("old", status="superseded", superseded_by="new")
        self.add_dataset("new", status="active", supersedes=["old"])
        self.write_consumers(
            [
                {
                    "consumer_id": "consumer",
                    "consumer_repository": "DiogoRibeiro7/consumer",
                    "dataset_id": "old",
                    "status": "active",
                    "migration": {
                        "status": "planned",
                        "target_dataset_id": "new",
                    },
                }
            ]
        )

        report = LIFECYCLE.build_report(self.root)

        self.assertEqual(report["consumer_migrations"][0]["status"], "planned")
        self.assertEqual(report["summary"]["migration_planned_count"], 1)
        self.assertEqual(report["summary"]["migration_needed_count"], 1)
        self.assertEqual(report["summary"]["migration_resolution_coverage"], 1.0)

    def test_retained_migration_records_rationale(self) -> None:
        self.add_dataset("old", status="superseded", superseded_by="new")
        self.add_dataset("new", status="active", supersedes=["old"])
        self.write_consumers(
            [
                {
                    "consumer_id": "consumer",
                    "consumer_repository": "DiogoRibeiro7/consumer",
                    "dataset_id": "old",
                    "status": "active",
                    "migration": {
                        "status": "retained",
                        "rationale": "Pinned for historical reproducibility.",
                    },
                }
            ]
        )

        report = LIFECYCLE.build_report(self.root)

        migration = report["consumer_migrations"][0]
        self.assertEqual(migration["status"], "retained")
        self.assertEqual(
            migration["rationale"],
            "Pinned for historical reproducibility.",
        )
        self.assertEqual(report["summary"]["migration_retained_count"], 1)
        self.assertEqual(report["summary"]["migration_needed_count"], 0)

    def test_migrated_historical_relationship_is_reported(self) -> None:
        self.add_dataset("old", status="superseded", superseded_by="new")
        self.add_dataset("new", status="active", supersedes=["old"])
        self.write_consumers(
            [
                {
                    "consumer_id": "consumer",
                    "consumer_repository": "DiogoRibeiro7/consumer",
                    "dataset_id": "old",
                    "status": "deprecated",
                    "migration": {
                        "status": "migrated",
                        "target_dataset_id": "new",
                    },
                },
                {
                    "consumer_id": "consumer",
                    "consumer_repository": "DiogoRibeiro7/consumer",
                    "dataset_id": "new",
                    "status": "active",
                },
            ]
        )

        report = LIFECYCLE.build_report(self.root)

        statuses = [item["status"] for item in report["consumer_migrations"]]
        self.assertEqual(statuses, ["migrated", "current"])
        self.assertEqual(report["summary"]["migrated_relationship_count"], 1)

    def test_markdown_renders_replacement_chain(self) -> None:
        self.add_dataset("old", status="superseded", superseded_by="new")
        self.add_dataset("new", status="active", supersedes=["old"])
        self.write_consumers([])
        markdown = LIFECYCLE.render_markdown(LIFECYCLE.build_report(self.root))
        self.assertIn("`old` -> `new`", markdown)
        self.assertIn("Superseded: **1**", markdown)

    def test_write_then_check_is_current(self) -> None:
        self.add_dataset("dataset")
        self.write_consumers([])
        self.assertEqual(LIFECYCLE.run(self.root, write=True), [])
        self.assertEqual(LIFECYCLE.run(self.root, write=False), [])

    def test_stale_report_is_reported(self) -> None:
        self.add_dataset("dataset")
        self.write_consumers([])
        LIFECYCLE.run(self.root, write=True)
        (self.root / "reports" / "lifecycle.md").write_text(
            "stale\n",
            encoding="utf-8",
        )
        errors = LIFECYCLE.run(self.root, write=False)
        self.assertTrue(any("lifecycle report is stale" in item for item in errors))

    def test_production_report_generation_is_deterministic(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            LIFECYCLE.expected_outputs(root),
            LIFECYCLE.expected_outputs(root),
        )


if __name__ == "__main__":
    unittest.main()
